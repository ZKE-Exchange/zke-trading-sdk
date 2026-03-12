#!/bin/bash

# 开启严格模式：任何错误立即停止，确保过程可控
set -euo pipefail

# 终端颜色配置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}    ZKE OpenClaw Plugin Manager       ${NC}"
echo -e "${GREEN}======================================${NC}"

# ======================================
# 核心配置 (保持不变)
# ======================================
INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_BRANCH="main"
PLUGIN_ID="zke-trading"

SPOT_URL="https://openapi.zke.com"
FUTURES_URL="https://futuresopenapi.zke.com"
WS_URL="wss://ws.zke.com/kline-api/ws"
RECV_WINDOW="5000"

# ======================================
# 交互工具函数
# ======================================
prompt_tty() {
    local prompt="$1"; local __resultvar="$2"; local value
    printf "%s" "$prompt" > /dev/tty
    IFS= read -r value < /tty
    printf -v "$__resultvar" '%s' "$value"
}

prompt_tty_secret() {
    local prompt="$1"; local __resultvar="$2"; local value
    printf "%s" "$prompt" > /dev/tty
    stty -echo < /dev/tty
    IFS= read -r value < /dev/tty
    stty echo < /dev/tty
    printf "\n" > /dev/tty
    printf -v "$__resultvar" '%s' "$value"
}

# ======================================
# [重点完善] 强力卸载与清理逻辑
# ======================================
do_uninstall() {
    echo -e "${YELLOW}[!] 正在深度清理 $PLUGIN_ID 的所有痕迹...${NC}"
    
    # 1. 尝试通过 CLI 正常卸载
    openclaw plugins disable "$PLUGIN_ID" >/dev/null 2>&1 || true
    openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
    
    # 2. 物理删除残留目录 (解决你刚才遇到的报错)
    # OpenClaw 存储插件实体的目录
    rm -rf "$HOME/.openclaw/extensions/$PLUGIN_ID"
    # OpenClaw 存储软链接的目录
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"
    # 针对旧版本的兼容性清理
    rm -rf "$HOME/.openclaw/data/plugins/$PLUGIN_ID" 
    
    echo "  ✓ 插件文件已彻底移除"
}

# ======================================
# 参数解析
# ======================================
MODE="install"
if [[ $# -gt 0 ]]; then
    case "$1" in
        --uninstall) do_uninstall; exit 0 ;;
        --reinstall) MODE="reinstall"; do_uninstall ;;
        --reset)     
            MODE="reset"
            do_uninstall
            echo -e "${RED}[!] 正在删除 SDK 源码及 Python 环境...${NC}"
            rm -rf "$INSTALL_DIR"
            ;;
        *)
            echo "用法: $0 [--reinstall | --uninstall | --reset]"
            exit 1
            ;;
    esac
fi

# ======================================
# 1-2. 环境检查
# ======================================
echo -e "\n${GREEN}[1/9] 检查系统依赖...${NC}"
for cmd in git npm openclaw; do
    command -v "$cmd" >/dev/null 2>&1 || { echo -e "${RED}错误: 缺少 $cmd${NC}"; exit 1; }
    echo "  ✓ $cmd 已就绪"
done

echo -e "\n${GREEN}[2/9] 检测 Python 环境 (>= 3.10)...${NC}"
find_python() {
    for PY in python3 python3.13 python3.12 python3.11; do
        if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
            echo "$PY"; return 0
        fi
    done
    return 1
}
PYTHON_BIN=$(find_python) || { echo -e "${RED}错误: 未找到合格的 Python${NC}"; exit 1; }

# ======================================
# 3. 源码同步
# ======================================
echo -e "\n${GREEN}[3/9] 正在同步 SDK 源码...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "  检测到现有版本，正在执行强制更新..."
    cd "$INSTALL_DIR"
    git fetch --all
    git reset --hard "origin/$DEFAULT_BRANCH"
else
    echo "  正在 Clone 远程仓库..."
    git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ======================================
# 4-5. Python 虚拟环境与依赖
# ======================================
echo -e "\n${GREEN}[4/9] 配置 Python 虚拟环境...${NC}"
[ -d ".venv" ] && rm -rf .venv
"$PYTHON_BIN" -m venv .venv
echo -e "\n${GREEN}[5/9] 安装 Python 依赖库...${NC}"
./.venv/bin/pip install --upgrade pip > /dev/null
./.venv/bin/pip install -r requirements.txt
echo "  ✓ 依赖安装完成"

# ======================================
# 6. API 密钥配置
# ======================================
echo -e "\n${GREEN}[6/9] API 密钥配置...${NC}"
if [ ! -f "config.json" ] || [ "$MODE" == "reset" ]; then
    prompt_tty "  > ZKE Spot API Key: " SPOT_KEY
    prompt_tty_secret "  > ZKE Spot API Secret: " SPOT_SEC
    prompt_tty "  > ZKE Futures API Key (Enter 复用 Spot): " FUT_KEY
    [ -z "$FUT_KEY" ] && { FUT_KEY=$SPOT_KEY; FUT_SEC=$SPOT_SEC; } || prompt_tty_secret "  > Futures API Secret: " FUT_SEC
    
    # 嵌入 Python 生成精简配置
    ./.venv/bin/python - "$SPOT_URL" "$FUTURES_URL" "$WS_URL" "$RECV_WINDOW" "$SPOT_KEY" "$SPOT_SEC" "$FUT_KEY" "$FUT_SEC" << 'PY'
import json, sys
a = sys.argv[1:]
c = {
    "spot": {"base_url": a[0], "api_key": a[4], "api_secret": a[5], "recv_window": int(a[3])},
    "futures": {"base_url": a[1], "api_key": a[6], "api_secret": a[7], "recv_window": int(a[3])},
    "ws": {"url": a[2]}
}
with open("config.json", "w") as f: json.dump(c, f, indent=2)
PY
    echo "  ✓ config.json 已就绪"
fi

# ======================================
# 7. 编译 OpenClaw 插件 (拆除限制后的源码编译)
# ======================================
echo -e "\n${GREEN}[7/9] 正在编译 OpenClaw 插件...${NC}"
cd openclaw-plugin
rm -rf dist node_modules
npm install
npm run build
echo "  ✓ 插件编译完成"

# ======================================
# 8-9. 系统集成
# ======================================
echo -e "\n${GREEN}[8/9] 注册并激活插件...${NC}"
# 获取当前绝对路径，确保注册不会失败
CURRENT_PLUGIN_PATH=$(pwd)
openclaw plugins install "$CURRENT_PLUGIN_PATH"
openclaw plugins enable "$PLUGIN_ID"

echo -e "\n${GREEN}[9/9] 更新 OpenClaw 安全白名单...${NC}"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
./.venv/bin/python - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
p, pid = sys.argv[1], sys.argv[2]
d = json.loads(open(p).read()) if os.path.exists(p) else {}
a = d.setdefault("plugins", {}).setdefault("allow", [])
if pid not in a: a.append(pid)
with open(p, "w") as f: json.dump(d, f, indent=2)
PY

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}    ZKE PLUGIN ${MODE^^} SUCCESS       ${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e "${YELLOW}👉 最后一步: 请执行以下命令重启网关：${NC}"
echo -e "${YELLOW}   openclaw gateway --force          ${NC}"
echo -e "${GREEN}======================================${NC}"

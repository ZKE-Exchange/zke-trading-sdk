#!/bin/bash

# 开启严格模式：任何一步失败都会停止脚本，防止弄坏系统
set -euo pipefail

# 颜色定义 (增强交互感)
GREEN='\033[0.32m'
YELLOW='\033[1.33m'
RED='\033[0.31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}    ZKE OpenClaw Plugin Manager       ${NC}"
echo -e "${GREEN}======================================${NC}"

# ======================================
# 核心配置 (与原版完全一致)
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
# 交互函数 (保留原版 prompt_tty 逻辑)
# ======================================
prompt_tty() {
    local prompt="$1"
    local __resultvar="$2"
    local value
    printf "%s" "$prompt" > /dev/tty
    IFS= read -r value < /dev/tty
    printf -v "$__resultvar" '%s' "$value"
}

prompt_tty_secret() {
    local prompt="$1"
    local __resultvar="$2"
    local value
    printf "%s" "$prompt" > /dev/tty
    stty -echo < /dev/tty
    IFS= read -r value < /dev/tty
    stty echo < /dev/tty
    printf "\n" > /dev/tty
    printf -v "$__resultvar" '%s' "$value"
}

# ======================================
# 模式解析
# ======================================
MODE="install"
if [[ $# -gt 0 ]]; then
    case "$1" in
        --uninstall)
            echo -e "${YELLOW}[!] 正在执行卸载流程...${NC}"
            openclaw plugins disable "$PLUGIN_ID" >/dev/null 2>&1 || true
            openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
            rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"
            echo "✓ 卸载完成。"
            exit 0
            ;;
        --reinstall)
            MODE="reinstall"
            echo -e "${YELLOW}[!] 正在清理旧版插件以便重装...${NC}"
            openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
            ;;
        --reset)
            MODE="reset"
            echo -e "${RED}[!] 正在彻底重置：删除 SDK 和所有配置...${NC}"
            openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
            rm -rf "$INSTALL_DIR"
            ;;
        *)
            echo "未知参数: $1"
            echo "可用参数: --uninstall, --reinstall, --reset"
            exit 1
            ;;
    esac
fi

# ======================================
# 1. 依赖检查 (逐项检查)
# ======================================
echo -e "\n${GREEN}[1/9] 正在检查系统依赖...${NC}"
for cmd in git npm openclaw; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo -e "${RED}错误: 你的系统尚未安装 $cmd。${NC}"
        exit 1
    fi
    echo -e "  ✓ $cmd 已就绪"
done

# ======================================
# 2. Python 环境检测
# ======================================
echo -e "\n${GREEN}[2/9] 正在检测 Python 环境 (要求 3.10+)...${NC}"
PYTHON_BIN=""
for PY in python3 python3.13 python3.12 python3.11 python3.10; do
    if command -v "$PY" >/dev/null 2>&1; then
        if "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
            PYTHON_BIN="$PY"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}错误: 未找到符合条件的 Python 版本 (需 3.10 以上)。${NC}"
    exit 1
fi
echo -e "  ✓ 使用 Python: $PYTHON_BIN"

# ======================================
# 3. 源码同步
# ======================================
echo -e "\n${GREEN}[3/9] 正在下载或同步 SDK 源码...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "  发现现有目录，正在执行 git reset 强制同步..."
    cd "$INSTALL_DIR"
    git fetch --all
    git reset --hard "origin/$DEFAULT_BRANCH"
else
    echo "  正在 Clone 仓库到 $INSTALL_DIR..."
    git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ======================================
# 4. 虚拟环境构建
# ======================================
echo -e "\n${GREEN}[4/9] 正在构建 Python 虚拟环境...${NC}"
[ -d ".venv" ] && rm -rf .venv
"$PYTHON_BIN" -m venv .venv
echo "  ✓ .venv 构建完成"

# ======================================
# 5. 安装 Python 依赖
# ======================================
echo -e "\n${GREEN}[5/9] 正在安装 Python 依赖包...${NC}"
source .venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo "  ✓ 依赖安装完成"

# ======================================
# 6. API 密钥配置 (保留原版交互逻辑)
# ======================================
echo -e "\n${GREEN}[6/9] 正在配置交易所 API 密钥...${NC}"
if [ ! -f "config.json" ] || [ "$MODE" == "reset" ]; then
    prompt_tty "  > 输入 ZKE Spot API Key: " SPOT_KEY
    prompt_tty_secret "  > 输入 ZKE Spot API Secret: " SPOT_SEC
    
    prompt_tty "  > 输入 Futures API Key (留空则复用 Spot): " FUT_KEY
    if [ -z "$FUT_KEY" ]; then
        FUT_KEY="$SPOT_KEY"; FUT_SEC="$SPOT_SEC"
        echo "  ℹ 已选择复用 Spot 密钥"
    else
        prompt_tty_secret "  > 输入 Futures API Secret: " FUT_SEC
    fi

    # 嵌入 Python 生成 config.json (结构与原版 100% 一致)
    python3 - "$SPOT_URL" "$FUTURES_URL" "$WS_URL" "$RECV_WINDOW" "$SPOT_KEY" "$SPOT_SEC" "$FUT_KEY" "$FUT_SEC" << 'PY'
import json, sys, os
args = sys.argv[1:]
config = {
    "spot": {"base_url": args[0], "api_key": args[4], "api_secret": args[5], "recv_window": int(args[3])},
    "futures": {"base_url": args[1], "api_key": args[6], "api_secret": args[7], "recv_window": int(args[3])},
    "ws": {"url": args[2]}
}
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)
PY
    echo "  ✓ config.json 已生成"
else
    echo "  ℹ 发现现有配置，已跳过输入。"
fi

# ======================================
# 7. 编译 OpenClaw 插件 (这是解开限制的关键)
# ======================================
echo -e "\n${GREEN}[7/9] 正在编译 OpenClaw 插件源码...${NC}"
cd openclaw-plugin
rm -rf dist node_modules
npm install
npm run build
echo "  ✓ 插件编译完成"

# ======================================
# 8. 注册插件到系统
# ======================================
echo -e "\n${GREEN}[8/9] 正在将插件注册到 OpenClaw...${NC}"
openclaw plugins install "$(pwd)"
openclaw plugins enable "$PLUGIN_ID"
echo "  ✓ 插件已启用"

# ======================================
# 9. 授权白名单
# ======================================
echo -e "\n${GREEN}[9/9] 正在更新系统允许列表 (Allowlist)...${NC}"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
mkdir -p "$HOME/.openclaw"
python3 - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
p, pid = sys.argv[1], sys.argv[2]
if os.path.exists(p):
    with open(p, "r") as f: data = json.load(f)
else:
    data = {}
allow = data.setdefault("plugins", {}).setdefault("allow", [])
if pid not in allow: allow.append(pid)
with open(p, "w") as f: json.dump(data, f, indent=2)
PY

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}    🎊 ZKE 插件操作成功！              ${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e "${YELLOW}👉 请务必执行以下命令以完成最后生效：${NC}"
echo -e "${YELLOW}   openclaw gateway --force          ${NC}"
echo -e "${GREEN}======================================${NC}"

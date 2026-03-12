#!/bin/bash

set -euo pipefail

# --- 配置信息 ---
INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_BRANCH="main"
PLUGIN_ID="zke-trading"
OPENCLAW_EXT_DIR="$HOME/.openclaw/extensions/$PLUGIN_ID"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ======================================
# 强力卸载函数
# ======================================
do_uninstall() {
    echo -e "${YELLOW}[!] 正在深度清理插件残留...${NC}"
    openclaw plugins disable "$PLUGIN_ID" >/dev/null 2>&1 || true
    openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
    # 物理删除，解决 "delete it first" 报错
    rm -rf "$OPENCLAW_EXT_DIR"
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"
    echo "✓ 卸载/清理完成。"
}

# ======================================
# 交互检测逻辑 (核心改进)
# ======================================
MODE="install"

# 检查是否已存在安装
if [ -d "$OPENCLAW_EXT_DIR" ] || [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}检测到 ZKE Trading 插件已安装。${NC}"
    echo "请选择操作:"
    echo "1) 重新安装 (保留 API 配置，更新代码)"
    echo "2) 彻底重置 (删除所有文件和配置，重新开始)"
    echo "3) 卸载插件"
    echo "4) 退出安装"
    
    printf "请输入选项 [1-4]: " > /dev/tty
    read -r choice < /dev/tty

    case "$choice" in
        1)
            MODE="reinstall"
            do_uninstall
            ;;
        2)
            MODE="reset"
            do_uninstall
            echo -e "${RED}[!] 正在删除 SDK 源码目录...${NC}"
            rm -rf "$INSTALL_DIR"
            ;;
        3)
            do_uninstall
            echo "已成功卸载，脚本退出。"
            exit 0
            ;;
        *)
            echo "操作取消。"
            exit 0
            ;;
    esac
fi

echo -e "\n${GREEN}开始执行 ${MODE^^} 流程...${NC}"

# ======================================
# 1. 依赖检查
# ======================================
echo -e "\n${GREEN}[1/9] 检查依赖...${NC}"
for cmd in git npm openclaw python3; do
    command -v "$cmd" >/dev/null 2>&1 || { echo -e "${RED}错误: 缺少 $cmd${NC}"; exit 1; }
    echo "  ✓ $cmd 已就绪"
done

# ======================================
# 2. 源码同步
# ======================================
echo -e "\n${GREEN}[2/9] 同步 SDK 源码...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR"
    git fetch --all
    git reset --hard "origin/$DEFAULT_BRANCH"
else
    git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ======================================
# 3. 虚拟环境与依赖
# ======================================
echo -e "\n${GREEN}[3/9] 配置 Python 虚拟环境...${NC}"
[ -d ".venv" ] || python3 -m venv .venv
./.venv/bin/pip install --upgrade pip > /dev/null
./.venv/bin/pip install -r requirements.txt

# ======================================
# 4. API 配置 (仅在全新或重置模式下询问)
# ======================================
echo -e "\n${GREEN}[4/9] 检查 API 配置...${NC}"
if [ ! -f "config.json" ] || [ "$MODE" == "reset" ]; then
    # 这里是你原有的 prompt_tty 逻辑，为了简洁在此简述
    # 询问 API KEY / SECRET 并生成 config.json
    echo "请按照提示输入 API 密钥..."
    # [此处插入你原有的生成 config.json 的 Python 代码块]
    echo "  ✓ config.json 已创建"
else
    echo "  ✓ 发现现有 API 配置，已跳过。"
fi

# ======================================
# 5. 编译插件 (关键：物理拆除限制后的源码编译)
# ======================================
echo -e "\n${GREEN}[5/9] 编译 OpenClaw 插件...${NC}"
cd openclaw-plugin
rm -rf dist node_modules
npm install
npm run build
echo "  ✓ 插件编译完成"

# ======================================
# 6. 注册与授权
# ======================================
echo -e "\n${GREEN}[6/9] 注册并激活插件...${NC}"
openclaw plugins install "$(pwd)"
openclaw plugins enable "$PLUGIN_ID"

# 更新 openclaw.json allowlist
echo -e "\n${GREEN}[7/9] 更新白名单...${NC}"
# [此处插入你原有的更新 openclaw.json 的逻辑]

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}    ZKE 插件 ${MODE} 成功完成!        ${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e "${YELLOW}👉 重要: 请执行 'openclaw gateway --force' 以生效${NC}"

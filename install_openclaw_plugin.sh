#!/bin/bash

set -euo pipefail

echo "======================================"
echo "Installing ZKE OpenClaw Plugin"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_BRANCH="main"
PLUGIN_ID="zke-trading"

SPOT_URL="https://openapi.zke.com"
FUTURES_URL="https://futuresopenapi.zke.com"
WS_URL="wss://ws.zke.com/kline-api/ws"
RECV_WINDOW="5000"

OPENCLAW_EXT_DIR="$HOME/.openclaw/extensions/$PLUGIN_ID"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

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

# --- 核心抗体 1：安全清理逻辑，防止 OpenClaw 死锁 ---
cleanup_existing_plugin() {
    echo "Cleaning up existing plugin installation..."
    openclaw plugins disable "$PLUGIN_ID" >/dev/null 2>&1 || true
    openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
    
    rm -rf "$OPENCLAW_EXT_DIR"
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"

    if [ -f "$OPENCLAW_CONFIG" ]; then
        python3 - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
cfg_path = sys.argv[1]
pid = sys.argv[2]
try:
    with open(cfg_path, 'r') as f:
        data = json.load(f)
    modified = False
    if "plugins" in data:
        entries = data.get("plugins", {}).get("entries", {})
        if pid in entries:
            del entries[pid]
            modified = True
        allow = data.get("plugins", {}).get("allow", [])
        if pid in allow:
            data["plugins"]["allow"] = [p for p in allow if p != pid]
            modified = True
    if modified:
        with open(cfg_path, 'w') as f:
            json.dump(data, f, indent=2)
except Exception: pass
PY
    fi
}

# --- 菜单交互流程 ---
IS_SDK_INSTALLED=false
IS_PLUGIN_REGISTERED=false

if [ -d "$INSTALL_DIR" ]; then IS_SDK_INSTALLED=true; fi
if [ -d "$OPENCLAW_EXT_DIR" ]; then IS_PLUGIN_REGISTERED=true; fi

if $IS_SDK_INSTALLED || $IS_PLUGIN_REGISTERED; then
    echo ""
    echo "Existing ZKE Trading installation detected."
    echo ""
    echo "Please select an action:"
    echo "  1) Update / Reinstall (Keep API config, update code)"
    echo "  2) Full Reset (Delete all files and configs, start fresh)"
    echo "  3) Uninstall Plugin Only"
    echo "  4) Cancel"
    echo ""

    prompt_tty "Enter choice [1-4]: " MENU_CHOICE

    case "$MENU_CHOICE" in
        1)
            echo "Starting update process..."
            cleanup_existing_plugin
            ;; # 注意这里不写 exit，让它自然向下执行安装步骤
        2)
            echo "Starting full reset..."
            cleanup_existing_plugin
            echo "Removing SDK directory: $INSTALL_DIR"
            rm -rf "$INSTALL_DIR"
            ;;
        3)
            cleanup_existing_plugin
            echo "Uninstallation complete. Exiting."
            exit 0
            ;;
        4|*)
            echo "Operation cancelled."
            exit 0
            ;;
    esac
fi

# ==========================================
# 标准安装流程开始 (1/9 到 9/9)
# ==========================================

echo ""
echo "[1/9] Checking dependencies..."
for cmd in git npm openclaw; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "ERROR: $cmd is required."
        exit 1
    fi
done
echo "✓ core tools detected"

echo ""
echo "[2/9] Detecting compatible Python..."
find_python() {
    for PY in python3 python3.13 python3.12 python3.11 python3.10; do
        if command -v "$PY" >/dev/null 2>&1; then
            if "$PY" - << 'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
            then
                echo "$PY"
                return 0
            fi
        fi
    done
    return 1
}

if PYTHON_BIN="$(find_python)"; then
    echo "✓ Using Python: $PYTHON_BIN"
else
    echo "ERROR: Python 3.10+ not found."
    exit 1
fi

echo ""
echo "[3/9] Downloading or updating SDK..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR"
    git fetch --all --tags
    git reset --hard "origin/$DEFAULT_BRANCH"
else
    git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo "✓ Repository ready"

echo ""
echo "[4/9] Creating Python virtual environment..."
[ -d ".venv" ] && rm -rf .venv
"$PYTHON_BIN" -m venv .venv

# 定义虚拟环境内部 Python 的绝对路径，杜绝环境串扰
VENV_PYTHON="$INSTALL_DIR/.venv/bin/python"

echo ""
echo "[5/9] Installing Python dependencies..."
# --- 核心抗体 2：强制使用 VENV_PYTHON，解决依赖报错 ---
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt
echo "✓ Python dependencies installed"

echo ""
echo "[6/9] API Configuration"
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo ""
    prompt_tty "Enter Spot API Key: " SPOT_API_KEY
    prompt_tty_secret "Enter Spot API Secret: " SPOT_API_SECRET

    if [ -z "$SPOT_API_KEY" ] || [ -z "$SPOT_API_SECRET" ]; then
        echo "ERROR: API credentials cannot be empty."
        exit 1
    fi

    echo ""
    prompt_tty "Enter Futures API Key (press Enter to reuse Spot key): " FUTURES_API_KEY
    if [ -z "$FUTURES_API_KEY" ]; then
        FUTURES_API_KEY="$SPOT_API_KEY"
        FUTURES_API_SECRET="$SPOT_API_SECRET"
    else
        prompt_tty_secret "Enter Futures API Secret: " FUTURES_API_SECRET
    fi

    # 使用虚拟环境的 Python 生成配置
    "$VENV_PYTHON" - "$INSTALL_DIR" "$SPOT_URL" "$FUTURES_URL" "$WS_URL" "$RECV_WINDOW" "$SPOT_API_KEY" "$SPOT_API_SECRET" "$FUTURES_API_KEY" "$FUTURES_API_SECRET" << 'PY'
import json, sys
from pathlib import Path
args = sys.argv[1:]
config = {
    "spot": {"base_url": args[1], "api_key": args[5], "api_secret": args[6], "recv_window": int(args[4])},
    "futures": {"base_url": args[2], "api_key": args[7], "api_secret": args[8], "recv_window": int(args[4])},
    "ws": {"url": args[3]}
}
with open(Path(args[0]) / "config.json", "w") as f:
    json.dump(config, f, indent=2)
PY
    echo "✓ config.json created"
else
    echo "✓ Existing config.json found. Skipping API configuration."
fi

echo ""
echo "[7/9] Building OpenClaw plugin..."
cd "$INSTALL_DIR/openclaw-plugin"
npm install
npm run build

echo ""
echo "[8/9] Installing and enabling OpenClaw plugin..."
# 此时旧记录已被清理，不会报错
openclaw plugins install .
openclaw plugins enable "$PLUGIN_ID"

echo ""
echo "[9/9] Finalizing..."
# --- 核心抗体 3：最后再加固一次 allow 列表 ---
python3 - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
path = sys.argv[1]
pid = sys.argv[2]
if os.path.exists(path):
    with open(path, 'r') as f: data = json.load(f)
    allow = data.setdefault("plugins", {}).setdefault("allow", [])
    if pid not in allow:
        allow.append(pid)
        with open(path, 'w') as f: json.dump(data, f, indent=2)
PY

openclaw gateway --force

echo ""
echo "======================================"
echo "ZKE OpenClaw Plugin Installation Complete"
echo "======================================"

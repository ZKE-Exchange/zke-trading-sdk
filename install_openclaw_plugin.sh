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

# ==========================================
# 1. 最优先：找到高版本 Python
# ==========================================
find_python() {
    for PY in python3 python3.13 python3.12 python3.11 python3.10; do
        if command -v "$PY" >/dev/null 2>&1; then
            if "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
                echo "$PY"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON_BIN="$(find_python || echo "")"
if [ -z "$PYTHON_BIN" ]; then
    echo "ERROR: Python 3.10+ not found. Please install it first."
    exit 1
fi

# ==========================================
# 2. 终极防弹清理逻辑 (带安全气囊)
# ==========================================
cleanup_existing_plugin() {
    echo "Cleaning up existing plugin installation..."
    set +e # 关闭致命报错，防止清理过程意外终止脚本

    openclaw plugins disable "$PLUGIN_ID" >/dev/null 2>&1
    openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1
    rm -rf "$OPENCLAW_EXT_DIR"
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"

    if [ -f "$OPENCLAW_CONFIG" ]; then
        "$PYTHON_BIN" -c '
import json, sys, os
try:
    with open(sys.argv[1], "r") as f: data = json.load(f)
    pid = sys.argv[2]
    modified = False
    if "plugins" in data:
        if pid in data.get("plugins", {}).get("entries", {}):
            del data["plugins"]["entries"][pid]
            modified = True
        allow = data.get("plugins", {}).get("allow", [])
        if pid in allow:
            data["plugins"]["allow"] = [p for p in allow if p != pid]
            modified = True
    if modified:
        with open(sys.argv[1], "w") as f: json.dump(data, f, indent=2)
except Exception: pass
' "$OPENCLAW_CONFIG" "$PLUGIN_ID"
    fi

    set -e # 恢复正常报错监控
}

# ==========================================
# 3. 菜单交互
# ==========================================
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
            ;;
        2)
            echo "Starting full reset..."
            cleanup_existing_plugin
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
# 4. 执行核心安装步骤
# ==========================================
echo ""
echo "[1/9] Checking dependencies..."
for cmd in git npm openclaw; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "ERROR: $cmd is required."
        exit 1
    fi
done
echo "✓ All core tools detected"

echo ""
echo "[2/9] Python version check..."
echo "✓ Using Python: $PYTHON_BIN"

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

echo ""
echo "[4/9] Creating Python virtual environment..."
[ -d ".venv" ] && rm -rf .venv
"$PYTHON_BIN" -m venv .venv
VENV_PYTHON="$INSTALL_DIR/.venv/bin/python"

echo ""
echo "[5/9] Installing Python dependencies..."
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt

echo ""
echo "[6/9] API Configuration"
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo ""
    echo "You can leave API keys blank and configure them later in $INSTALL_DIR/config.json"
    prompt_tty "Enter Spot API Key (press Enter to skip): " SPOT_API_KEY
    prompt_tty_secret "Enter Spot API Secret (press Enter to skip): " SPOT_API_SECRET

    echo ""
    prompt_tty "Enter Futures API Key (press Enter to reuse Spot key or skip): " FUTURES_API_KEY
    if [ -z "$FUTURES_API_KEY" ]; then
        FUTURES_API_KEY="$SPOT_API_KEY"
        FUTURES_API_SECRET="$SPOT_API_SECRET"
    else
        prompt_tty_secret "Enter Futures API Secret (press Enter to skip): " FUTURES_API_SECRET
    fi

    "$VENV_PYTHON" -c '
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
' "$INSTALL_DIR" "$SPOT_URL" "$FUTURES_URL" "$WS_URL" "$RECV_WINDOW" "$SPOT_API_KEY" "$SPOT_API_SECRET" "$FUTURES_API_KEY" "$FUTURES_API_SECRET"
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
openclaw plugins install .
openclaw plugins enable "$PLUGIN_ID"

echo ""
echo "[9/9] Finalizing..."
"$PYTHON_BIN" -c '
import json, sys, os
try:
    with open(sys.argv[1], "r") as f: data = json.load(f)
    pid = sys.argv[2]
    allow = data.setdefault("plugins", {}).setdefault("allow", [])
    if pid not in allow:
        allow.append(pid)
        with open(sys.argv[1], "w") as f: json.dump(data, f, indent=2)
except Exception: pass
' "$OPENCLAW_CONFIG" "$PLUGIN_ID"

openclaw gateway --force

echo ""
echo "======================================"
echo "✅ ZKE OpenClaw Plugin Installation Complete"
echo "======================================"

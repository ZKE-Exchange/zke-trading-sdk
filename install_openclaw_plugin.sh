#!/bin/bash

set -euo pipefail

echo "======================================"
echo "Installing ZKE OpenClaw Plugin"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
PLUGIN_DIR_NAME="zke-openclaw-plugin"

SPOT_URL="https://openapi.zke.com"
FUTURES_URL="https://futuresopenapi.zke.com"
WS_URL="wss://ws.zke.com/kline-api/ws"
RECV_WINDOW="5000"

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

echo ""
echo "[1/9] Checking dependencies..."

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is required."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm is required for building the OpenClaw plugin."
    exit 1
fi

if ! command -v openclaw >/dev/null 2>&1; then
    echo "ERROR: openclaw CLI is required."
    exit 1
fi

echo "✓ git detected"
echo "✓ npm detected"
echo "✓ openclaw detected"

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
    PYTHON_VER="$("$PYTHON_BIN" - << 'PY'
import sys
print(".".join(map(str, sys.version_info[:3])))
PY
)"
    echo "✓ Using Python: $PYTHON_BIN ($PYTHON_VER)"
else
    echo "ERROR: Python 3.10+ not found."
    echo "For macOS with Homebrew:"
    echo "  brew install python"
    exit 1
fi

echo ""
echo "[3/9] Downloading or updating SDK..."

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation"
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "[4/9] Creating Python virtual environment..."

if [ -d ".venv" ]; then
    echo "Existing virtual environment found. Recreating..."
    rm -rf .venv
fi

"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "✓ Virtual environment created"

echo ""
echo "[5/9] Installing Python dependencies..."

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Python dependencies installed"

echo ""
echo "[6/9] API Configuration"
echo ""
echo "Create API keys at:"
echo "https://www.zke.com/en_US/personal/apiManagement"
echo ""

API_KEY=""
API_SECRET=""

prompt_tty "Enter ZKE API Key: " API_KEY
prompt_tty_secret "Enter ZKE API Secret: " API_SECRET

if [ -z "$API_KEY" ] || [ -z "$API_SECRET" ]; then
    echo "ERROR: API key and secret cannot be empty."
    exit 1
fi

echo ""
echo "Generating config.json..."

"$PYTHON_BIN" - "$INSTALL_DIR" "$SPOT_URL" "$FUTURES_URL" "$WS_URL" "$RECV_WINDOW" "$API_KEY" "$API_SECRET" << 'PY'
import json
import sys
from pathlib import Path

install_dir, spot_url, futures_url, ws_url, recv_window, api_key, api_secret = sys.argv[1:]

config = {
    "spot": {
        "base_url": spot_url,
        "api_key": api_key,
        "api_secret": api_secret,
        "recv_window": int(recv_window),
    },
    "futures": {
        "base_url": futures_url,
        "api_key": api_key,
        "api_secret": api_secret,
        "recv_window": int(recv_window),
    },
    "ws": {
        "url": ws_url,
    },
}

Path(install_dir).mkdir(parents=True, exist_ok=True)
with open(Path(install_dir) / "config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("✓ config.json created")
PY

echo ""
echo "[7/9] Building OpenClaw plugin..."

PLUGIN_SRC="$INSTALL_DIR/openclaw-plugin"

if [ ! -f "$PLUGIN_SRC/package.json" ]; then
    echo "ERROR: plugin package.json not found: $PLUGIN_SRC/package.json"
    exit 1
fi

if [ ! -f "$PLUGIN_SRC/openclaw.plugin.json" ]; then
    echo "ERROR: plugin manifest not found: $PLUGIN_SRC/openclaw.plugin.json"
    exit 1
fi

cd "$PLUGIN_SRC"
npm install
npm run build

echo "✓ Plugin build complete"

echo ""
echo "[8/9] Installing and enabling OpenClaw plugin..."

openclaw plugins uninstall zke-trading >/dev/null 2>&1 || true
openclaw plugins install -l "$PLUGIN_SRC"
openclaw plugins enable zke-trading

echo "✓ Plugin installed and enabled"

echo ""
echo "[9/9] Installation complete"

echo ""
echo "======================================"
echo "ZKE OpenClaw Plugin installed"
echo "======================================"
echo ""
echo "SDK location:"
echo "  $INSTALL_DIR"
echo ""
echo "Plugin source:"
echo "  $PLUGIN_SRC"
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw"
echo "  2. Test prompts:"
echo "     Check BTC price on ZKE"
echo "     Show my USDT balance on ZKE"
echo "     Show my futures positions on ZKE"
echo ""
echo "Plugin diagnostics:"
echo "  openclaw plugins list"
echo "  openclaw plugins info zke-trading"
echo "  openclaw plugins doctor"
echo ""
echo "======================================"

#!/bin/bash

set -e

echo "======================================"
echo "Installing ZKE Trading Skill"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
PLUGIN_DIR="$HOME/.openclaw/plugins/zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"

SPOT_URL="https://openapi.zke.com"
FUTURES_URL="https://futuresopenapi.zke.com"
WS_URL="wss://ws.zke.com/kline-api/ws"
RECV_WINDOW="5000"

echo ""
echo "[1/9] Checking dependencies..."

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is required."
    exit 1
fi

echo "✓ git detected"

echo ""
echo "[2/9] Detecting compatible Python..."

find_python() {
    for PY in python3 python3.13 python3.12 python3.11 python3.10; do
        if command -v "$PY" >/dev/null 2>&1; then
            OK=$("$PY" - << 'PY'
import sys
print("yes" if sys.version_info >= (3, 10) else "no")
PY
)
            if [ "$OK" = "yes" ]; then
                echo "$PY"
                return 0
            fi
        fi
    done
    return 1
}

if PYTHON_BIN=$(find_python); then
    PYTHON_VER=$("$PYTHON_BIN" - << 'PY'
import sys
print(".".join(map(str, sys.version_info[:3])))
PY
)
    echo "✓ Using Python: $PYTHON_BIN ($PYTHON_VER)"
else
    echo "ERROR: Python 3.10+ not found."
    echo ""
    echo "Please install Python 3.10 or newer, then rerun this installer."
    echo ""
    echo "For macOS with Homebrew:"
    echo "  brew install python"
    echo ""
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
    echo "Existing virtual environment found. Recreating with $PYTHON_BIN ..."
    rm -rf .venv
fi

"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "✓ Virtual environment created"

echo ""
echo "[5/9] Installing dependencies..."

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"

echo ""
echo "[6/9] API Configuration"
echo ""
echo "Create API keys at:"
echo "https://www.zke.com/en_US/personal/apiManagement"
echo ""

read -rp "Enter ZKE API Key: " API_KEY
read -rsp "Enter ZKE API Secret: " API_SECRET
echo ""

echo ""
echo "Generating config.json..."

export INSTALL_DIR SPOT_URL FUTURES_URL WS_URL RECV_WINDOW API_KEY API_SECRET

python << 'PY'
import json
import os
from pathlib import Path

install_dir = Path(os.environ["INSTALL_DIR"])
config = {
    "spot": {
        "base_url": os.environ["SPOT_URL"],
        "api_key": os.environ["API_KEY"],
        "api_secret": os.environ["API_SECRET"],
        "recv_window": int(os.environ["RECV_WINDOW"]),
    },
    "futures": {
        "base_url": os.environ["FUTURES_URL"],
        "api_key": os.environ["API_KEY"],
        "api_secret": os.environ["API_SECRET"],
        "recv_window": int(os.environ["RECV_WINDOW"]),
    },
    "ws": {
        "url": os.environ["WS_URL"],
    },
}
with open(install_dir / "config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
PY

echo "✓ config.json created"

echo ""
echo "[7/9] Installing OpenClaw plugin..."

mkdir -p "$PLUGIN_DIR"

if [ -d "openclaw" ]; then
    cp -r openclaw/* "$PLUGIN_DIR/"
    echo "✓ Plugin installed to: $PLUGIN_DIR"
else
    echo "WARNING: openclaw directory not found"
fi

echo ""
echo "[8/9] Checking existing MCP server..."

if pgrep -f "python mcp_server.py" >/dev/null 2>&1; then
    echo "Existing MCP server found. Stopping..."
    pkill -f "python mcp_server.py" || true
    sleep 1
else
    echo "No existing MCP server"
fi

echo ""
read -rp "Start MCP server now? (y/n): " START_MCP

if [[ "$START_MCP" == "y" || "$START_MCP" == "Y" ]]; then
    echo "Starting MCP server..."
    nohup python mcp_server.py > "$INSTALL_DIR/mcp.log" 2>&1 &
    sleep 2

    if pgrep -f "python mcp_server.py" >/dev/null 2>&1; then
        echo "✓ MCP server started"
        echo "Log file: $INSTALL_DIR/mcp.log"
    else
        echo "ERROR: MCP server failed to start"
        echo "Check log file: $INSTALL_DIR/mcp.log"
        exit 1
    fi
else
    echo "Skipping MCP startup"
fi

echo ""
echo "[9/9] Installation complete"

echo ""
echo "======================================"
echo "ZKE Trading Skill installed"
echo "======================================"
echo ""
echo "Install location:"
echo "  $INSTALL_DIR"
echo ""
echo "Plugin location:"
echo "  $PLUGIN_DIR"
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw"
echo "  2. Try prompts like:"
echo "     Check BTC price on ZKE"
echo "     Show my USDT balance on ZKE"
echo ""
echo "Manual test:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python main.py ticker BTCUSDT"
echo ""
echo "If MCP was not started automatically:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python mcp_server.py"
echo ""
echo "======================================"

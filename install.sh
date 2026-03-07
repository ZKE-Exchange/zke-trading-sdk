#!/bin/bash

set -euo pipefail

echo "======================================"
echo "Installing ZKE Trading Skill"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
SKILL_DIR="$HOME/.openclaw/skills/zke_trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"

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

echo "✓ git detected"

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
    echo ""
    echo "Please install Python 3.10 or newer."
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
echo "[7/9] Installing OpenClaw shared skill..."

mkdir -p "$SKILL_DIR"

if [ -f "$INSTALL_DIR/openclaw/skills/zke_trading/SKILL.md" ]; then
    cp "$INSTALL_DIR/openclaw/skills/zke_trading/SKILL.md" "$SKILL_DIR/SKILL.md"
    echo "✓ Skill installed to: $SKILL_DIR"
else
    echo "ERROR: SKILL.md not found in repository"
    exit 1
fi

echo ""
echo "[8/9] Restarting MCP server..."

if pgrep -f "mcp_server.py" >/dev/null 2>&1; then
    echo "Existing MCP server found. Stopping..."
    pkill -f "mcp_server.py" || true
    sleep 1
else
    echo "No existing MCP server"
fi

START_MCP=""
prompt_tty "Start MCP server now? (y/n): " START_MCP

if [[ "$START_MCP" == "y" || "$START_MCP" == "Y" ]]; then
    echo "Starting MCP server..."
    nohup python mcp_server.py > "$INSTALL_DIR/mcp.log" 2>&1 &
    MCP_PID=$!
    sleep 2

    if kill -0 "$MCP_PID" >/dev/null 2>&1; then
        echo "✓ MCP server started"
        echo "PID: $MCP_PID"
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
echo "Skill location:"
echo "  $SKILL_DIR"
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw / gateway"
echo "  2. Try prompts:"
echo "     Check BTC price on ZKE"
echo "     Show my USDT balance on ZKE"
echo ""
echo "Manual SDK test:"
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

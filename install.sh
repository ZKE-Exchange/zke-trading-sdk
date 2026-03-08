#!/bin/bash

set -euo pipefail

echo "======================================"
echo "Installing ZKE Trading SDK"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_BRANCH="main"

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
echo "[1/8] Checking dependencies..."

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is required."
    exit 1
fi

echo "✓ git detected"

echo ""
echo "[2/8] Detecting compatible Python..."

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
echo "[3/8] Downloading or updating SDK..."

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Existing installation detected, updating..."
    cd "$INSTALL_DIR"
    git fetch --all --tags
    git reset --hard "origin/$DEFAULT_BRANCH"
else
    git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found."
    exit 1
fi

echo "✓ Repository ready"

echo ""
echo "[4/8] Creating Python virtual environment..."

if [ -d ".venv" ]; then
    echo "Existing virtual environment found. Recreating..."
    rm -rf .venv
fi

"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "✓ Virtual environment created"

echo ""
echo "[5/8] Installing dependencies..."

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"

echo ""
echo "[6/8] API Configuration"
echo ""
echo "Create API keys at:"
echo "https://www.zke.com/en_US/personal/apiManagement"
echo ""
echo "You can use separate API keys for Spot and Futures."
echo "If you want to reuse the Spot key for Futures, just press Enter."
echo ""

SPOT_API_KEY=""
SPOT_API_SECRET=""
FUTURES_API_KEY=""
FUTURES_API_SECRET=""

prompt_tty "Enter Spot API Key: " SPOT_API_KEY
prompt_tty_secret "Enter Spot API Secret: " SPOT_API_SECRET

if [ -z "$SPOT_API_KEY" ] || [ -z "$SPOT_API_SECRET" ]; then
    echo "ERROR: Spot API key and secret cannot be empty."
    exit 1
fi

echo ""
prompt_tty "Enter Futures API Key (press Enter to reuse Spot key): " FUTURES_API_KEY
if [ -z "$FUTURES_API_KEY" ]; then
    FUTURES_API_KEY="$SPOT_API_KEY"
    FUTURES_API_SECRET="$SPOT_API_SECRET"
    echo "✓ Reusing Spot API credentials for Futures"
else
    prompt_tty_secret "Enter Futures API Secret: " FUTURES_API_SECRET
    if [ -z "$FUTURES_API_SECRET" ]; then
        echo "ERROR: Futures API secret cannot be empty when Futures API key is provided."
        exit 1
    fi
fi

echo ""
echo "Generating config.json..."

"$PYTHON_BIN" - "$INSTALL_DIR" "$SPOT_URL" "$FUTURES_URL" "$WS_URL" "$RECV_WINDOW" "$SPOT_API_KEY" "$SPOT_API_SECRET" "$FUTURES_API_KEY" "$FUTURES_API_SECRET" << 'PY'
import json
import sys
from pathlib import Path

(
    install_dir,
    spot_url,
    futures_url,
    ws_url,
    recv_window,
    spot_api_key,
    spot_api_secret,
    futures_api_key,
    futures_api_secret,
) = sys.argv[1:]

config = {
    "spot": {
        "base_url": spot_url,
        "api_key": spot_api_key,
        "api_secret": spot_api_secret,
        "recv_window": int(recv_window),
    },
    "futures": {
        "base_url": futures_url,
        "api_key": futures_api_key,
        "api_secret": futures_api_secret,
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
echo "[7/8] Running validation checks..."

python -m py_compile main.py
echo "✓ main.py syntax check passed"

python -m py_compile mcp_server.py
echo "✓ mcp_server.py syntax check passed"

echo ""
echo "Testing Spot public API..."
if python main.py ping >/dev/null 2>&1; then
    echo "✓ Spot API connectivity check passed"
else
    echo "WARNING: Spot API connectivity check failed"
    echo "You can still inspect config.json and test manually."
fi

echo ""
echo "[8/8] Installation complete"

echo ""
echo "======================================"
echo "ZKE Trading SDK installed"
echo "======================================"
echo ""
echo "Install location:"
echo "  $INSTALL_DIR"
echo ""
echo "Manual SDK test:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python main.py ticker BTCUSDT"
echo ""
echo "Manual MCP start:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python mcp_server.py"
echo ""
echo "Manual config file:"
echo "  $INSTALL_DIR/config.json"
echo ""
echo "======================================"

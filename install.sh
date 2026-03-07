#!/bin/bash

set -e

echo "======================================"
echo "Installing ZKE Trading Skill"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
PLUGIN_DIR="$HOME/.openclaw/plugins/zke-trading"
REPO="https://github.com/ZKE-Exchange/zke-trading-sdk.git"

SPOT_URL="https://openapi.zke.com"
FUTURES_URL="https://futuresopenapi.zke.com"
WS_URL="wss://ws.zke.com/kline-api/ws"

PYTHON_BIN="python3"

echo ""
echo "[1/9] Checking dependencies..."

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is required."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required."
    exit 1
fi

echo "✓ git detected"
echo "✓ python3 detected"

echo ""
echo "[2/9] Checking Python version..."

PYTHON_OK=$(python3 - << 'PY'
import sys
print("yes" if sys.version_info >= (3, 10) else "no")
PY
)

PYTHON_VER=$(python3 - << 'PY'
import sys
print(".".join(map(str, sys.version_info[:3])))
PY
)

echo "Detected Python version: $PYTHON_VER"

if [ "$PYTHON_OK" != "yes" ]; then
    echo ""
    echo "Python 3.10+ is required because the 'mcp' package does not support Python $PYTHON_VER."
    echo ""

    if command -v brew >/dev/null 2>&1; then
        echo "Homebrew detected."
        read -rp "Install Python 3.11 with Homebrew now? (y/n): " INSTALL_PY311

        if [[ "$INSTALL_PY311" == "y" || "$INSTALL_PY311" == "Y" ]]; then
            brew install python@3.11

            if [ -x "/opt/homebrew/bin/python3.11" ]; then
                PYTHON_BIN="/opt/homebrew/bin/python3.11"
            elif [ -x "/usr/local/bin/python3.11" ]; then
                PYTHON_BIN="/usr/local/bin/python3.11"
            else
                echo "ERROR: Python 3.11 installation finished but executable not found."
                exit 1
            fi

            echo "✓ Using Python: $PYTHON_BIN"
        else
            echo "Installation cancelled. Please install Python 3.10+ and rerun."
            exit 1
        fi
    else
        echo "ERROR: Homebrew not found."
        echo "Please install Python 3.10+ manually, or install Homebrew first."
        echo "Homebrew: https://brew.sh"
        exit 1
    fi
else
    if [ -x "/opt/homebrew/bin/python3.11" ]; then
        PYTHON_BIN="/opt/homebrew/bin/python3.11"
    elif [ -x "/usr/local/bin/python3.11" ]; then
        PYTHON_BIN="/usr/local/bin/python3.11"
    else
        PYTHON_BIN="python3"
    fi
fi

echo ""
echo "[3/9] Downloading or updating SDK..."

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation"
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "[4/9] Creating Python environment..."

if [ -d ".venv" ]; then
    echo "Existing virtual environment found. Recreating with $PYTHON_BIN ..."
    rm -rf .venv
fi

"$PYTHON_BIN" -m venv .venv
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

cat > "$INSTALL_DIR/config.json" << EOF
{
  "spot": {
    "base_url": "$SPOT_URL",
    "api_key": "$API_KEY",
    "api_secret": "$API_SECRET",
    "recv_window": 5000
  },
  "futures": {
    "base_url": "$FUTURES_URL",
    "api_key": "$API_KEY",
    "api_secret": "$API_SECRET",
    "recv_window": 5000
  },
  "ws": {
    "url": "$WS_URL"
  }
}
EOF

echo "✓ config.json created"

echo ""
echo "[7/9] Installing OpenClaw plugin..."

mkdir -p "$PLUGIN_DIR"

if [ -d "openclaw" ]; then
    cp -r openclaw/* "$PLUGIN_DIR/"
    echo "✓ Plugin installed"
else
    echo "WARNING: openclaw directory missing"
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
read -rp "Start MCP server now? (y/n): " START

if [[ "$START" == "y" || "$START" == "Y" ]]; then
    echo "Starting MCP server..."
    nohup python mcp_server.py > "$INSTALL_DIR/mcp.log" 2>&1 &
    sleep 2

    if pgrep -f "python mcp_server.py" >/dev/null 2>&1; then
        echo "✓ MCP server started"
        echo "Log file: $INSTALL_DIR/mcp.log"
    else
        echo "ERROR: MCP server failed to start"
        echo "Check log: $INSTALL_DIR/mcp.log"
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
echo "$INSTALL_DIR"
echo ""
echo "Next steps:"
echo "1. Restart OpenClaw"
echo "2. Try:"
echo "   Check BTC price on ZKE"
echo "   Show my USDT balance on ZKE"
echo ""
echo "Manual test:"
echo "cd $INSTALL_DIR"
echo "source .venv/bin/activate"
echo "python main.py ticker BTCUSDT"
echo ""
echo "======================================"

#!/bin/bash

set -e

echo "======================================"
echo "Installing ZKE Trading Skill..."
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
OPENCLAW_PLUGIN_DIR="$HOME/.openclaw/plugins/zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_SPOT_BASE_URL="https://openapi.zke.com"
DEFAULT_FUTURES_BASE_URL="https://futuresopenapi.zke.com"
DEFAULT_WS_URL="wss://ws.zke.com/kline-api/ws"
DEFAULT_RECV_WINDOW="5000"

echo ""
echo "[1/10] Checking system dependencies..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not installed."
    exit 1
fi
echo "✓ python3 found: $(python3 --version)"

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_OK=$(python3 - << 'PY'
import sys
print("yes" if sys.version_info >= (3, 10) else "no")
PY
)

if [ "$PYTHON_OK" != "yes" ]; then
    echo "ERROR: Python 3.10 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi
echo "✓ Python version is supported"

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is not installed."
    exit 1
fi
echo "✓ git found"

if ! command -v pip3 >/dev/null 2>&1; then
    echo "WARNING: pip3 not found, trying to bootstrap with ensurepip..."
    python3 -m ensurepip --upgrade || true
fi
echo "✓ pip available"

echo ""
echo "[2/10] Detecting OS..."

UNAME_OUT="$(uname -s)"
case "${UNAME_OUT}" in
    Linux*)     OS_NAME="Linux" ;;
    Darwin*)    OS_NAME="MacOS" ;;
    *)          OS_NAME="Unknown" ;;
esac
echo "✓ Detected OS: $OS_NAME"

echo ""
echo "[3/10] Clone or update repository..."

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Existing installation found at: $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "[4/10] Creating Python virtual environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo ""
echo "[5/10] Upgrading pip and installing dependencies..."

python -m pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "[6/10] Collecting API configuration..."

read -rp "Spot API Key: " SPOT_API_KEY
read -rsp "Spot API Secret: " SPOT_API_SECRET
echo ""
read -rp "Futures API Key: " FUTURES_API_KEY
read -rsp "Futures API Secret: " FUTURES_API_SECRET
echo ""

echo ""
echo "Using default endpoints:"
echo "  Spot Base URL    = $DEFAULT_SPOT_BASE_URL"
echo "  Futures Base URL = $DEFAULT_FUTURES_BASE_URL"
echo "  WebSocket URL    = $DEFAULT_WS_URL"
echo "  Recv Window      = $DEFAULT_RECV_WINDOW"

echo ""
echo "[7/10] Writing config.json..."

cat > "$INSTALL_DIR/config.json" << EOF
{
  "spot": {
    "base_url": "$DEFAULT_SPOT_BASE_URL",
    "api_key": "$SPOT_API_KEY",
    "api_secret": "$SPOT_API_SECRET",
    "recv_window": $DEFAULT_RECV_WINDOW
  },
  "futures": {
    "base_url": "$DEFAULT_FUTURES_BASE_URL",
    "api_key": "$FUTURES_API_KEY",
    "api_secret": "$FUTURES_API_SECRET",
    "recv_window": $DEFAULT_RECV_WINDOW
  },
  "ws": {
    "url": "$DEFAULT_WS_URL"
  }
}
EOF

echo "✓ config.json created"

echo ""
echo "[8/10] Installing OpenClaw plugin..."

mkdir -p "$OPENCLAW_PLUGIN_DIR"

if [ -d "openclaw" ]; then
    cp -r openclaw/* "$OPENCLAW_PLUGIN_DIR/"
    echo "✓ Plugin installed to: $OPENCLAW_PLUGIN_DIR"
else
    echo "WARNING: openclaw directory not found, plugin files were not copied"
fi

echo ""
echo "[9/10] Verifying installation..."

if [ -f "$INSTALL_DIR/mcp_server.py" ]; then
    echo "✓ mcp_server.py found"
else
    echo "ERROR: mcp_server.py missing"
    exit 1
fi

if [ -f "$INSTALL_DIR/config.json" ]; then
    echo "✓ config.json found"
else
    echo "ERROR: config.json missing"
    exit 1
fi

if [ -f "$OPENCLAW_PLUGIN_DIR/openclaw.plugin.json" ]; then
    echo "✓ openclaw.plugin.json found"
else
    echo "WARNING: openclaw.plugin.json not found"
fi

if [ -f "$OPENCLAW_PLUGIN_DIR/skills/zke_trading/SKILL.md" ]; then
    echo "✓ SKILL.md found"
else
    echo "WARNING: SKILL.md not found"
fi

echo ""
echo "[10/10] MCP server startup..."

read -rp "Start MCP server now? (y/n): " START_MCP

if [[ "$START_MCP" == "y" || "$START_MCP" == "Y" ]]; then
    echo "Checking existing MCP server..."

    if pgrep -f "python mcp_server.py" >/dev/null 2>&1; then
        echo "Existing MCP server detected. Restarting..."
        pkill -f "python mcp_server.py" || true
        sleep 1
    else
        echo "No existing MCP server found."
    fi

    echo "Starting MCP server..."
    cd "$INSTALL_DIR"
    # shellcheck disable=SC1091
    source .venv/bin/activate
    nohup python mcp_server.py > "$INSTALL_DIR/mcp.log" 2>&1 &

    sleep 2

    if pgrep -f "python mcp_server.py" >/dev/null 2>&1; then
        echo "✓ MCP server started successfully"
        echo "✓ Log file: $INSTALL_DIR/mcp.log"
    else
        echo "ERROR: MCP server failed to start"
        echo "Check log file: $INSTALL_DIR/mcp.log"
        exit 1
    fi
else
    echo "Skipping MCP auto-start."
fi

echo ""
echo "======================================"
echo "ZKE Trading Skill installation complete"
echo "======================================"
echo ""
echo "Installation path:"
echo "  $INSTALL_DIR"
echo ""
echo "Plugin path:"
echo "  $OPENCLAW_PLUGIN_DIR"
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw"
echo "  2. Try prompts like:"
echo "     Check BTC price on ZKE"
echo "     Show my USDT balance on ZKE"
echo ""
echo "Manual commands:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python main.py ping"
echo "  python main.py ticker BTCUSDT"
echo ""
echo "If MCP was not started automatically:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python mcp_server.py"
echo ""
echo "======================================"

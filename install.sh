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

echo ""
echo "[1/8] Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is required."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "ERROR: git is required."
    exit 1
fi

echo "✓ python3 and git detected"

echo ""
echo "[2/8] Downloading or updating SDK..."

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation"
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "[3/8] Creating Python environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo ""
echo "[4/8] Installing dependencies..."

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"

echo ""
echo "[5/8] API Configuration"

echo ""
echo "Create API keys at:"
echo "https://zke.com/user/api"
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
echo "[6/8] Installing OpenClaw plugin..."

mkdir -p "$PLUGIN_DIR"

if [ -d "openclaw" ]; then
    cp -r openclaw/* "$PLUGIN_DIR/"
    echo "✓ Plugin installed"
else
    echo "WARNING: openclaw directory missing"
fi

echo ""
echo "[7/8] Checking existing MCP server..."

if pgrep -f "python mcp_server.py" > /dev/null; then
    echo "Existing MCP server found. Restarting..."
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

    if pgrep -f "python mcp_server.py" > /dev/null; then
        echo "✓ MCP server started"
        echo "Log file: $INSTALL_DIR/mcp.log"
    else
        echo "ERROR: MCP server failed to start"
        exit 1
    fi

else
    echo "Skipping MCP startup"
fi

echo ""
echo "[8/8] Installation complete"

echo ""
echo "======================================"
echo "ZKE Trading Skill installed"
echo "======================================"
echo ""

echo "Install location:"
echo "$INSTALL_DIR"

echo ""
echo "Next steps:"
echo ""
echo "1. Restart OpenClaw"
echo ""
echo "2. Try prompts:"
echo ""
echo "Check BTC price on ZKE"
echo "Show my USDT balance on ZKE"
echo ""

echo "Manual commands:"
echo ""
echo "cd $INSTALL_DIR"
echo "source .venv/bin/activate"
echo "python main.py ticker BTCUSDT"

echo ""
echo "======================================"

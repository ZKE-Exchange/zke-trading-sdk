#!/bin/bash

echo "======================================"
echo "Installing ZKE Trading Skill..."
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
OPENCLAW_PLUGIN_DIR="$HOME/.openclaw/plugins/zke-trading"

echo "Step 1: cloning repository..."

if [ -d "$INSTALL_DIR" ]; then
    echo "Existing installation found. Updating..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone https://github.com/ZKE-Exchange/zke-trading-sdk.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo "Step 2: creating python environment..."

python3 -m venv .venv
source .venv/bin/activate

echo "Step 3: installing dependencies..."

pip install -r requirements.txt

echo "Step 4: installing OpenClaw plugin..."

mkdir -p "$OPENCLAW_PLUGIN_DIR"

cp -r openclaw/* "$OPENCLAW_PLUGIN_DIR/"

echo "======================================"
echo "ZKE Trading Skill installed!"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure API keys:"
echo "   $INSTALL_DIR/config.json"
echo ""
echo "2. Start MCP server:"
echo "   cd $INSTALL_DIR"
echo "   source .venv/bin/activate"
echo "   python mcp_server.py"
echo ""
echo "3. Restart OpenClaw"
echo ""
echo "======================================"

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

cleanup_existing_plugin() {
    echo "Cleaning up existing plugin installation..."
    openclaw plugins disable "$PLUGIN_ID" >/dev/null 2>&1 || true
    openclaw plugins uninstall "$PLUGIN_ID" >/dev/null 2>&1 || true
    rm -rf "$OPENCLAW_EXT_DIR"
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"
}

# Check for existing installation
IS_SDK_INSTALLED=false
IS_PLUGIN_REGISTERED=false

if [ -d "$INSTALL_DIR" ]; then IS_SDK_INSTALLED=true; fi
if [ -d "$OPENCLAW_EXT_DIR" ]; then IS_PLUGIN_REGISTERED=true; fi

if $IS_SDK_INSTALLED || $IS_PLUGIN_REGISTERED; then
    echo ""
    echo "Existing ZKE Trading installation detected."
    if $IS_PLUGIN_REGISTERED; then
        echo "Status: Plugin is installed and registered."
    else
        echo "Status: SDK found, but plugin is not registered."
    fi
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
            echo ""
            echo "Starting update process..."
            if $IS_PLUGIN_REGISTERED; then cleanup_existing_plugin; fi
            ;;
        2)
            echo ""
            echo "Starting full reset..."
            cleanup_existing_plugin
            echo "Removing SDK directory: $INSTALL_DIR"
            rm -rf "$INSTALL_DIR"
            ;;
        3)
            echo ""
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

echo ""
echo "[1/9] Checking dependencies..."

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is required."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm is required."
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
    echo "Existing repository detected, updating..."
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

if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo ""
    echo "Create API keys at:"
    echo "https://www.zke.com/en_US/personal/apiManagement"
    echo ""
    echo "You can use separate API keys for Spot and Futures."
    echo "Press Enter on Futures API Key to reuse the Spot credentials."
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
else
    echo "✓ Existing config.json found. Skipping API configuration."
fi

echo ""
echo "[7/9] Building OpenClaw plugin..."

PLUGIN_SRC="$INSTALL_DIR/openclaw-plugin"

if [ ! -d "$PLUGIN_SRC" ]; then
    echo "ERROR: Plugin source directory not found: $PLUGIN_SRC"
    exit 1
fi

if [ ! -f "$PLUGIN_SRC/package.json" ]; then
    echo "ERROR: package.json not found: $PLUGIN_SRC/package.json"
    exit 1
fi

if [ ! -f "$PLUGIN_SRC/openclaw.plugin.json" ]; then
    echo "ERROR: openclaw.plugin.json not found: $PLUGIN_SRC/openclaw.plugin.json"
    exit 1
fi

if [ ! -f "$PLUGIN_SRC/skills/zke_trading/SKILL.md" ]; then
    echo "ERROR: skills/zke_trading/SKILL.md not found"
    exit 1
fi

cd "$PLUGIN_SRC"
rm -rf dist node_modules

npm install
npm run build

if [ ! -f "$PLUGIN_SRC/dist/index.js" ]; then
    echo "ERROR: Plugin build failed, dist/index.js not found"
    exit 1
fi

echo "✓ Plugin build complete"

echo ""
echo "[8/9] Installing and enabling OpenClaw plugin..."

openclaw plugins install "$PLUGIN_SRC"
openclaw plugins enable "$PLUGIN_ID"

echo "✓ Plugin installed and enabled"

echo ""
echo "[9/9] Final verification..."

mkdir -p "$HOME/.openclaw"

"$PYTHON_BIN" - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json
import sys
from pathlib import Path

cfg_path = Path(sys.argv[1])
plugin_id = sys.argv[2]

if cfg_path.exists():
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
else:
    data = {}

plugins = data.get("plugins")
if not isinstance(plugins, dict):
    plugins = {}
    data["plugins"] = plugins

allow = plugins.get("allow")
if not isinstance(allow, list):
    allow = []
    plugins["allow"] = allow

if plugin_id not in allow:
    allow.append(plugin_id)

cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✓ Updated OpenClaw allowlist")
PY

if openclaw plugins info "$PLUGIN_ID" >/dev/null 2>&1; then
    echo "✓ Plugin verification passed"
else
    echo "WARNING: Plugin installed but verification returned non-zero"
fi

echo ""
echo "Running basic Python validation..."
cd "$INSTALL_DIR"
source .venv/bin/activate
python -m py_compile main.py
python -m py_compile mcp_server.py
echo "✓ Python validation passed"

echo ""
echo "======================================"
echo "ZKE OpenClaw Plugin Installation Complete"
echo "======================================"
echo ""
echo "SDK location:"
echo "  $INSTALL_DIR"
echo ""
echo "Plugin source:"
echo "  $PLUGIN_SRC"
echo ""
echo "Next steps:"
echo "  1. Completely restart OpenClaw (Run: openclaw gateway --force)"
echo "  2. Open a NEW chat/session"
echo "  3. Test prompts:"
echo "     Check BTC price on ZKE"
echo "     Show my USDT balance on ZKE"
echo "     Show my futures positions on ZKE"
echo "     Place a BTC limit order on ZKE"
echo ""
echo "Diagnostics:"
echo "  openclaw plugins list"
echo "  openclaw plugins info $PLUGIN_ID"
echo "  openclaw plugins doctor"
echo ""
echo "======================================"

#!/bin/bash
set -euo pipefail

echo "======================================"
echo "ZKE OpenClaw Plugin Installer"
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
# 使用你指定的绝对路径
OPENCLAW_CONFIG="/Users/openclaw/.openclaw/openclaw.json"

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

echo "Please select an action:"
echo "  1) Fresh Install (全新安装)"
echo "  2) Uninstall (彻底卸载，修复配置死锁)"
echo "  3) Cancel (取消)"
echo ""

prompt_tty "Enter choice [1-3]: " MENU_CHOICE

# ==========================================
# 选 2: 彻底卸载与修复流程
# ==========================================
if [ "$MENU_CHOICE" == "2" ]; then
    echo "Starting deep uninstallation..."
    
    # 加上 < /dev/null 防止管道吞噬代码
    openclaw plugins disable "$PLUGIN_ID" < /dev/null >/dev/null 2>&1 || true
    openclaw plugins uninstall "$PLUGIN_ID" < /dev/null >/dev/null 2>&1 || true
    
    rm -rf "$OPENCLAW_EXT_DIR" || true
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID" || true
    rm -rf "$INSTALL_DIR" || true

    # 外科手术清理 JSON 幽灵记录
    if [ -f "$OPENCLAW_CONFIG" ]; then
        python3 -c '
import json, sys
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
' "$OPENCLAW_CONFIG" "$PLUGIN_ID" || true
    fi
    echo "✅ Uninstallation and config repair successful."
    echo "You can now run the script again to select [1] Fresh Install."
    exit 0

elif [ "$MENU_CHOICE" == "3" ]; then
    echo "Operation cancelled."
    exit 0
elif [ "$MENU_CHOICE" != "1" ]; then
    echo "Invalid choice. Exiting."
    exit 1
fi

# ==========================================
# 选 1: 纯粹的全新安装流程 (不干涉用户的清理操作)
# ==========================================
echo "Starting fresh installation..."

echo ""
echo "[1/9] Checking dependencies..."
for cmd in git npm openclaw python3; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "ERROR: $cmd is required."
        exit 1
    fi
done

echo ""
echo "[2/9] Finding compatible Python (3.10+)..."
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
echo "✓ Using Python: $PYTHON_BIN"

echo ""
echo "[3/9] Downloading SDK..."
git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"

echo ""
echo "[4/9] Creating Python virtual environment..."
"$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv"
VENV_PYTHON="$INSTALL_DIR/.venv/bin/python"

echo ""
echo "[5/9] Installing Python dependencies..."
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r "$INSTALL_DIR/requirements.txt"

echo ""
echo "[6/9] API Configuration"
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

echo ""
echo "[7/9] Building OpenClaw plugin..."
cd "$INSTALL_DIR/openclaw-plugin"
npm install
npm run build

echo ""
echo "[8/9] Installing and enabling OpenClaw plugin..."
# 加上 < /dev/null 防止管道吞噬代码
openclaw plugins install . < /dev/null
openclaw plugins enable "$PLUGIN_ID" < /dev/null

echo ""
echo "[9/9] Finalizing..."
openclaw gateway --force < /dev/null

echo ""
echo "======================================"
echo "✅ ZKE OpenClaw Plugin Installation Complete"
echo "======================================"

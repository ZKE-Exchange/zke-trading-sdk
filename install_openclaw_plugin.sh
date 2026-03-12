#!/bin/bash

set -euo pipefail

echo "======================================"
echo "ZKE OpenClaw Plugin: Ultimate Robust Edition"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_BRANCH="main"
PLUGIN_ID="zke-trading"
OPENCLAW_EXT_DIR="$HOME/.openclaw/extensions/$PLUGIN_ID"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

# ---------------------------------------------------------
# [你的核心逻辑] 自动探测 3.10+ 的高版本 Python
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# [我的核心逻辑] 手术级清理，保留其他插件，打破死锁
# ---------------------------------------------------------
cleanup_existing_plugin() {
    echo "Cleaning up existing plugin records (Physically & Logically)..."
    rm -rf "$OPENCLAW_EXT_DIR"
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"

    if [ -f "$OPENCLAW_CONFIG" ]; then
        # 即使 CLI 挂了，我们也用 Python 直接修文件
        python3 - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
cfg_path = sys.argv[1]
pid = sys.argv[2]
try:
    with open(cfg_path, 'r') as f:
        data = json.load(f)
    modified = False
    if "plugins" in data:
        entries = data.get("plugins", {}).get("entries", {})
        if pid in entries:
            del entries[pid]
            modified = True
        allow_list = data.get("plugins", {}).get("allow", [])
        if pid in allow_list:
            data["plugins"]["allow"] = [p for p in allow_list if p != pid]
            modified = True
    if modified:
        with open(cfg_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Config scrubbed for {pid}.")
except Exception as e:
    print(f"! Warning: Patched failed: {e}")
PY
    fi
}

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

# ---------------------------------------------------------
# 流程开始
# ---------------------------------------------------------

# 1. 检测 Python 版本 (使用你的探测逻辑)
if ! PYTHON_BIN="$(find_python)"; then
    echo "ERROR: Python 3.10+ is required but not found."
    exit 1
fi
echo "✓ Found compatible Python: $PYTHON_BIN"

# 2. 检查现有安装
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "Existing ZKE Trading installation detected."
    echo "1) Update / Reinstall (Keep API config)"
    echo "2) Full Reset"
    echo "3) Cancel"
    prompt_tty "Choice: " MENU_CHOICE
    case "$MENU_CHOICE" in
        1) cleanup_existing_plugin ;;
        2) cleanup_existing_plugin; rm -rf "$INSTALL_DIR" ;;
        *) exit 0 ;;
    esac
fi

# 3. 同步代码
echo ""
echo "[3/9] Syncing SDK..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR" && git fetch --all && git reset --hard origin/main
else
    git clone https://github.com/ZKE-Exchange/zke-trading-sdk.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. 环境搭建 (强制使用探测到的高版本 Python)
echo ""
echo "[4/9] Setting up Virtual Env..."
[ -d ".venv" ] && rm -rf .venv
"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed with $(python --version)"

# 5. API 配置
if [ ! -f "config.json" ]; then
    prompt_tty "Spot API Key: " S_KEY
    prompt_tty_secret "Spot Secret: " S_SEC
    prompt_tty "Futures API Key (Enter to reuse): " F_KEY
    [ -z "$F_KEY" ] && F_KEY="$S_KEY" && F_SEC="$S_SEC" || prompt_tty_secret "Futures Secret: " F_SEC
    
    cat <<EOF > config.json
{
  "spot": { "base_url": "https://openapi.zke.com", "api_key": "$S_KEY", "api_secret": "$S_SEC", "recv_window": 5000 },
  "futures": { "base_url": "https://futuresopenapi.zke.com", "api_key": "$F_KEY", "api_secret": "$F_SEC", "recv_window": 5000 },
  "ws": { "url": "wss://ws.zke.com/kline-api/ws" }
}
EOF
fi

# 6. 编译安装
echo ""
echo "[6/9] Building Plugin..."
cd "$INSTALL_DIR/openclaw-plugin"
npm install && npm run build

echo ""
echo "[8/9] Installing..."
# 这里 JSON 已经提前修好了，install 不会报错
openclaw plugins install .
openclaw plugins enable "$PLUGIN_ID"

# 7. 重启
openclaw gateway --force
echo "======================================"
echo "✅ SUCCESS! Run with $PYTHON_BIN"
echo "======================================"

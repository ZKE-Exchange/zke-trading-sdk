#!/bin/bash

set -euo pipefail

echo "======================================"
echo "ZKE OpenClaw Plugin: Full Professional Installer"
echo "======================================"

INSTALL_DIR="$HOME/.zke-trading"
REPO_URL="https://github.com/ZKE-Exchange/zke-trading-sdk.git"
DEFAULT_BRANCH="main"
PLUGIN_ID="zke-trading"

# OpenClaw 默认路径
OPENCLAW_EXT_DIR="$HOME/.openclaw/extensions/$PLUGIN_ID"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

# ---------------------------------------------------------
# 1. 深度清理与死锁修复函数 (保留其他插件)
# ---------------------------------------------------------
cleanup_existing_plugin() {
    echo "Performing surgical cleanup of '$PLUGIN_ID'..."
    
    # 物理清理目录
    rm -rf "$OPENCLAW_EXT_DIR"
    rm -f "$HOME/.openclaw/plugins/$PLUGIN_ID"

    # 物理修复 JSON 配置文件中的死锁条目
    if [ -f "$OPENCLAW_CONFIG" ]; then
        python3 - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
cfg_path = sys.argv[1]
pid = sys.argv[2]
try:
    with open(cfg_path, 'r') as f:
        data = json.load(f)
    
    modified = False
    if "plugins" in data:
        # 仅移除 entries 中属于本项目 ID 的残余，保留其他插件
        entries = data.get("plugins", {}).get("entries", {})
        if pid in entries:
            del entries[pid]
            modified = True
        
        # 仅从 allow 列表中剔除本项目 ID，保留其他所有插件
        allow_list = data.get("plugins", {}).get("allow", [])
        if pid in allow_list:
            data["plugins"]["allow"] = [p for p in allow_list if p != pid]
            modified = True
            
    if modified:
        with open(cfg_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Fixed stale config entries for {pid}. (Other plugins preserved)")
except Exception as e:
    print(f"! Warning: Config patching skipped: {e}")
PY
    fi
}

# ---------------------------------------------------------
# 2. 交互工具
# ---------------------------------------------------------
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
# 3. 检查现有安装
# ---------------------------------------------------------
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "Existing ZKE Trading installation detected."
    echo "1) Update / Reinstall (Keep API config, update code)"
    echo "2) Full Reset (Delete all files and configs, start fresh)"
    echo "3) Cancel"
    echo ""
    prompt_tty "Enter choice [1-3]: " MENU_CHOICE
    case "$MENU_CHOICE" in
        1) cleanup_existing_plugin ;;
        2) 
            cleanup_existing_plugin
            echo "Removing SDK directory: $INSTALL_DIR"
            rm -rf "$INSTALL_DIR"
            ;;
        *) echo "Operation cancelled."; exit 0 ;;
    esac
fi

# ---------------------------------------------------------
# 4. 执行核心步骤
# ---------------------------------------------------------
echo ""
echo "[1/9] Checking dependencies..."
for cmd in git npm openclaw python3; do
    if ! command -v $cmd >/dev/null 2>&1; then echo "ERROR: $cmd is required."; exit 1; fi
done

echo ""
echo "[2/9] Syncing SDK Repository..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR" && git fetch --all && git reset --hard "origin/$DEFAULT_BRANCH"
else
    git clone -b "$DEFAULT_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "[3/9] Setting up Python Environment..."
[ -d ".venv" ] && rm -rf .venv
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt

# ---------------------------------------------------------
# 5. API 配置逻辑 (只有在 config.json 不存在时执行)
# ---------------------------------------------------------
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo ""
    echo "--- ZKE API CONFIGURATION ---"
    prompt_tty "Enter Spot API Key: " SPOT_KEY
    prompt_tty_secret "Enter Spot API Secret: " SPOT_SEC
    prompt_tty "Enter Futures API Key (Enter to reuse Spot): " FUT_KEY
    if [ -z "$FUT_KEY" ]; then
        FUT_KEY="$SPOT_KEY"; FUT_SEC="$SPOT_SEC"
    else
        prompt_tty_secret "Enter Futures API Secret: " FUT_SEC
    fi

    # 生成 config.json
    cat <<EOF > "$INSTALL_DIR/config.json"
{
  "spot": { "base_url": "https://openapi.zke.com", "api_key": "$SPOT_KEY", "api_secret": "$SPOT_SEC", "recv_window": 5000 },
  "futures": { "base_url": "https://futuresopenapi.zke.com", "api_key": "$FUT_KEY", "api_secret": "$FUT_SEC", "recv_window": 5000 },
  "ws": { "url": "wss://ws.zke.com/kline-api/ws" }
}
EOF
    echo "✓ config.json generated."
fi

echo ""
echo "[6/9] Building OpenClaw Plugin..."
cd "$INSTALL_DIR/openclaw-plugin"
npm install
npm run build
echo "✓ Plugin compiled successfully."

echo ""
echo "[7/9] Registering with OpenClaw..."
# 这里之前已经通过 Python 修复了死锁，所以 install 命令不会报错
openclaw plugins install .
openclaw plugins enable "$PLUGIN_ID"

echo ""
echo "[8/9] Injecting runtime permissions..."
# 确保在 allow 列表中 (双重保险)
python3 - "$OPENCLAW_CONFIG" "$PLUGIN_ID" << 'PY'
import json, sys, os
cfg_path = sys.argv[1]
pid = sys.argv[2]
if os.path.exists(cfg_path):
    with open(cfg_path, "r") as f:
        data = json.load(f)
    allow = data.setdefault("plugins", {}).setdefault("allow", [])
    if pid not in allow:
        allow.append(pid)
        with open(cfg_path, "w") as f:
            json.dump(data, f, indent=2)
PY

echo ""
echo "[9/9] Restarting Gateway..."
openclaw gateway --force

echo ""
echo "======================================"
echo "✅ SUCCESS! ZKE Trading Plugin is fully operational."
echo "======================================"
echo "SDK: $INSTALL_DIR"
echo "Plugin: $INSTALL_DIR/openclaw-plugin"
echo "======================================"

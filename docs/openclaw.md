# OpenClaw Integration

The ZKE Trading SDK includes an OpenClaw plugin that allows AI agents to interact with ZKE Exchange directly.

This enables OpenClaw agents to perform tasks such as:

• checking market prices  
• retrieving balances  
• viewing positions  
• creating orders  
• canceling orders  
• retrieving withdrawal history  

---

# Architecture

OpenClaw interacts with the Python SDK through the plugin layer.

```
OpenClaw Agent
     │
     ▼
ZKE OpenClaw Plugin
     │
     ▼
Python SDK
     │
     ▼
ZKE Exchange API
```

The plugin acts as a bridge between OpenClaw tools and the Python trading SDK.

---

# Installation

Install the plugin automatically:

```
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

The installer will:

• build the OpenClaw plugin  
• install it into the OpenClaw extensions directory  
• configure plugin settings  

Installation path:

```
~/.openclaw/extensions/zke-trading
```

---

# Verify Installation

Check installed plugins:

```
openclaw plugins list
```

Expected output:

```
ZKE Trading
Status: loaded
Tools: zke_get_spot_ticker ...
```

---

# Required OpenClaw Permission

By default OpenClaw restricts external tools.

You must enable full tool permissions.

Open:

```
~/.openclaw/openclaw.json
```

Find:

```
tools.profile
```

Set:

```json
"tools": {
  "profile": "full"
}
```

Restart OpenClaw afterwards.

---

# Example Prompts

Once installed, you can ask OpenClaw:

```
Check BTC price on ZKE
Show my USDT balance on ZKE
Show my futures positions on ZKE
Place a BTC limit order on ZKE
Cancel my BTC order
Withdraw 20 USDTBSC
```

The AI agent will automatically call the corresponding plugin tools.

---

# Available Tools

The plugin exposes the following tools:

```
zke_get_spot_ticker
zke_get_spot_depth
zke_get_spot_balance
zke_get_spot_open_orders
zke_get_spot_my_trades
zke_create_spot_order
zke_cancel_spot_order

zke_get_futures_ticker
zke_get_futures_index
zke_get_futures_balance
zke_get_futures_positions
zke_get_futures_open_orders
zke_get_futures_my_trades
zke_get_futures_order_history
zke_get_futures_profit_history
zke_create_futures_order
zke_cancel_futures_order

zke_get_withdraw_history
zke_create_withdraw
```

---

# Troubleshooting

## Plugin installed but tools unavailable

Ensure the OpenClaw tool permission is enabled:

```
tools.profile = full
```

Restart OpenClaw after updating the configuration.

---

## Verify Python SDK

You can test the SDK directly:

```
cd ~/.zke-trading
source .venv/bin/activate
python main.py ticker BTCUSDT
```

---

# Security Notes

This system runs locally.

Users are responsible for:

• API key security  
• trading decisions  
• withdrawal confirmations

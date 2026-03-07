# ZKE Trading SDK

Official **ZKE Exchange Trading SDK** with AI agent support.

This repository provides a complete developer toolkit for interacting with ZKE Exchange, including:

- Python Trading SDK
- WebSocket market data client
- CLI trading tools
- Local MCP Server for AI agents
- OpenClaw plugin integration
- Automated installation scripts

This project enables developers and AI agents to safely interact with **ZKE Spot and Futures APIs**.

---

# Features

• Spot market data  
• Futures market data  
• Spot trading  
• Futures trading  
• Wallet balances  
• Order management  
• Withdrawal history  

Advanced integrations:

• Python applications  
• AI agents via MCP  
• OpenClaw plugin tools  
• WebSocket real-time data streams  

---

# Quick Start

Install the SDK and local MCP server:

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install.sh | bash
```

Install the OpenClaw plugin:

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

---

# Repository Structure

```
zke-trading-sdk
│
├── main.py
├── mcp_server.py
├── config.example.json
├── requirements.txt
│
├── install.sh
├── install_openclaw_plugin.sh
│
├── tools
│   ├── account_service.py
│   ├── common.py
│   ├── errors.py
│   ├── field_mapper.py
│   ├── formatters.py
│   ├── futures_account_service.py
│   ├── futures_order_service.py
│   ├── futures_private.py
│   ├── futures_public.py
│   ├── futures_service.py
│   ├── margin_order_service.py
│   ├── margin_private.py
│   ├── market_service.py
│   ├── order_service.py
│   ├── spot_private.py
│   ├── spot_public.py
│   ├── symbol_utils.py
│   ├── withdraw_service.py
│   ├── ws_client.py
│   ├── ws_parser.py
│   └── ws_service.py
│
├── openclaw-plugin
│   ├── src
│   │   ├── index.ts
│   │   ├── python.ts
│   │   └── types.ts
│   │
│   ├── skills
│   │   └── zke_trading
│   │       └── SKILL.md
│   │
│   ├── package.json
│   ├── openclaw.plugin.json
│   └── tsconfig.json
│
├── docs
│   ├── cli.md
│   ├── openclaw.md
│   └── examples
│       ├── cli_examples.md
│
└── README.md
```

---

# Runtime Modes

The SDK supports three runtime modes.

### Python SDK

Directly integrate with Python applications.

### MCP Server

Expose trading tools to AI agents via **Model Context Protocol (MCP)**.

### OpenClaw Plugin

Expose trading tools directly inside **OpenClaw AI agents**.

---

# Python SDK

Install dependencies:

```bash
pip install -r requirements.txt
```

Create configuration:

```bash
cp config.example.json config.json
```

Example configuration:

```json
{
  "spot": {
    "base_url": "https://openapi.zke.com",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET"
  },
  "futures": {
    "base_url": "https://openapi.zke.com",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET"
  }
}
```

Create API keys:

https://www.zke.com/en_US/personal/apiManagement

---

# CLI Usage

The SDK includes a CLI interface.

Examples:

```bash
python main.py ticker BTCUSDT
python main.py depth BTCUSDT
python main.py balance
python main.py positions
```

Example output:

```
{
  "high": "68539.78",
  "low": "67446.38",
  "last": "67621.67"
}
```

---

# WebSocket Support

The SDK includes real-time WebSocket support.

Modules:

```
tools/ws_client.py
tools/ws_parser.py
tools/ws_service.py
```

These allow subscriptions to real-time market streams such as:

• ticker updates  
• orderbook depth  
• trade streams  

Example usage:

```python
from tools.ws_service import WSService

ws = WSService()

ws.subscribe_ticker("BTCUSDT")

ws.run()
```

Example output:

```
{
  "symbol": "BTCUSDT",
  "price": "67621.67",
  "time": 1772908031000
}
```

---

# Local MCP Server

Run the MCP server:

```bash
python mcp_server.py
```

This exposes trading functionality to AI agents through MCP tools.

Supported MCP tools:

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

# OpenClaw Plugin

Install automatically:

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

Verify installation:

```bash
openclaw plugins list
```

Expected output:

```
ZKE Trading
Status: loaded
Tools: zke_get_spot_ticker ...
```

---

# Important OpenClaw Setting

OpenClaw may restrict external tools by default.

Enable full tool permissions:

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

Restart OpenClaw after updating.

---

# Example OpenClaw Prompts

```
Check BTC price on ZKE
Show my USDT balance on ZKE
Show my futures positions on ZKE
Place a BTC limit order on ZKE
Cancel my BTC order on ZKE
```

---

# Architecture

OpenClaw integration:

```
AI Agent
   │
   ▼
OpenClaw Plugin
   │
   ▼
Python SDK
   │
   ├─ REST API
   └─ WebSocket
```

MCP integration:

```
AI Agent
   │
   ▼
MCP Server
   │
   ▼
Python SDK
   │
   ├─ REST API
   └─ WebSocket
```

---

# Security Notice

Never expose your API keys publicly.

Recommended API permissions:

• Read  
• Trade  

Disable withdrawal permissions unless necessary.

---

# ZKE Exchange

Official Website

https://www.zke.com

API Documentation

https://help.zke.com/api_en/

---

# License

MIT License

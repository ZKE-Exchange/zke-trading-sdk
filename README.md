# ZKE Trading SDK

Official **ZKE Exchange Trading SDK** with AI agent support.

This repository provides a complete developer toolkit for interacting with ZKE Exchange.

It includes:

• Python Trading SDK  
• WebSocket market data client  
• CLI trading tools  
• Local MCP Server for AI agents  
• OpenClaw plugin integration  
• Automated installation scripts  

The SDK enables developers and AI agents to interact with **ZKE Spot and Futures APIs safely and efficiently.**

---

# Features

## Spot

• Market data  
• Trading  
• Wallet balances  
• Order management  
• Asset transfers  
• Withdrawal history  

## Futures

• Market data  
• Position management  
• Order management  
• Conditional orders  
• Margin adjustment  
• Leverage control  

## Advanced Integrations

• Python applications  
• AI agents via MCP  
• OpenClaw plugin tools  
• WebSocket real-time market streams  

---

# Quick Start

Install SDK

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install.sh | bash
```

Install OpenClaw plugin

```bash
bash <(curl -s "https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh?v=$RANDOM")
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
│   ├── transfer_service.py
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
│
└── README.md
```

---

# Configuration

Create configuration file

```bash
cp config.example.json config.json
```

Example configuration

```json
{
  "spot": {
    "base_url": "https://openapi.zke.com",
    "api_key": "YOUR_SPOT_API_KEY",
    "api_secret": "YOUR_SPOT_API_SECRET",
    "recv_window": 5000
  },
  "futures": {
    "base_url": "https://futuresopenapi.zke.com",
    "api_key": "YOUR_FUTURES_API_KEY",
    "api_secret": "YOUR_FUTURES_API_SECRET",
    "recv_window": 5000
  },
  "ws": {
    "url": "wss://ws.zke.com/kline-api/ws"
  }
}
```

Create API keys

https://www.zke.com/en_US/personal/apiManagement

Recommended permissions

• Read  
• Trade  

Disable withdrawal permissions unless required.

---

# CLI Usage

Examples

```bash
python main.py ticker BTCUSDT
python main.py depth BTCUSDT
python main.py balance
python main.py positions
```

Example output

```
{
  "high": "68539.78",
  "low": "67446.38",
  "last": "67621.67"
}
```

---

# Python SDK Example

## Spot Example

```python
from tools.spot_private import SpotPrivateApi
from tools.zke_client import ZKEClient

client = ZKEClient(
    base_url="https://openapi.zke.com",
    api_key="YOUR_KEY",
    api_secret="YOUR_SECRET"
)

spot = SpotPrivateApi(client)

balance = spot.account()

print(balance)
```

---

## Futures Example

```python
from tools.futures_private import FuturesPrivateApi
from tools.zke_client import ZKEClient

client = ZKEClient(
    base_url="https://futuresopenapi.zke.com",
    api_key="YOUR_KEY",
    api_secret="YOUR_SECRET"
)

futures = FuturesPrivateApi(client)

positions = futures.account()

print(positions)
```

---

# WebSocket Support

Modules

```
tools/ws_client.py
tools/ws_parser.py
tools/ws_service.py
```

Supported streams

• ticker  
• orderbook depth  
• trade stream  
• kline  

Example

```python
from tools.ws_service import WSService

ws = WSService()

ws.subscribe_ticker("BTCUSDT")

ws.run()
```

---

# MCP Server

Run MCP server

```bash
python mcp_server.py
```

---

# MCP Tools

## Spot

```
zke_get_spot_ticker
zke_get_spot_depth
zke_get_spot_klines
zke_get_spot_account
zke_get_spot_nonzero_balances
zke_get_spot_balance
zke_get_spot_account_by_type
zke_get_spot_open_orders
zke_get_spot_my_trades
zke_get_spot_my_trades_v3
zke_get_spot_history_orders
zke_create_spot_order
zke_cancel_spot_order
```

## Asset

```
zke_transfer_spot_to_futures
zke_transfer_futures_to_spot
zke_get_transfer_history
zke_create_withdraw
zke_get_withdraw_history
```

## Margin

```
zke_create_margin_order
zke_get_margin_order
zke_cancel_margin_order
zke_get_margin_open_orders
zke_get_margin_my_trades
```

## Futures

```
zke_get_futures_ticker
zke_get_futures_index
zke_get_futures_depth
zke_get_futures_klines
zke_get_futures_balance
zke_get_futures_positions
zke_get_futures_order
zke_get_futures_open_orders
zke_get_futures_my_trades
zke_get_futures_order_history
zke_get_futures_profit_history
zke_get_futures_transaction_history
zke_create_futures_order
zke_create_futures_condition_order
zke_cancel_futures_order
zke_cancel_all_futures_orders
zke_edit_futures_position_mode
zke_edit_futures_margin_mode
zke_adjust_futures_position_margin
zke_edit_futures_leverage
```

---

# OpenClaw Plugin

Install plugin

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

Verify

```bash
openclaw plugins list
```

Expected

```
ZKE Trading
Status: loaded
```

---

# Important OpenClaw Setting

Edit

```
~/.openclaw/openclaw.json
```

Set

```json
"tools": {
  "profile": "full"
}
```

Restart OpenClaw after updating.

---

# Architecture

## MCP

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

## OpenClaw

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

---

# Security Notice

Never expose your API keys publicly.

Recommended permissions

• Read  
• Trade  

Disable withdrawal permission unless necessary.

---

# ZKE Exchange

Official Website

https://www.zke.com

API Documentation

https://help.zke.com/api_en/

---

# License

MIT License

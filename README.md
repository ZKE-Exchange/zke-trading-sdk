# ZKE Trading SDK

Official Python SDK, MCP Server, and OpenClaw Plugin for ZKE Exchange.

ZKE Trading SDK provides a unified toolkit for interacting with the ZKE Exchange API.

Developers and AI agents can access ZKE trading capabilities using:

- Python SDK
- Local MCP server
- OpenClaw AI plugin
- WebSocket market streams

---

# Features

- Spot market data
- Spot trading
- Futures market data
- Futures trading
- Wallet operations
- Withdraw API
- Python CLI interface
- Local MCP server for AI agents
- OpenClaw plugin integration
- WebSocket real-time market data

---

# Architecture

```
AI Agent / OpenClaw
        │
        │ tools
        ▼
ZKE OpenClaw Plugin
        │
        │ CLI / SDK
        ▼
Python Trading SDK
(main.py + tools/)
        │
        │ REST / WS API
        ▼
ZKE Exchange
```

---

# Repository Structure

```
zke-trading-sdk/

├── docs/
│   Additional documentation
│
├── examples/
│   Example usage files
│
├── openclaw-plugin/
│   OpenClaw plugin implementation
│
├── tools/
│   Core Python API wrappers and trading logic
│
├── main.py
│   Python CLI entry point
│
├── mcp_server.py
│   Local MCP server for AI agents
│
├── install.sh
│   One-click installer for local MCP environment
│
├── install_openclaw_plugin.sh
│   One-click OpenClaw plugin installer
│
├── config.example.json
│   Example configuration file
│
├── requirements.txt
│   Python dependencies
│
└── README.md
```

---

# Quick Start

## Option 1 — Local MCP Server (Recommended)

Install the SDK and MCP server with one command:

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install.sh | bash
```

This installer will:

- install Python environment
- install SDK dependencies
- create config.json
- start the local MCP server

Start MCP manually:

```bash
python mcp_server.py
```

---

## Option 2 — OpenClaw Plugin

Install the OpenClaw plugin:

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

This will:

- install SDK
- build the OpenClaw plugin
- install plugin into OpenClaw
- enable ZKE trading tools

---

# OpenClaw Configuration

OpenClaw must allow full tool access.

Edit:

```
~/.openclaw/openclaw.json
```

Ensure:

```json
{
  "tools": {
    "profile": "full"
  }
}
```

Restart OpenClaw after editing.

---

# Python SDK Installation

Clone repository:

```bash
git clone https://github.com/ZKE-Exchange/zke-trading-sdk
cd zke-trading-sdk
```

Create environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create config:

```bash
cp config.example.json config.json
```

Edit API credentials.

Example:

```json
{
  "spot": {
    "base_url": "https://openapi.zke.com",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET"
  }
}
```

---

# Python CLI Usage

Get ticker:

```bash
python main.py ticker BTCUSDT
```

Example response:

```json
{
  "last": "67621.67",
  "buy": 67621.33,
  "sell": 67622.02
}
```

Get order book:

```bash
python main.py depth BTCUSDT
```

---

# WebSocket Market Data

ZKE supports WebSocket streams for real-time market updates.

Typical use cases:

- real-time price updates
- order book updates
- trading bots
- AI agents with streaming data

Example architecture:

```
ZKE WebSocket
      │
      ▼
Python SDK
      │
      ▼
Trading bot / AI agent
```

WS streams provide lower latency than REST polling.

---

# Local MCP Server

Start the MCP server:

```bash
python mcp_server.py
```

The MCP server exposes tools for AI agents.

Example tools:

```
zke_get_spot_ticker
zke_get_spot_depth
zke_get_spot_balance
zke_get_futures_positions
zke_create_spot_order
zke_create_withdraw
```

These tools allow AI systems to trade on ZKE.

---

# OpenClaw Example Commands

Once the plugin is installed:

```
Check BTC price on ZKE
Show my USDT balance on ZKE
Show my futures positions on ZKE
Place a BTC limit order
Withdraw 20 USDT on ZKE
```

The AI assistant will automatically call ZKE trading tools.

---

# MCP Tool List

## Spot

```
zke_get_spot_ticker
zke_get_spot_depth
zke_get_spot_balance
zke_get_spot_open_orders
zke_get_spot_my_trades
zke_create_spot_order
zke_cancel_spot_order
```

## Futures

```
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
```

## Wallet

```
zke_get_withdraw_history
zke_create_withdraw
```

---

# Security

Never expose your API secret.

Recommended permissions:

- Read
- Trade

Disable withdraw permission unless required.

---

# License

MIT License

---

# About ZKE Exchange

ZKE Exchange provides a secure and high-performance cryptocurrency trading platform.

Official website:

https://www.zke.com

---

# Support

For issues or feature requests, please open a GitHub issue.

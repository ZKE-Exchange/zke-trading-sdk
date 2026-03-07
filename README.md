# ZKE Trading SDK

Official **ZKE Exchange Trading SDK** for developers and AI agents.

This project provides:

- Python trading SDK
- Local MCP Server for AI agents
- OpenClaw plugin integration
- CLI trading tools
- Automated installation scripts

It allows AI agents and developers to interact with **ZKE Exchange Spot and Futures APIs** safely and easily.

---

# Features

• Spot market data  
• Futures market data  
• Spot trading  
• Futures trading  
• Wallet balance  
• Order management  
• Withdraw history  

Integration support:

• Python applications  
• AI agents via MCP  
• OpenClaw plugin tools  

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
├── tools/
│
├── openclaw-plugin/
│   ├── src/
│   ├── skills/
│   │   └── zke_trading/
│   │       └── SKILL.md
│   ├── package.json
│   └── openclaw.plugin.json
│
└── docs/
```

---

# Python SDK

You can use the SDK directly.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create configuration:

```
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

Create API keys here:

https://www.zke.com/en_US/personal/apiManagement

---

# CLI Usage

The SDK includes a CLI interface.

Example commands:

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

# Local MCP Server

The SDK can run as a **Model Context Protocol (MCP) server**.

Start MCP server manually:

```bash
python mcp_server.py
```

This allows AI agents to access trading tools through MCP.

Supported tools include:

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

This repository includes a fully functional **OpenClaw plugin**.

Install automatically:

```bash
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

Verify installation:

```bash
openclaw plugins list
```

You should see:

```
ZKE Trading
Status: loaded
Tools: zke_get_spot_ticker ...
```

---

# Important OpenClaw Setting

OpenClaw may block external tools by default.

Enable full tool permissions:

Open:

```
~/.openclaw/openclaw.json
```

Find:

```
tools.profile
```

Change to:

```json
"tools": {
  "profile": "full"
}
```

Restart OpenClaw after updating.

---

# OpenClaw Example Prompts

Once installed you can ask:

```
Check BTC price on ZKE
Show my USDT balance on ZKE
Show my futures positions on ZKE
Place a BTC limit order on ZKE
```

The AI agent will call the plugin tools automatically.

---

# Architecture

The system architecture:

```
AI Agent
   │
   ▼
OpenClaw Plugin
   │
   ▼
Python SDK
   │
   ▼
ZKE Exchange API
```

Alternatively AI agents can use the **MCP server**:

```
AI Agent
   │
   ▼
MCP Server
   │
   ▼
Python SDK
   │
   ▼
ZKE Exchange API
```

---

# Security Notice

Never expose your API keys publicly.

Recommended permissions:

• Read  
• Trade  

Disable withdrawal permissions unless necessary.

---

# License

MIT License

---

# ZKE Exchange

Official website:

https://www.zke.com

API documentation:

https://openapi.zke.com

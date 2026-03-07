ZKE Trading SDK

Official open source trading toolkit for ZKE Exchange.
Run `python main.py ticker BTCUSDT` to get the price.
This project provides a complete Python SDK + CLI + MCP server for interacting with the ZKE Exchange API, including:
	•	Spot trading
	•	Futures trading
	•	Margin trading
	•	Withdraw API
	•	WebSocket market data
	•	AI agent integration (MCP / OpenClaw)

The SDK can be used by:
	•	traders
	•	developers
	•	quantitative trading systems
	•	AI agents

⸻

Features

Trading APIs
	•	Spot trading
	•	Futures trading
	•	Margin trading
	•	Withdraw API
	•	Account balance query
	•	Order management

Market Data
	•	REST market API
	•	WebSocket real-time market data
	•	ticker
	•	depth
	•	trades
	•	kline streams

Developer Tools
	•	Python SDK
	•	CLI trading tool
	•	MCP server for AI tools
	•	OpenClaw skill support

⸻

📦 Project Structure
zke-trading-sdk/

├── main.py                 # CLI trading tool
├── mcp_server.py           # MCP server for AI agents
├── config.example.json     # example configuration
├── requirements.txt
│
├── tools/                  # core SDK implementation
│   ├── account_service.py
│   ├── common.py
│   ├── errors.py
│   ├── field_mapper.py
│   ├── formatters.py
│   │
│   ├── spot_public.py
│   ├── spot_private.py
│   │
│   ├── futures_public.py
│   ├── futures_private.py
│   ├── futures_account_service.py
│   ├── futures_order_service.py
│   ├── futures_service.py
│   │
│   ├── margin_private.py
│   ├── margin_order_service.py
│   │
│   ├── market_service.py
│   ├── order_service.py
│   ├── withdraw_service.py
│   │
│   ├── symbol_utils.py
│   │
│   ├── ws_client.py
│   ├── ws_parser.py
│   ├── ws_service.py
│   │
│   └── zke_client.py
│
├── openclaw/               # OpenClaw skill plugin
│   ├── openclaw.plugin.json
│   └── skills/
│       └── zke_trading/
│           └── SKILL.md
│
├── docs/                   # project documentation
└── examples/               # usage examples

Installation

Clone the repository
git clone https://github.com/zke-exchange/zke-trading-sdk.git
cd zke-trading-sdk

Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

Install dependencies
pip install -r requirements.txt

Configuration

Copy the example configuration file
cp config.example.json config.json

Edit the file and add your API credentials.

Example:

{
  "spot": {
    "base_url": "https://openapi.zke.com",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET",
    "recv_window": 5000
  },
  "futures": {
    "base_url": "https://futuresopenapi.zke.com",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET",
    "recv_window": 5000
  },
  "ws": {
    "url": "wss://ws.zke.com/kline-api/ws"
  }
}

CLI Usage

The SDK includes a simple CLI interface.

Check API connectivity
python main.py ping

Get market ticker
python main.py ticker BTCUSDT

Create spot order
python main.py create-order BTCUSDT BUY LIMIT 0.001 60000

Cancel order
python main.py cancel-order BTCUSDT ORDER_ID

Query account balance
python main.py account

WebSocket Market Data
The SDK supports real-time market data via WebSocket.

Ticker stream
python main.py ws-ticker BTCUSDT

Depth stream
python main.py ws-depth BTCUSDT

Trades stream
python main.py ws-trades BTCUSDT

Kline stream
python main.py ws-kline BTCUSDT 1min

Supported intervals:
1min
5min
15min
30min
60min
1day
1week
1month

MCP Server (AI Agent Integration)
This project includes a Model Context Protocol (MCP) server that exposes trading tools for AI agents.

Start MCP server
python mcp_server.py

Available tools include:
	•	get_spot_balance
	•	get_spot_ticker
	•	create_spot_order
	•	cancel_spot_order
	•	get_futures_positions
	•	create_futures_order
	•	create_withdraw
	•	get_withdraw_history

These tools can be used by AI agents or automation frameworks.

OpenClaw Skill Integration

This repository includes a ZKE Trading Skill for OpenClaw.

Install the plugin by copying the openclaw directory into:

~/.openclaw/plugins/

Restart OpenClaw and the ZKE trading tools will become available to the AI agent.

Example prompts:
Check BTC price on ZKE
Show my USDT balance
Place BTC limit order at 60000
Withdraw 20 USDT

Supported Markets

The SDK currently supports:
	•	Spot Trading
	•	Futures Trading
	•	Margin Trading
	•	Withdraw API
	•	REST Market Data
	•	WebSocket Market Data

⸻

🔒 Security Notes

Never expose your API keys publicly.

Recommended settings:
	•	Enable IP whitelist
	•	Disable withdraw permission if not required
	•	Use separate keys for trading and withdrawals


📄 License

MIT License


ZKE Exchange

Official website

https://zke.com

Contributing

Contributions are welcome.

If you find a bug or want to suggest improvements, please open an issue or submit a pull request.

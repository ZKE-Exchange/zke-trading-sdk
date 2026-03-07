# OpenClaw Integration

This project can be used together with OpenClaw locally.

The ZKE Trading SDK exposes trading capabilities through a local MCP server.

## Included Files

openclaw/
├── openclaw.plugin.json
└── skills/
    └── zke_trading/
        └── SKILL.md

These files define the OpenClaw plugin and skill description.

## Local Setup

Clone the repository

git clone https://github.com/ZKE-Exchange/zke-trading-sdk.git
cd zke-trading-sdk

Create Python virtual environment

python3 -m venv .venv
source .venv/bin/activate

Install dependencies

pip install -r requirements.txt

Configure API keys

cp config.example.json config.json

Start the MCP server

python mcp_server.py

Install the OpenClaw plugin

Copy the openclaw directory into

~/.openclaw/plugins/zke-trading/

Restart OpenClaw.

## Example prompts

Check BTC price on ZKE
Show my USDT balance
Show my futures positions
Place a BTC limit order
Withdraw 20 USDTBSC

## Notes

This project runs completely locally.

Users remain responsible for:

API key security
trading decisions
withdraw confirmations

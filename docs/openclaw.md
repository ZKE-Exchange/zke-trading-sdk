OpenClaw Integration

This project can be used together with OpenClaw locally.

The ZKE Trading SDK exposes trading capabilities through a local MCP server, which can then be used by OpenClaw as a skill.

⸻

Included Files

The repository contains the following OpenClaw integration files:

openclaw/
├── openclaw.plugin.json
└── skills/
  └── zke_trading/
    └── SKILL.md

These files define the OpenClaw plugin and skill description.

⸻

Local Setup

1. Clone the repository

git clone https://github.com/ZKE-Exchange/zke-trading-sdk.git
cd zke-trading-sdk

⸻

2. Create Python virtual environment

python3 -m venv .venv
source .venv/bin/activate

⸻

3. Install dependencies

pip install -r requirements.txt

⸻

4. Configure API keys

Copy the example configuration file:

cp config.example.json config.json

Then edit config.json and insert your API keys.

⸻

5. Start the MCP server

python mcp_server.py

This server exposes trading tools to OpenClaw.

⸻

6. Install the OpenClaw plugin

Copy the openclaw directory into your OpenClaw plugins folder.

Example:

~/.openclaw/plugins/zke-trading/

Restart OpenClaw after copying.

⸻

Result

Once installed, OpenClaw can use the ZKE Trading skill.

Example prompts:

Check BTC price on ZKE
Show my USDT balance
Show my futures positions
Place a BTC limit order
Withdraw 20 USDTBSC

⸻

Notes

This project runs completely locally.

The repository does not provide any hosted trading service.

Users remain responsible for:

• API key security
• trading decisions
• withdraw confirmations

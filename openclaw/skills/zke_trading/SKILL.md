---
name: zke_trading
description: Use ZKE Exchange trading tools for spot, futures, margin, withdrawals and market data through the local MCP server.
---

# ZKE Trading Skill

This skill helps the agent interact with the ZKE Exchange trading toolkit.

The toolkit supports:

- Spot market data
- Spot trading
- Futures market data
- Futures trading
- Margin trading
- Withdraw history
- Withdraw requests
- WebSocket market streams

This skill is intended for local use with the ZKE Trading SDK MCP server.

## Requirements

Before using this skill, the user should:

1. Install the ZKE Trading SDK locally
2. Configure API keys in `config.json`
3. Start the local MCP server:

```bash
python mcp_server.py

# Changelog

All notable changes to this project will be documented in this file.

---

# v1.0.0

Initial public release of the ZKE Trading SDK.

## Added

### Python SDK
- Spot trading API
- Futures trading API
- Margin trading API
- Withdraw API
- Account and order management

### Market Data
- Spot market endpoints
- Futures market endpoints
- WebSocket market streaming
  - ticker
  - depth
  - trades
  - kline

### CLI Interface
- Command line trading client (`main.py`)
- Spot market commands
- Futures commands
- Account queries
- Withdraw operations
- WebSocket streaming commands

### AI Integration
- Local MCP server (`mcp_server.py`)
- MCP tools for trading operations

### OpenClaw Integration
- OpenClaw plugin
- ZKE trading skill
- Automated installation script

### Installation
- `install.sh` for local SDK + MCP setup
- `install_openclaw_plugin.sh` for OpenClaw plugin installation

### Documentation
- README
- CLI documentation
- OpenClaw integration guide
- CLI examples

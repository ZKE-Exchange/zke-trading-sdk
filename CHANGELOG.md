# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning.

---

# v1.0.0

Initial public release of the **ZKE Trading SDK**.

This release introduces the official developer toolkit for interacting with ZKE Exchange Spot and Futures APIs, including Python SDK support, AI agent integrations, CLI tools, and WebSocket market streams.

---

## Added

### Python SDK

Complete Python SDK for interacting with ZKE APIs.

Spot API

- Account information
- Spot trading
- Order management
- Open orders query
- Trade history
- Historical orders (v3)
- Asset transfers
- Withdrawal requests
- Withdrawal history

Futures API

- Futures account information
- Position information
- Futures trading
- Conditional orders
- Order history
- Profit history
- Transaction history
- Cancel order
- Cancel all orders
- Adjust position margin
- Modify leverage
- Modify margin mode
- Modify position mode

Margin API

- Margin trading support
- Margin order management
- Margin open orders
- Margin trade history

---

### Market Data

Spot market endpoints

- Ticker
- Orderbook depth
- Recent trades
- Kline data

Futures market endpoints

- Ticker
- Index price
- Orderbook depth
- Kline data

WebSocket streaming

- ticker stream
- orderbook depth stream
- trade stream
- kline stream

---

### CLI Interface

Command line trading client (`main.py`)

Supported commands

- Spot market queries
- Futures market queries
- Account balances
- Position queries
- Order queries
- Trade history
- WebSocket streaming

---

### AI Integration

Local MCP server (`mcp_server.py`)

Available MCP tools include

Spot

- spot ticker
- spot depth
- spot account
- spot balances
- spot open orders
- spot trade history
- create spot order
- cancel spot order

Asset

- transfer between accounts
- transfer history
- withdraw
- withdraw history

Futures

- futures account
- futures positions
- futures open orders
- futures order history
- futures trade history
- futures profit history
- create futures order
- cancel futures order
- conditional orders
- leverage modification
- margin adjustment

---

### OpenClaw Integration

OpenClaw plugin

Features

- ZKE trading skill
- Direct AI trading actions
- Automated installation script
- Local MCP bridge

---

### WebSocket Client

Real-time market data client

Modules

- ws_client
- ws_parser
- ws_service

Supported channels

- ticker
- depth
- trade
- kline

---

### Installation

Automated installation scripts

`install.sh`

- Install Python SDK
- Install dependencies
- Setup MCP server environment

`install_openclaw_plugin.sh`

- Install OpenClaw plugin
- Register ZKE trading skill

---

### Documentation

Documentation included

- README
- CLI documentation
- OpenClaw integration guide
- CLI examples

---

## Security

Security best practices documented

- API key permission guidance
- Withdrawal permission warnings
- Recommended access levels

---

## License

MIT License

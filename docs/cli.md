# ZKE Trading CLI

The ZKE Trading SDK includes a command line interface through `main.py`.

This CLI allows you to interact with ZKE Exchange directly from the terminal.

---

# Basic Usage

```
python main.py <command> [arguments]
```

Example:

```
python main.py ticker BTCUSDT
```

---

# Spot Market Commands

Check API connectivity

```
python main.py ping
```

Get ticker price

```
python main.py ticker BTCUSDT
```

Get orderbook depth

```
python main.py depth BTCUSDT 20
```

Parameters

| Parameter | Description |
|----------|-------------|
| symbol | trading pair |
| depth | number of orderbook levels |

Example

```
python main.py depth BTCUSDT 20
```

Get recent trades

```
python main.py trades BTCUSDT 20
```

Get Kline data

```
python main.py klines BTCUSDT 1day
```

Supported intervals

```
1min
5min
15min
30min
1hour
4hour
1day
1week
1month
```

---

# Account Commands

Get full account information

```
python main.py account
```

Get asset balance

```
python main.py balance USDT
```

Show non-zero balances

```
python main.py balances
```

---

# Spot Order Commands

Get open orders

```
python main.py open-orders BTCUSDT
```

Create order

```
python main.py create-order BTCUSDT BUY LIMIT 0.001 10000
```

Parameters

| Parameter | Description |
|----------|-------------|
| symbol | trading pair |
| side | BUY / SELL |
| type | LIMIT / MARKET |
| volume | order amount |
| price | order price |

Example

```
python main.py create-order BTCUSDT BUY LIMIT 0.001 10000
```

Cancel order

```
python main.py cancel-order BTCUSDT ORDER_ID
```

---

# Asset Transfer Commands

Transfer assets between accounts

```
python main.py transfer USDT 10 EXCHANGE FUTURE
```

Parameters

| Parameter | Description |
|----------|-------------|
| coin | asset symbol |
| amount | transfer amount |
| from | source account |
| to | destination account |

Example

```
python main.py transfer USDT 10 EXCHANGE FUTURE
```

Get transfer history

```
python main.py transfer-history
```

---

# Withdraw Commands

Create withdraw request

```
python main.py withdraw USDT BSC 0xYourAddress 20
```

Parameters

| Parameter | Description |
|----------|-------------|
| coin | asset symbol |
| network | chain name |
| address | withdrawal address |
| amount | withdrawal amount |

Example

```
python main.py withdraw USDT BSC 0xabc123... 20
```

Get withdraw history

```
python main.py withdraw-history
```

---

# Futures Commands

Check futures API

```
python main.py futures-ping
```

Get futures ticker

```
python main.py futures-ticker E-BTC-USDT
```

Get futures positions

```
python main.py futures-positions
```

Get futures open orders

```
python main.py futures-open-orders
```

Get futures trades

```
python main.py futures-my-trades E-BTC-USDT
```

Get futures order history

```
python main.py futures-order-history E-BTC-USDT
```

Get futures profit history

```
python main.py futures-profit-history E-BTC-USDT
```

---

# WebSocket Commands

The CLI also supports WebSocket streaming for real-time market data.

Subscribe to ticker stream

```
python main.py ws-ticker BTCUSDT 30
```

Subscribe to orderbook depth

```
python main.py ws-depth BTCUSDT step0 30
```

Subscribe to kline stream

```
python main.py ws-kline BTCUSDT 1min 30
```

Subscribe to trades stream

```
python main.py ws-trades BTCUSDT 30
```

Parameters

| Parameter | Description |
|----------|-------------|
| symbol | trading pair |
| duration | streaming duration in seconds |

Example

```
python main.py ws-ticker BTCUSDT 30
```

Example output

```
{
  "symbol": "BTCUSDT",
  "price": "67621.67",
  "time": 1772908031000
}
```

---

# Symbol Formats

Spot symbols

```
BTCUSDT
ETHUSDT
SOLUSDT
```

Futures symbols

```
E-BTC-USDT
E-ETH-USDT
E-SOL-USDT
```

---

# Notes

• WebSocket commands run for the specified duration  
• CLI output is returned as JSON  
• API keys must be configured in `config.json`

---

# Related Commands

Run MCP server

```
python mcp_server.py
```

Install OpenClaw plugin

```
curl -s https://raw.githubusercontent.com/ZKE-Exchange/zke-trading-sdk/main/install_openclaw_plugin.sh | bash
```

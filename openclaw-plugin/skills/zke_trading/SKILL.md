---
name: zke_trading
description: Use ZKE Exchange local trading tools for spot, futures, balances, positions, transfers, withdrawals and market data.
---

# ZKE Trading

## 1. Core Rule (Highest Priority)
When the user asks about **ZKE Exchange** (prices, balances, positions, orders, transfers, etc.), **ALWAYS** use the local ZKE plugin tools first. 
Do **NOT** use web search, CoinGecko, CoinMarketCap, or generic crypto knowledge unless the user specifically asks for external data.

## 2. Symbol Format Guidelines (CRITICAL)
ZKE Exchange requires very specific symbol formats depending on the endpoint. You must format the symbol correctly before calling the tools:
* **Spot & Margin:** Use base+quote without separators. 
    * *Example:* `BTCUSDT`, `ETHUSDT`
* **Futures (Ticker, Depth, Orders, Positions):** Prepend `E-` and use hyphens. 
    * *Example:* `E-BTC-USDT`, `E-ETH-USDT`
* **Futures Transaction History:** Use hyphens without the prefix. 
    * *Example:* `BTC-USDT`

## 3. Parameter Quirks & Best Practices
* **Timestamps:** When an endpoint (like futures transaction history) requires `begin_time` or `end_time`, you MUST use **13-digit millisecond timestamps** (e.g., `1740787200000`). Do not use `YYYY-MM-DD` strings.
* **Transfer History:** Do not call transfer history with empty parameters. Always try to provide `from_account` and `to_account`. Valid account types are `EXCHANGE` (Spot) and `FUTURE`.
* **Tool Parameters:** Rely on the explicit `inputSchema` provided by each tool to determine required fields (e.g., only provide `price` if `order_type` is `LIMIT`).

## 4. Capabilities Summary
You have tools for:
* **Spot/Margin:** Querying tickers, depth, balances, open orders, trade history, and creating/canceling orders.
* **Futures:** Querying index prices, account balances, active positions, adjusting leverage/margin modes, and creating/canceling orders (including conditional orders).
* **Wallet:** Executing and querying internal transfers (Spot <-> Futures) and withdrawals.

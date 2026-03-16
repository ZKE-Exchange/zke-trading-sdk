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
* **Order IDs & Precision Loss (CRITICAL):** ZKE numeric order IDs are extremely long and WILL cause JavaScript precision loss if passed as integers. To prevent this, strict ID rules apply:
    * **Spot & Margin Orders:** The system automatically generates a safe alphanumeric ID starting with `ZKE-AI-` (e.g., `ZKE-AI-SELL-a1b2`). When cancelling or querying these orders, **ALWAYS** use this `client_order_id` instead of the numeric `order_id`. 
    * **Futures Orders:** Futures require the standard `order_id`. You **MUST ALWAYS** pass it as a string (wrapped in double quotes, e.g., `"256609229205684228"`) when calling tools to prevent truncation.
* **Timestamps:** When an endpoint (like futures transaction history) requires `begin_time` or `end_time`, you MUST use **13-digit millisecond timestamps** (e.g., `1740787200000`). Do not use `YYYY-MM-DD` strings.
* **Transfer History:** Do not call transfer history with empty parameters. Always try to provide `from_account` and `to_account`. Valid account types are `EXCHANGE` (Spot) and `FUTURE`.
* **Tool Parameters:** Rely on the explicit `inputSchema` provided by each tool to determine required fields (e.g., only provide `price` if `order_type` is `LIMIT`).

## 4. Capabilities Summary
You have tools for:
* **Spot/Margin:** Querying tickers, depth, balances, open orders, trade history, and creating/canceling orders (Safeguarded against ID precision loss).
* **Futures:** Querying index prices, account balances, active positions, adjusting leverage/margin modes, and creating/canceling orders (including conditional orders).
* **Wallet:** Executing and querying internal transfers (Spot <-> Futures) and withdrawals.

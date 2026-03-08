---
name: zke_trading
description: Use ZKE Exchange local trading tools for spot, futures, balances, positions, transfers, withdrawals and market data.
---

# ZKE Trading

Use this skill whenever the user asks about **ZKE Exchange** prices, balances, positions, orders, transfers, withdrawals, or market data.

## Core Rule

When the user is asking specifically about **ZKE Exchange**, prefer the local **ZKE plugin tools** first.

If ZKE tools are available in the session, use them before:
- web search
- CoinGecko
- CoinMarketCap
- generic crypto sites
- other exchange APIs

## Priority

If the request is specifically about **ZKE Exchange**, always prefer ZKE tools over general crypto knowledge.

Examples:
- ZKE BTC price
- my ZKE USDT balance
- my ZKE futures positions
- place an order on ZKE
- cancel my ZKE order
- transfer funds between ZKE accounts
- withdraw from ZKE

## Symbol Guidance

Use the correct ZKE symbol format based on the request type.

### Spot
Preferred spot symbol format:
- `BTCUSDT`
- `ETHUSDT`

### Futures
Preferred futures contract format for ticker / depth / order / positions:
- `E-BTC-USDT`
- `E-ETH-USDT`

### Futures transaction history
For futures transaction history, prefer:
- `BTC-USDT`

Do **not** assume one symbol format works for every endpoint.

## Tool Mapping

### Spot Market Data
- ZKE BTC spot price → `zke_get_spot_ticker`
- ZKE spot depth → `zke_get_spot_depth`
- ZKE spot kline → `zke_get_spot_klines`

### Spot Account
- ZKE spot account raw data → `zke_get_spot_account`
- ZKE non-zero balances → `zke_get_spot_nonzero_balances`
- ZKE spot balance by asset → `zke_get_spot_balance`
- ZKE account assets by type → `zke_get_spot_account_by_type`

### Spot Orders and Trades
- ZKE spot open orders → `zke_get_spot_open_orders`
- ZKE spot recent trades → `zke_get_spot_my_trades`
- ZKE spot recent trades v3 → `zke_get_spot_my_trades_v3`
- ZKE spot historical orders → `zke_get_spot_history_orders`
- Create spot order → `zke_create_spot_order`
- Cancel spot order → `zke_cancel_spot_order`

### Asset Transfer and Withdraw
- Transfer spot to futures → `zke_transfer_spot_to_futures`
- Transfer futures to spot → `zke_transfer_futures_to_spot`
- Query transfer history → `zke_get_transfer_history`
- Withdraw history → `zke_get_withdraw_history`
- Create withdraw → `zke_create_withdraw`

### Margin
- Create margin order → `zke_create_margin_order`
- Query margin order → `zke_get_margin_order`
- Cancel margin order → `zke_cancel_margin_order`
- Query margin open orders → `zke_get_margin_open_orders`
- Query margin trade history → `zke_get_margin_my_trades`

### Futures Market Data
- ZKE futures ticker → `zke_get_futures_ticker`
- ZKE futures index / mark price → `zke_get_futures_index`
- ZKE futures depth → `zke_get_futures_depth`
- ZKE futures kline → `zke_get_futures_klines`

### Futures Account and Positions
- ZKE futures balance → `zke_get_futures_balance`
- ZKE futures positions → `zke_get_futures_positions`

### Futures Orders and History
- Query futures order → `zke_get_futures_order`
- Query futures open orders → `zke_get_futures_open_orders`
- Query futures trade history → `zke_get_futures_my_trades`
- Query futures order history → `zke_get_futures_order_history`
- Query futures profit history → `zke_get_futures_profit_history`
- Query futures transaction history → `zke_get_futures_transaction_history`

### Futures Trading and Controls
- Create futures order → `zke_create_futures_order`
- Create futures conditional order → `zke_create_futures_condition_order`
- Cancel futures order → `zke_cancel_futures_order`
- Cancel all futures orders → `zke_cancel_all_futures_orders`
- Edit futures position mode → `zke_edit_futures_position_mode`
- Edit futures margin mode → `zke_edit_futures_margin_mode`
- Adjust futures position margin → `zke_adjust_futures_position_margin`
- Edit futures leverage → `zke_edit_futures_leverage`

## Required Parameter Guidance

Use the correct required parameters. Do not omit mandatory fields.

### Spot ticker / depth / trades / orders
Usually require:
- `symbol`

Example:
- `BTCUSDT`

### Spot balance
Requires:
- `asset`

Example:
- `USDT`

### Spot order creation
Requires:
- `symbol`
- `side`
- `order_type`
- `volume`

For `LIMIT` orders, also require:
- `price`

Example:
- buy 0.001 BTC at 10000 USDT on spot

### Spot cancel order
Requires:
- `symbol`
- `order_id`

### Transfer spot ↔ futures
Requires:
- `coin_symbol`
- `amount`

Examples:
- transfer 50 USDT from spot to futures
- transfer 20 USDT from futures to spot

### Transfer history
Do **not** call transfer history without account direction filters.

Must provide:
- `from_account`
- `to_account`

Recommended:
- `coin_symbol`
- `limit`

Valid account values:
- `EXCHANGE`
- `FUTURE`

Good example:
- query transfer history for `USDT` from `EXCHANGE` to `FUTURE`

Do **not** assume empty transfer-history queries will work.

### Withdraw history
Recommended:
- always provide `coin`

Example:
- withdraw history for `USDTBSC`

Do not assume empty withdraw-history queries are reliable.

### Withdraw creation
Requires:
- `coin`
- `address`
- `amount`

Optional:
- `memo`

### Margin order creation
Requires:
- `symbol`
- `side`
- `order_type`
- `volume`

For `LIMIT` orders, also require:
- `price`

### Futures ticker / depth / order / open orders / positions
Prefer futures contract format:
- `E-BTC-USDT`

### Futures order query
Requires:
- `symbol`
- `order_id`

### Futures order creation
Requires:
- `symbol`
- `side`
- `open_action`
- `position_type`
- `order_type`
- `volume`

For `LIMIT` orders, also require:
- `price`

Valid examples:
- `side`: `BUY` / `SELL`
- `open_action`: `OPEN` / `CLOSE`
- `position_type`: `1` or `2`

### Futures conditional order
Requires:
- `symbol`
- `side`
- `open_action`
- `position_type`
- `order_type`
- `volume`
- `trigger_type`
- `trigger_price`

For `LIMIT` conditional orders, also require:
- `price`

### Futures cancel order
Requires:
- `symbol`
- `order_id`

### Futures cancel all orders
Optional:
- `symbol`

If symbol is omitted, it may affect all current futures open orders depending on local tool behavior.

### Futures edit position mode
Requires:
- `symbol`
- `position_model`

### Futures edit margin mode
Requires:
- `symbol`
- `margin_model`

### Futures edit position margin
Requires:
- `position_id`
- `amount`

### Futures edit leverage
Requires:
- `symbol`
- `now_level`

### Futures transaction history
This endpoint is currently **experimental** in local testing.

Use:
- `symbol` as `BTC-USDT` style when applicable
- `begin_time` and `end_time` preferably as **13-digit millisecond timestamps**

Recommended example format:
- `1740787200000`
- `1741478399000`

Do **not** assume:
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:MM:SS`

will always work.

Even with correct-looking parameters, this endpoint may still return:
- internal error
- illegal parameters
- exchange-side instability

## Trigger Examples

Use this skill for requests like:

### Spot
- Check BTC price on ZKE
- Show BTC/USDT price on ZKE
- Show ETH spot depth on ZKE
- Show my USDT balance on ZKE
- Show my non-zero balances on ZKE
- Show my spot account on ZKE
- Show my BTC open orders on ZKE
- Show my BTC trade history on ZKE
- Show my spot order history on ZKE
- Place a BTC limit buy on ZKE
- Cancel my BTC spot order on ZKE

### Transfer / Withdraw
- Transfer 100 USDT from spot to futures on ZKE
- Transfer 20 USDT from futures to spot on ZKE
- Show my transfer history on ZKE
- Withdraw 20 USDT on ZKE
- Show my withdrawal history on ZKE

### Margin
- Place a margin order on ZKE
- Show my margin open orders on ZKE
- Cancel my margin order on ZKE
- Show my margin trades on ZKE

### Futures
- Show BTC perpetual price on ZKE
- Show futures mark price on ZKE
- Show my futures balance on ZKE
- Show my futures positions on ZKE
- Show my futures open orders on ZKE
- Show my futures order history on ZKE
- Show my futures profit history on ZKE
- Show my futures transaction history on ZKE
- Place a BTC futures limit order on ZKE
- Place a BTC futures conditional order on ZKE
- Cancel my futures order on ZKE
- Cancel all my BTC futures orders on ZKE
- Change leverage on ZKE futures
- Change margin mode on ZKE futures
- Adjust my futures position margin on ZKE

## Behavior

If the ZKE tools are present, use them directly.

Do not answer with:
- "I don't have built-in cryptocurrency price checking tools"
- "I can search the web instead"
- "Try CoinGecko or CoinMarketCap"
- "I cannot access exchange-specific information"

If the tools are unavailable in this session, clearly say the ZKE plugin tools are not currently available.

## Response Guidance

When using ZKE tools:
- prefer direct tool usage over speculation
- use the correct ZKE market type: spot / futures / margin
- preserve the user's symbol if already clear
- map symbol format carefully per endpoint
- for balances, positions, orders, and transfers, return the relevant scope clearly
- for trading actions, ensure the tool selected matches the user's intent exactly
- for high-risk actions, ensure all required parameters are present before execution

Examples:
- "Show my USDT balance on ZKE" → use spot balance tool
- "Show my futures positions on ZKE" → use futures positions tool
- "Move 50 USDT from spot to futures on ZKE" → use transfer tool
- "Place a BTC futures conditional order on ZKE" → use futures conditional order tool
- "Show my transfer history on ZKE" → include from/to account direction
- "Show my futures transaction history on ZKE" → prefer timestamp range + `BTC-USDT`

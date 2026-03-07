---
name: zke_trading
description: Use ZKE Exchange local trading tools for spot, futures, balances, positions, withdrawals and market data.
---

# ZKE Trading

Use this skill whenever the user asks about **ZKE Exchange** prices, balances, positions, orders, withdrawals, or market data.

## Core rule

When the user is asking about **ZKE Exchange**, prefer the ZKE plugin tools instead of replying that you do not have crypto price tools.

Do not default to:
- web search
- CoinGecko
- CoinMarketCap
- generic crypto sites

If ZKE tools are available in the session, use them first.

## Tool mapping

- ZKE BTC spot price → `zke_get_spot_ticker`
- ZKE spot depth → `zke_get_spot_depth`
- ZKE spot balance → `zke_get_spot_balance`
- ZKE spot open orders → `zke_get_spot_open_orders`
- ZKE spot trades → `zke_get_spot_my_trades`
- Create spot order → `zke_create_spot_order`
- Cancel spot order → `zke_cancel_spot_order`

- ZKE futures ticker → `zke_get_futures_ticker`
- ZKE futures index → `zke_get_futures_index`
- ZKE futures balance → `zke_get_futures_balance`
- ZKE futures positions → `zke_get_futures_positions`
- ZKE futures open orders → `zke_get_futures_open_orders`
- ZKE futures trades → `zke_get_futures_my_trades`
- ZKE futures order history → `zke_get_futures_order_history`
- ZKE futures profit history → `zke_get_futures_profit_history`
- Create futures order → `zke_create_futures_order`
- Cancel futures order → `zke_cancel_futures_order`

- Withdraw history → `zke_get_withdraw_history`
- Create withdraw → `zke_create_withdraw`

## Trigger examples

Use this skill for requests like:

- Check BTC price on ZKE
- Show BTC/USDT price on ZKE
- Show my USDT balance on ZKE
- Show my futures positions on ZKE
- Show my BTC open orders on ZKE
- Withdraw 20 USDTBSC on ZKE
- Place a BTC limit buy on ZKE

## Behavior

If the ZKE tools are present, use them directly.

Do not answer with:
- "I don't have built-in cryptocurrency price checking tools"
- "I can search the web instead"

If the tools are unavailable in this session, clearly say the ZKE plugin tools are not currently available.

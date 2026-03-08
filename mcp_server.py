# /www/wwwroot/zke-trading/mcp_server.py

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

from tools.zke_client import ZKEClient
from tools.spot_public import SpotPublicApi
from tools.spot_private import SpotPrivateApi
from tools.futures_public import FuturesPublicApi
from tools.futures_private import FuturesPrivateApi
from tools.margin_private import MarginPrivateApi

from tools import market_service
from tools import account_service
from tools import order_service
from tools import futures_service
from tools import futures_account_service
from tools import futures_order_service
from tools import margin_order_service
from tools import withdraw_service
from tools import transfer_service
from tools.field_mapper import map_side, map_position_type, map_order_status
from tools.ws_client import ZKEWebSocketClient
from tools.ws_parser import normalize_ws_message
from tools import ws_service


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

mcp = FastMCP("zke-trading")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_spot_client() -> ZKEClient:
    config = load_config()
    spot_conf = config["spot"]
    return ZKEClient(
        base_url=spot_conf["base_url"],
        api_key=spot_conf.get("api_key", ""),
        api_secret=spot_conf.get("api_secret", ""),
        recv_window=spot_conf.get("recv_window", 5000),
    )


def build_futures_client() -> ZKEClient:
    config = load_config()
    fut_conf = config["futures"]
    return ZKEClient(
        base_url=fut_conf["base_url"],
        api_key=fut_conf.get("api_key", ""),
        api_secret=fut_conf.get("api_secret", ""),
        recv_window=fut_conf.get("recv_window", 5000),
    )


def get_ws_url() -> str:
    config = load_config()
    ws_conf = config.get("ws", {})
    url = ws_conf.get("url")
    if not url:
        raise ValueError("config.json 中缺少 ws.url")
    return url


SPOT_CLIENT = build_spot_client()
SPOT_PUBLIC = SpotPublicApi(SPOT_CLIENT)
SPOT_PRIVATE = SpotPrivateApi(SPOT_CLIENT)
MARGIN_PRIVATE = MarginPrivateApi(SPOT_CLIENT)

FUTURES_CLIENT = build_futures_client()
FUTURES_PUBLIC = FuturesPublicApi(FUTURES_CLIENT)
FUTURES_PRIVATE = FuturesPrivateApi(FUTURES_CLIENT)

SPOT_REGISTRY = market_service.get_registry(SPOT_PUBLIC)
FUTURES_REGISTRY = futures_service.get_registry(FUTURES_PUBLIC)


def _normalize_list_result(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, dict):
        if isinstance(raw.get("list"), list):
            return raw["list"]
        if isinstance(raw.get("data"), list):
            return raw["data"]
        if raw.get("data") is None and str(raw.get("code")) == "0":
            return []
        return []
    if isinstance(raw, list):
        return raw
    return []


# =========================================================
# WebSocket helpers
# =========================================================

def _collect_ws_messages(
    subscriptions: List[dict],
    seconds: int = 3,
    limit: int = 20,
    debug: bool = False,
) -> Dict[str, Any]:
    messages: List[Dict[str, Any]] = []

    def _handler(data: Any):
        try:
            normalized = normalize_ws_message(data)
        except Exception:
            normalized = {"type": "unknown", "raw": data}

        if len(messages) < limit:
            messages.append(normalized)

    client = ZKEWebSocketClient(
        url=get_ws_url(),
        subscriptions=subscriptions,
        on_message=_handler,
        reconnect=False,
        reconnect_delay=1,
        debug=debug,
    )

    thread = client.start_background()

    try:
        time.sleep(max(1, int(seconds)))
    finally:
        client.close()

    if thread:
        thread.join(timeout=2)

    return {
        "ws_url": get_ws_url(),
        "seconds": max(1, int(seconds)),
        "count": len(messages),
        "messages": messages,
    }


# =========================================================
# Spot - Readonly
# =========================================================

@mcp.tool()
def get_spot_ticker(symbol: str) -> Dict[str, Any]:
    """
    获取现货交易对最新行情。
    symbol 例子: BTCUSDT
    """
    data = market_service.get_ticker(SPOT_PUBLIC, SPOT_REGISTRY, symbol)
    return {
        "symbol": symbol.upper(),
        "last": data.get("last"),
        "buy": data.get("buy", data.get("bidPrice")),
        "sell": data.get("sell", data.get("askPrice")),
        "high": data.get("high"),
        "low": data.get("low"),
        "vol": data.get("vol"),
        "rose": data.get("rose"),
        "open": data.get("open"),
        "time": data.get("time"),
    }


@mcp.tool()
def get_spot_depth(symbol: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取现货订单簿深度。
    symbol 例子: BTCUSDT
    """
    data = market_service.get_depth(SPOT_PUBLIC, SPOT_REGISTRY, symbol, limit)
    return {
        "symbol": symbol.upper(),
        "limit": limit,
        "bids": data.get("bids", []),
        "asks": data.get("asks", []),
    }


@mcp.tool()
def get_spot_klines(symbol: str, interval: str = "1day") -> Dict[str, Any]:
    """
    获取现货K线。
    symbol 例子: BTCUSDT
    """
    data = market_service.get_klines(SPOT_PUBLIC, SPOT_REGISTRY, symbol, interval)
    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "klines": data,
        "count": len(data) if isinstance(data, list) else 0,
    }


@mcp.tool()
def get_spot_account() -> Dict[str, Any]:
    """
    获取现货账户原始资产数据。
    """
    return SPOT_PRIVATE.account()


@mcp.tool()
def get_spot_nonzero_balances() -> Dict[str, Any]:
    """
    获取现货非零余额资产列表。
    """
    account_data = SPOT_PRIVATE.account()
    balances = account_service.extract_account_balances(account_data)
    nonzero = account_service.filter_nonzero_balances(balances)
    return {
        "balances": nonzero,
        "count": len(nonzero),
    }


@mcp.tool()
def get_spot_balance(asset: str) -> Dict[str, Any]:
    """
    获取现货某个币种余额。
    asset 例子: USDT
    """
    account_data = SPOT_PRIVATE.account()
    balances = account_service.extract_account_balances(account_data)
    summary = account_service.get_asset_balance_summary(balances, asset)
    return {
        "asset": summary.get("asset"),
        "free": summary.get("free"),
        "locked": summary.get("locked"),
    }


@mcp.tool()
def get_spot_account_by_type(account_type: str) -> Dict[str, Any]:
    """
    按账户类型查询现货资产。
    account_type 例子: 1
    """
    return SPOT_PRIVATE.account_by_type(account_type)


@mcp.tool()
def get_spot_open_orders(symbol: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取现货某个交易对当前挂单。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    raw = SPOT_PRIVATE.open_orders(api_symbol, limit)
    orders = _normalize_list_result(raw)
    return {
        "symbol": symbol.upper(),
        "orders": orders,
        "count": len(orders),
    }


@mcp.tool()
def get_spot_my_trades(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取现货某个交易对最近成交。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    raw = SPOT_PRIVATE.my_trades(api_symbol, limit)
    trades = _normalize_list_result(raw)
    return {
        "symbol": symbol.upper(),
        "trades": trades,
        "count": len(trades),
    }


@mcp.tool()
def get_spot_my_trades_v3(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取现货某个交易对 v3 成交记录。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    raw = SPOT_PRIVATE.my_trades_v3(symbol=api_symbol, limit=limit)
    trades = _normalize_list_result(raw)
    return {
        "symbol": symbol.upper(),
        "trades": trades,
        "count": len(trades),
    }


@mcp.tool()
def get_spot_history_orders(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取现货某个交易对历史订单。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    raw = SPOT_PRIVATE.history_orders(symbol=api_symbol, limit=limit)
    orders = _normalize_list_result(raw)
    return {
        "symbol": symbol.upper(),
        "orders": orders,
        "count": len(orders),
    }


# =========================================================
# Spot - Trading
# =========================================================

@mcp.tool()
def create_spot_order(
    symbol: str,
    side: str,
    order_type: str,
    volume: str,
    price: str = ""
) -> Dict[str, Any]:
    """
    创建现货订单。
    symbol 例子: BTCUSDT
    side: BUY / SELL
    order_type: LIMIT / MARKET
    volume: 数量
    price: LIMIT 单必填，MARKET 可留空
    """
    p = price.strip() if isinstance(price, str) else price
    if p == "":
        p = None

    data, result = order_service.create_order(
        SPOT_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        side,
        order_type,
        volume,
        p
    )

    return {
        "request": data,
        "result": result,
    }


@mcp.tool()
def cancel_spot_order(symbol: str, order_id: str) -> Dict[str, Any]:
    """
    撤销现货订单。
    symbol 例子: BTCUSDT
    order_id: 订单ID
    """
    result = order_service.cancel_order(
        SPOT_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        order_id
    )
    return {
        "symbol": symbol.upper(),
        "order_id": order_id,
        "result": result,
    }


# =========================================================
# Spot Transfer
# =========================================================

@mcp.tool()
def transfer_spot_to_futures(coin_symbol: str, amount: str) -> Dict[str, Any]:
    """
    现货账户划转到合约账户。
    coin_symbol 例子: USDT
    """
    return transfer_service.transfer_spot_to_futures(
        SPOT_PRIVATE,
        coin_symbol,
        amount,
    )


@mcp.tool()
def transfer_futures_to_spot(coin_symbol: str, amount: str) -> Dict[str, Any]:
    """
    合约账户划转回现货账户。
    coin_symbol 例子: USDT
    """
    return transfer_service.transfer_futures_to_spot(
        SPOT_PRIVATE,
        coin_symbol,
        amount,
    )


@mcp.tool()
def get_transfer_history(
    coin_symbol: str = "",
    from_account: str = "",
    to_account: str = "",
    limit: int = 20,
) -> Dict[str, Any]:
    """
    查询现货/合约划转记录。
    from_account / to_account 可用 EXCHANGE / FUTURE
    """
    rows = transfer_service.query_transfer_history(
        api=SPOT_PRIVATE,
        coin_symbol=coin_symbol if coin_symbol else None,
        from_account=from_account if from_account else None,
        to_account=to_account if to_account else None,
        limit=limit,
    )
    return {
        "coin_symbol": coin_symbol,
        "from_account": from_account,
        "to_account": to_account,
        "records": rows,
        "count": len(rows),
    }


# =========================================================
# Withdraw
# =========================================================

@mcp.tool()
def create_withdraw(
    coin: str,
    address: str,
    amount: str,
    network: str = "",
    memo: str = ""
) -> Dict[str, Any]:
    """
    发起提现。
    network 和 memo 可留空。
    """
    result = withdraw_service.apply_withdraw(
        SPOT_PRIVATE,
        coin,
        address,
        amount,
        network if network else None,
        memo if memo else None
    )

    return result


@mcp.tool()
def get_withdraw_history(
    coin: str = "",
    limit: int = 20
) -> Dict[str, Any]:
    """
    查询提现记录。
    coin 可留空。
    """
    rows = withdraw_service.withdraw_history(
        SPOT_PRIVATE,
        coin if coin else None,
        limit
    )

    return {
        "coin": coin,
        "records": rows,
        "count": len(rows)
    }


# =========================================================
# Margin
# =========================================================

@mcp.tool()
def create_margin_order(
    symbol: str,
    side: str,
    order_type: str,
    volume: str,
    price: str = ""
) -> Dict[str, Any]:
    """
    创建杠杆订单。
    symbol 例子: BTCUSDT
    side: BUY / SELL
    order_type: LIMIT / MARKET
    volume: 数量
    price: LIMIT 单必填，MARKET 可留空
    """
    p = price.strip() if isinstance(price, str) else price
    if p == "":
        p = None

    data, result = margin_order_service.create_order(
        MARGIN_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        side,
        order_type,
        volume,
        p
    )

    return {
        "request": data,
        "result": result,
    }


@mcp.tool()
def get_margin_order(symbol: str, order_id: str) -> Dict[str, Any]:
    """
    查询杠杆订单。
    symbol 例子: BTCUSDT
    order_id: 订单ID
    """
    result = margin_order_service.order_query(
        MARGIN_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        order_id=order_id
    )
    return result


@mcp.tool()
def cancel_margin_order(symbol: str, order_id: str) -> Dict[str, Any]:
    """
    撤销杠杆订单。
    symbol 例子: BTCUSDT
    order_id: 订单ID
    """
    result = margin_order_service.cancel_order(
        MARGIN_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        order_id=order_id
    )
    return {
        "symbol": symbol.upper(),
        "order_id": order_id,
        "result": result,
    }


@mcp.tool()
def get_margin_open_orders(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """
    获取杠杆当前挂单。
    symbol 例子: BTCUSDT
    """
    rows = margin_order_service.open_orders(
        MARGIN_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        limit=limit
    )
    return {
        "symbol": symbol.upper(),
        "orders": rows,
        "count": len(rows),
    }


@mcp.tool()
def get_margin_my_trades(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """
    获取杠杆成交记录。
    symbol 例子: BTCUSDT
    """
    rows = margin_order_service.my_trades(
        MARGIN_PRIVATE,
        SPOT_REGISTRY,
        symbol,
        limit=limit
    )
    return {
        "symbol": symbol.upper(),
        "trades": rows,
        "count": len(rows),
    }


# =========================================================
# Futures - Readonly
# =========================================================

@mcp.tool()
def get_futures_ticker(symbol: str) -> Dict[str, Any]:
    """
    获取合约最新行情。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    data = futures_service.get_ticker(FUTURES_PUBLIC, FUTURES_REGISTRY, symbol)
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    return {
        "contract": contract,
        "last": data.get("last"),
        "buy": data.get("buy", data.get("bidPrice")),
        "sell": data.get("sell", data.get("askPrice")),
        "high": data.get("high"),
        "low": data.get("low"),
        "vol": data.get("vol"),
        "rose": data.get("rose"),
        "time": data.get("time"),
    }


@mcp.tool()
def get_futures_index(symbol: str) -> Dict[str, Any]:
    """
    获取合约指数/标记价格。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    data = futures_service.get_index(FUTURES_PUBLIC, FUTURES_REGISTRY, symbol)
    return {
        "contract": contract,
        "tagPrice": data.get("tagPrice", data.get("markPrice")),
        "indexPrice": data.get("indexPrice"),
        "currentFundRate": data.get("currentFundRate", data.get("lastFundingRate")),
        "nextFundRate": data.get("nextFundRate"),
        "time": data.get("time"),
    }


@mcp.tool()
def get_futures_depth(symbol: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取合约订单簿深度。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    data = futures_service.get_depth(FUTURES_PUBLIC, FUTURES_REGISTRY, symbol, limit)
    return {
        "contract": contract,
        "limit": limit,
        "bids": data.get("bids", []),
        "asks": data.get("asks", []),
    }


@mcp.tool()
def get_futures_klines(symbol: str, interval: str = "1min", limit: int = 20) -> Dict[str, Any]:
    """
    获取合约K线。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    data = futures_service.get_klines(FUTURES_PUBLIC, FUTURES_REGISTRY, symbol, interval, limit)
    return {
        "contract": contract,
        "interval": interval,
        "limit": limit,
        "klines": data,
        "count": len(data) if isinstance(data, list) else 0,
    }


@mcp.tool()
def get_futures_balance(margin_coin: str = "USDT") -> Dict[str, Any]:
    """
    获取合约某个保证金币种余额。
    margin_coin 例子: USDT
    """
    data = FUTURES_PRIVATE.account()
    accounts = futures_account_service.extract_accounts(data)
    summary = futures_account_service.get_margin_coin_summary(accounts, margin_coin)
    return summary


@mcp.tool()
def get_futures_positions() -> Dict[str, Any]:
    """
    获取当前所有非零合约持仓。
    """
    data = FUTURES_PRIVATE.account()
    accounts = futures_account_service.extract_accounts(data)
    positions = futures_account_service.flatten_positions(accounts)
    positions = futures_account_service.filter_nonzero_positions(positions)

    normalized = []
    for p in positions:
        normalized.append({
            "contract": p.get("_contractName"),
            "contract_symbol": p.get("_contractSymbol"),
            "margin_coin": p.get("_marginCoin"),
            "side": map_side(p.get("side")),
            "position_type": map_position_type(p.get("positionType")),
            "volume": p.get("volume"),
            "open_price": p.get("openPrice"),
            "avg_price": p.get("avgPrice"),
            "leverage": p.get("leverageLevel"),
            "unrealized_pnl": p.get("unRealizedAmount", p.get("unrealizedAmount")),
            "realized_pnl": p.get("realizedAmount"),
            "margin_rate": p.get("marginRate"),
            "liquidation_hint_price": p.get("reducePrice"),
            "return_rate": p.get("returnRate"),
            "position_balance": p.get("positionBalance"),
            "mark_price": p.get("indexPrice"),
        })

    return {
        "positions": normalized,
        "count": len(normalized),
    }


@mcp.tool()
def get_futures_open_orders(symbol: str) -> Dict[str, Any]:
    """
    获取某个合约当前挂单。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    rows = futures_order_service.open_orders(
        FUTURES_PRIVATE,
        FUTURES_REGISTRY,
        symbol
    )

    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)

    normalized = []
    for o in rows:
        normalized.append({
            "contract": o.get("contractName") or contract,
            "side": map_side(o.get("side")),
            "position_type": map_position_type(o.get("positionType")),
            "price": o.get("price"),
            "volume": o.get("volume"),
            "deal_volume": o.get("dealVolume"),
            "status": map_order_status(o.get("status")),
            "order_id": o.get("orderId"),
            "time": o.get("ctimeMs") or o.get("ctime") or o.get("transactTime"),
        })

    return {
        "contract": contract,
        "orders": normalized,
        "count": len(normalized),
    }


@mcp.tool()
def get_futures_my_trades(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取某个合约最近成交记录。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    trades = futures_order_service.my_trades(
        FUTURES_PRIVATE,
        FUTURES_REGISTRY,
        symbol,
        limit
    )
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    return {
        "contract": contract,
        "trades": trades,
        "count": len(trades),
    }


@mcp.tool()
def get_futures_order_history(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取某个合约历史订单。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    rows = futures_order_service.order_historical(
        FUTURES_PRIVATE,
        FUTURES_REGISTRY,
        symbol,
        limit
    )
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    return {
        "contract": contract,
        "orders": rows,
        "count": len(rows),
    }


@mcp.tool()
def get_futures_profit_history(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取某个合约盈亏记录。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    """
    rows = futures_order_service.profit_historical(
        FUTURES_PRIVATE,
        FUTURES_REGISTRY,
        symbol,
        limit
    )
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    return {
        "contract": contract,
        "records": rows,
        "count": len(rows),
    }


# =========================================================
# Futures - Trading
# =========================================================

@mcp.tool()
def create_futures_order(
    symbol: str,
    side: str,
    open_action: str,
    position_type: int,
    order_type: str,
    volume: str,
    price: str = ""
) -> Dict[str, Any]:
    """
    创建合约订单。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    side: BUY / SELL
    open_action: OPEN / CLOSE
    position_type: 1=全仓 2=逐仓
    order_type: LIMIT / MARKET
    volume: 数量（张）
    price: LIMIT 单必填，MARKET 可留空
    """
    p = price.strip() if isinstance(price, str) else price
    if p == "":
        p = None

    data, result = futures_order_service.create_order(
        FUTURES_PRIVATE,
        FUTURES_REGISTRY,
        symbol,
        side,
        open_action,
        position_type,
        order_type,
        volume,
        p
    )

    return {
        "request": data,
        "result": result,
    }


@mcp.tool()
def cancel_futures_order(symbol: str, order_id: str) -> Dict[str, Any]:
    """
    撤销合约订单。
    symbol 例子: E-BTC-USDT 或 BTCUSDT
    order_id: 订单ID
    """
    result = futures_order_service.cancel_order(
        FUTURES_PRIVATE,
        FUTURES_REGISTRY,
        symbol,
        order_id
    )
    contract = FUTURES_REGISTRY.resolve_contract_name(symbol)
    return {
        "contract": contract,
        "order_id": order_id,
        "result": result,
    }


# =========================================================
# Spot WS - Public
# =========================================================

@mcp.tool()
def ws_spot_ticker_once(symbol: str, seconds: int = 3, limit: int = 20) -> Dict[str, Any]:
    """
    短时订阅现货 ticker WebSocket。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    return _collect_ws_messages(
        subscriptions=[ws_service.build_ticker_sub(api_symbol)],
        seconds=seconds,
        limit=limit,
    )


@mcp.tool()
def ws_spot_depth_once(symbol: str, step: str = "step0", seconds: int = 3, limit: int = 20) -> Dict[str, Any]:
    """
    短时订阅现货 depth WebSocket。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    return _collect_ws_messages(
        subscriptions=[ws_service.build_depth_sub(api_symbol, step=step)],
        seconds=seconds,
        limit=limit,
    )


@mcp.tool()
def ws_spot_kline_once(symbol: str, interval: str = "1min", seconds: int = 3, limit: int = 20) -> Dict[str, Any]:
    """
    短时订阅现货 kline WebSocket。
    symbol 例子: BTCUSDT
    interval: 1min/5min/15min/30min/60min/1day/1week/1month
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    return _collect_ws_messages(
        subscriptions=[ws_service.build_kline_sub(api_symbol, interval=interval)],
        seconds=seconds,
        limit=limit,
    )


@mcp.tool()
def ws_spot_trades_once(symbol: str, seconds: int = 3, limit: int = 20) -> Dict[str, Any]:
    """
    短时订阅现货实时成交 WebSocket。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    return _collect_ws_messages(
        subscriptions=[ws_service.build_trade_sub(api_symbol)],
        seconds=seconds,
        limit=limit,
    )


@mcp.tool()
def ws_spot_kline_history_once(
    symbol: str,
    interval: str = "1min",
    page_size: int = 100,
    end_idx: str = "",
    seconds: int = 3,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    通过 WS req 请求现货历史K线。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    return _collect_ws_messages(
        subscriptions=[
            ws_service.build_kline_req(
                api_symbol,
                interval=interval,
                end_idx=end_idx if end_idx else None,
                page_size=page_size,
            )
        ],
        seconds=seconds,
        limit=limit,
    )


@mcp.tool()
def ws_spot_trade_history_once(symbol: str, seconds: int = 3, limit: int = 20) -> Dict[str, Any]:
    """
    通过 WS req 请求现货历史成交。
    symbol 例子: BTCUSDT
    """
    api_symbol = SPOT_REGISTRY.get_api_symbol(symbol)
    return _collect_ws_messages(
        subscriptions=[ws_service.build_trade_req(api_symbol)],
        seconds=seconds,
        limit=limit,
    )


if __name__ == "__main__":
    mcp.run()

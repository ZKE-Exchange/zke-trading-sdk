# tools/futures_order_service.py

from .field_mapper import (
    map_side,
    map_open_close,
    map_position_type,
    map_order_status,
)


def open_orders(api, registry, symbol):
    contract = registry.resolve_contract_name(symbol)

    result = api.open_orders(contract)

    if isinstance(result, dict):

        if isinstance(result.get("data"), list):
            return result["data"]

        if isinstance(result.get("data"), dict):
            return [result["data"]]

        return []

    if isinstance(result, list):
        return result

    return []


def order_query(api, registry, symbol, order_id=None):
    contract = registry.resolve_contract_name(symbol)

    result = api.order_query(contract, order_id)

    return result


def my_trades(api, registry, symbol, limit=10):
    contract = registry.resolve_contract_name(symbol)

    trades = api.my_trades(contract, limit)

    if isinstance(trades, dict):

        if isinstance(trades.get("data"), list):
            trade_list = trades["data"]
        else:
            trade_list = []

    elif isinstance(trades, list):
        trade_list = trades
    else:
        trade_list = []

    clean = []

    for t in trade_list:

        clean.append({
            "contract": t.get("contractName"),
            "side": map_side(t.get("side")),
            "price": t.get("price"),
            "qty": t.get("qty"),
            "fee": t.get("fee"),
            "time": t.get("time"),
        })

    return clean


def order_historical(api, registry, symbol, limit=10):
    contract = registry.resolve_contract_name(symbol)

    orders = api.order_historical(contract, limit)

    if isinstance(orders, dict):

        if isinstance(orders.get("data"), list):
            order_list = orders["data"]
        else:
            order_list = []

    elif isinstance(orders, list):
        order_list = orders
    else:
        order_list = []

    clean = []

    for o in order_list:

        clean.append({
            "contract": o.get("contractName"),
            "side": map_side(o.get("side")),
            "action": map_open_close(o.get("openOrClose")),
            "position_mode": map_position_type(o.get("positionType")),
            "price": o.get("price"),
            "volume": o.get("volume"),
            "deal_volume": o.get("dealVolume"),
            "status": map_order_status(o.get("status")),
            "time": o.get("ctimeMs", o.get("ctime")),
        })

    return clean


def profit_historical(api, registry, symbol, limit=10):
    contract = registry.resolve_contract_name(symbol)

    records = api.profit_historical(contract, limit)

    if isinstance(records, dict):

        if isinstance(records.get("data"), list):
            record_list = records["data"]
        else:
            record_list = []

    elif isinstance(records, list):
        record_list = records
    else:
        record_list = []

    clean = []

    for r in record_list:

        clean.append({
            "contract": r.get("contractName"),
            "side": map_side(r.get("side")),
            "position_mode": map_position_type(r.get("positionType")),
            "open_price": r.get("openPrice"),
            "profit": r.get("closeProfit"),
            "fee": r.get("tradeFee"),
            "leverage": r.get("leverageLevel"),
            "time": r.get("ctime"),
        })

    return clean


def create_order(
    api,
    registry,
    symbol,
    side,
    open_action,
    position_type,
    order_type,
    volume,
    price=None
):

    contract = registry.resolve_contract_name(symbol)

    data = {
        "contract_name": contract,
        "side": side,
        "open_action": open_action,
        "position_type": position_type,
        "order_type": order_type,
        "volume": volume,
        "price": price,
    }

    result = api.create_order(
        contract,
        side,
        open_action,
        position_type,
        order_type,
        volume,
        price,
    )

    return data, result


def cancel_order(api, registry, symbol, order_id):
    contract = registry.resolve_contract_name(symbol)

    result = api.cancel_order(contract, order_id)

    return result
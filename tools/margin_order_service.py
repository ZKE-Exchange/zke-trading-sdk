from .field_mapper import map_spot_order_status, map_order_type


def _normalize_side_for_margin(side):
    if side is None:
        return "-"

    s = str(side).strip().upper()

    if s == "BUY":
        return "buy"
    if s == "SELL":
        return "sell"

    return s.lower()


def _normalize_list_result(raw):
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


def create_order(
    api,
    registry,
    symbol,
    side,
    order_type,
    volume,
    price=None,
    new_client_order_id=None,
    recv_window=None,
):
    api_symbol = registry.get_api_symbol(symbol)
    display_symbol = registry.get_display_symbol(symbol)

    data = {
        "display_symbol": display_symbol,
        "api_symbol": api_symbol,
        "side": str(side).upper(),
        "order_type": str(order_type).upper(),
        "volume": str(volume),
        "price": str(price) if price is not None else None,
        "newClientOrderId": new_client_order_id,
        "recvWindow": recv_window,
    }

    result = api.create_order(
        symbol=api_symbol,
        side=str(side).upper(),
        order_type=str(order_type).upper(),
        volume=volume,
        price=price,
        new_client_order_id=new_client_order_id,
        recv_window=recv_window,
    )

    return data, result


def order_query(api, registry, symbol, order_id=None, new_client_order_id=None):
    api_symbol = registry.get_api_symbol(symbol)

    result = api.order_query(
        symbol=api_symbol,
        order_id=order_id,
        new_client_order_id=new_client_order_id,
    )

    if not isinstance(result, dict):
        return result

    return {
        "symbol": result.get("symbol", api_symbol),
        "order_id": result.get("orderId") or result.get("orderIdString"),
        "client_order_id": result.get("clientOrderId") or result.get("clientorderId"),
        "side": _normalize_side_for_margin(result.get("side")),
        "type": map_order_type(result.get("type")),
        "price": result.get("price"),
        "orig_qty": result.get("origQty"),
        "executed_qty": result.get("executedQty"),
        "avg_price": result.get("avgPrice"),
        "status": map_spot_order_status(result.get("status")),
        "time": result.get("transactTime") or result.get("time"),
        "raw": result,
    }


def cancel_order(api, registry, symbol, order_id=None, new_client_order_id=None):
    api_symbol = registry.get_api_symbol(symbol)

    result = api.cancel_order(
        symbol=api_symbol,
        order_id=order_id,
        new_client_order_id=new_client_order_id,
    )

    if not isinstance(result, dict):
        return result

    return {
        "symbol": result.get("symbol", api_symbol),
        "order_id": result.get("orderId") or result.get("orderIdString"),
        "client_order_id": result.get("clientOrderId") or result.get("clientorderId"),
        "status": map_spot_order_status(result.get("status")),
        "raw": result,
    }


def open_orders(api, registry, symbol, limit=100):
    api_symbol = registry.get_api_symbol(symbol)

    raw = api.open_orders(api_symbol, limit)
    rows = _normalize_list_result(raw)

    clean = []

    for o in rows:
        clean.append({
            "symbol": o.get("symbol", api_symbol),
            "order_id": o.get("orderId") or o.get("orderIdString"),
            "client_order_id": o.get("clientOrderId") or o.get("clientorderId"),
            "side": _normalize_side_for_margin(o.get("side")),
            "type": map_order_type(o.get("type")),
            "price": o.get("price"),
            "orig_qty": o.get("origQty"),
            "executed_qty": o.get("executedQty"),
            "avg_price": o.get("avgPrice"),
            "status": map_spot_order_status(o.get("status")),
            "time": o.get("transactTime") or o.get("time"),
            "raw": o,
        })

    return clean


def my_trades(api, registry, symbol, limit=100, from_id=None):
    api_symbol = registry.get_api_symbol(symbol)

    raw = api.my_trades(
        symbol=api_symbol,
        limit=limit,
        from_id=from_id,
    )

    rows = _normalize_list_result(raw)

    clean = []

    for t in rows:
        clean.append({
            "symbol": t.get("symbol", api_symbol),
            "trade_id": t.get("id"),
            "bid_id": t.get("bidId"),
            "ask_id": t.get("askId"),
            "price": t.get("price"),
            "qty": t.get("qty"),
            "time": t.get("time"),
            "side": _normalize_side_for_margin(t.get("side")),
            "is_maker": t.get("isMaker"),
            "fee": t.get("fee"),
            "fee_coin": t.get("feeCoin"),
            "raw": t,
        })

    return clean

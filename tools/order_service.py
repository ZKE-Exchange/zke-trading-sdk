def prepare_order(registry, symbol, volume, price, order_type):
    validated = registry.validate_order(symbol, volume, price, order_type)

    return {
        "display_symbol": validated["display_symbol"],
        "api_symbol": validated["api_symbol"],
        "volume": validated["fixed_volume"],
        "price": validated["fixed_price"]
    }


def test_order(
    private_api,
    registry,
    symbol,
    side,
    order_type,
    volume,
    price=None,
    new_client_order_id="",
    recv_window=5000,
):
    data = prepare_order(registry, symbol, volume, price, order_type)

    result = private_api.test_order(
        symbol=data["api_symbol"],
        volume=data["volume"],
        side=side,
        order_type=order_type,
        price=data["price"],
        new_client_order_id=new_client_order_id,
        recv_window=recv_window,
    )

    return data, result


def create_order(
    private_api,
    registry,
    symbol,
    side,
    order_type,
    volume,
    price=None,
    new_client_order_id="",
    recv_window=5000,
    trigger_price=None,
):
    data = prepare_order(registry, symbol, volume, price, order_type)

    result = private_api.create_order(
        symbol=data["api_symbol"],
        volume=data["volume"],
        side=side,
        order_type=order_type,
        price=data["price"],
        new_client_order_id=new_client_order_id,
        recv_window=recv_window,
        trigger_price=trigger_price,
    )

    return data, result


def cancel_order(
    private_api,
    registry,
    symbol,
    order_id=None,
    client_order_id=None,
):
    api_symbol = registry.get_api_symbol(symbol)

    return private_api.cancel_order(
        api_symbol,
        order_id=order_id,
        client_order_id=client_order_id,
    )


def open_orders(private_api, registry, symbol, limit=100):
    api_symbol = registry.get_api_symbol(symbol)
    return private_api.open_orders(api_symbol, limit=limit)

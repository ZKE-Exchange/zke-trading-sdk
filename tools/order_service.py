import json

def prepare_order(registry, symbol, volume, price, order_type):
    """
    统一校验并格式化订单参数
    """
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
    """
    测试下单接口（不真实下单）
    """
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
    """
    创建真实订单 - 已修复参数溢出问题
    """
    data = prepare_order(registry, symbol, volume, price, order_type)

    # 1. 组装基础参数
    params = {
        "symbol": data["api_symbol"],
        "volume": data["volume"],
        "side": side,
        "order_type": order_type,
        "price": data["price"],
        "new_client_order_id": new_client_order_id,
        "recv_window": recv_window,
    }

    # 2. 只有当 trigger_price 真的有值时（止盈止损/合约），才动态加入
    if trigger_price is not None and str(trigger_price).strip() != "":
        params["trigger_price"] = trigger_price

    # 3. 使用 **params 动态传参，API 没定义的参数不会被强行发送
    result = private_api.create_order(**params)

    return data, result


def cancel_order(
    private_api,
    registry,
    symbol,
    order_id=None,
    client_order_id=None,
):
    """
    撤销订单
    """
    api_symbol = registry.get_api_symbol(symbol)

    return private_api.cancel_order(
        api_symbol,
        order_id=order_id,
        client_order_id=client_order_id,
    )


def open_orders(private_api, registry, symbol, limit=100):
    """
    查询当前挂单
    """
    api_symbol = registry.get_api_symbol(symbol)
    return private_api.open_orders(api_symbol, limit=limit)

import json
import time
import uuid
from typing import Any, Optional

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
    symbol: Any,
    side: Any,
    order_type: Any,
    volume: Any,
    price: Optional[Any] = None,
    new_client_order_id: Any = "",
    recv_window: Any = 5000,
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
    symbol: Any,
    side: Any,
    order_type: Any,
    volume: Any,
    price: Optional[Any] = None,
    new_client_order_id: Any = "",
    recv_window: Any = 5000,
    trigger_price: Optional[Any] = None,
):
    """
    创建真实订单 - 【纯净加固版：强制使用自定义字符串ID】
    """
    # 强制生成带字母的安全 ID，彻底断绝 JS 精度丢失。
    # 格式如：ZKE-AI-SELL-a1b2
    safe_cid = f"ZKE-AI-{str(side).upper()}-{str(uuid.uuid4())[:4]}"
    
    data = prepare_order(registry, symbol, volume, price, order_type)

    result = private_api.create_order(
        symbol=data["api_symbol"],
        volume=data["volume"],
        side=side,
        order_type=order_type,
        price=data["price"],
        new_client_order_id=safe_cid,
        recv_window=recv_window,
    )

    # 结果处理：确保 AI 看到的 clientOrderId 是安全的字符串
    if isinstance(result, dict):
        result["clientOrderId"] = str(safe_cid)
        # 隐藏可能会导致 AI 幻觉的长数字 orderId
        if "orderId" in result:
            result["_original_order_id"] = str(result.pop("orderId")) 

    return data, result


def cancel_order(
    private_api,
    registry,
    symbol: Any,
    order_id: Optional[Any] = None,
    client_order_id: Optional[Any] = None,
):
    """
    撤销订单 - 【纯净加固版：仅支持自定义ID，完全屏蔽数字ID风险】
    """
    api_symbol = registry.get_api_symbol(symbol)

    # 逻辑简化：无论 AI 传到哪个字段，只要带 ZKE 前缀，我们就当做 client_order_id 处理
    final_cid = None
    if client_order_id and str(client_order_id).startswith("ZKE"):
        final_cid = str(client_order_id).strip()
    elif order_id and str(order_id).startswith("ZKE"):
        final_cid = str(order_id).strip()

    if not final_cid:
        raise ValueError("撤单失败：未检测到以 'ZKE-AI-' 开头的有效自定义 ID")

    # 物理屏蔽 order_id 参数，只传 client_order_id
    return private_api.cancel_order(
        api_symbol,
        order_id=None,
        client_order_id=final_cid,
    )


def open_orders(private_api, registry, symbol: Any, limit: Any = 100):
    """
    查询当前挂单 - 【纯净加固版：确保 clientOrderId 可读】
    """
    api_symbol = registry.get_api_symbol(symbol)
    
    safe_limit = int(limit) if limit is not None and str(limit).strip() != "" else 100
    
    orders = private_api.open_orders(api_symbol, limit=safe_limit)

    # 遍历列表，确保每个订单的 clientOrderId 都是干净的字符串供 AI 使用
    if isinstance(orders, list):
        for o in orders:
            if "clientOrderId" in o:
                o["clientOrderId"] = str(o["clientOrderId"])
            # 同样隐藏容易爆精度的数字 ID，强制 AI 关注 clientOrderId
            if "orderId" in o:
                o["_original_order_id"] = str(o.pop("orderId"))

    return orders

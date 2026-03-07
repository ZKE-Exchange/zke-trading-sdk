# /www/wwwroot/zke-trading/tools/margin_private.py

from typing import Any, Dict, Optional


class MarginPrivateApi:
    """
    杠杆私有接口封装

    目标接口：
    - POST /sapi/v1/margin/order
    - GET  /sapi/v1/margin/order
    - POST /sapi/v1/margin/cancel
    - GET  /sapi/v1/margin/openOrders
    - GET  /sapi/v1/margin/myTrades

    说明：
    由于你现有 zke_client.py 的底层方法名我这里无法直接读到，
    所以这里做了一个“自适应调用”：
    会优先尝试常见的 signed get/post 方法名。
    """

    def __init__(self, client):
        self.client = client

    # ---------------------------------------------------------
    # 内部：适配不同 zke_client 写法
    # ---------------------------------------------------------

    def _signed_get(self, path: str, params: Optional[Dict[str, Any]] = None):
        params = params or {}

        # 1) 常见写法：get_signed(path, params)
        if hasattr(self.client, "get_signed"):
            return self.client.get_signed(path, params)

        # 2) 常见写法：signed_get(path, params)
        if hasattr(self.client, "signed_get"):
            return self.client.signed_get(path, params)

        # 3) 常见写法：private_get(path, params)
        if hasattr(self.client, "private_get"):
            return self.client.private_get(path, params)

        # 4) 常见写法：auth_get(path, params)
        if hasattr(self.client, "auth_get"):
            return self.client.auth_get(path, params)

        # 5) 常见写法：request(method, path, params=..., signed=True)
        if hasattr(self.client, "request"):
            return self.client.request("GET", path, params=params, signed=True)

        # 6) 常见写法：_request(method, path, params=..., signed=True)
        if hasattr(self.client, "_request"):
            return self.client._request("GET", path, params=params, signed=True)

        raise RuntimeError(
            "zke_client.py 中未找到可用的 signed GET 方法，请检查底层客户端实现。"
        )

    def _signed_post(self, path: str, body: Optional[Dict[str, Any]] = None):
        body = body or {}

        # 1) 常见写法：post_signed(path, body)
        if hasattr(self.client, "post_signed"):
            return self.client.post_signed(path, body)

        # 2) 常见写法：signed_post(path, body)
        if hasattr(self.client, "signed_post"):
            return self.client.signed_post(path, body)

        # 3) 常见写法：private_post(path, body)
        if hasattr(self.client, "private_post"):
            return self.client.private_post(path, body)

        # 4) 常见写法：auth_post(path, body)
        if hasattr(self.client, "auth_post"):
            return self.client.auth_post(path, body)

        # 5) 常见写法：request(method, path, json/body=..., signed=True)
        if hasattr(self.client, "request"):
            try:
                return self.client.request("POST", path, json=body, signed=True)
            except TypeError:
                return self.client.request("POST", path, body=body, signed=True)

        # 6) 常见写法：_request(method, path, json/body=..., signed=True)
        if hasattr(self.client, "_request"):
            try:
                return self.client._request("POST", path, json=body, signed=True)
            except TypeError:
                return self.client._request("POST", path, body=body, signed=True)

        raise RuntimeError(
            "zke_client.py 中未找到可用的 signed POST 方法，请检查底层客户端实现。"
        )

    # ---------------------------------------------------------
    # 杠杆接口
    # ---------------------------------------------------------

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        volume,
        price=None,
        new_client_order_id: Optional[str] = None,
        recvwindow: Optional[int] = None,
    ):
        body = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "volume": volume,
        }

        if price is not None:
            body["price"] = price

        if new_client_order_id:
            body["newClientOrderId"] = new_client_order_id

        if recvwindow is not None:
            body["recvwindow"] = recvwindow

        return self._signed_post("/sapi/v1/margin/order", body)

    def order_query(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
    ):
        params = {
            "symbol": symbol,
        }

        if order_id:
            params["orderId"] = order_id

        if new_client_order_id:
            params["newClientOrderId"] = new_client_order_id

        return self._signed_get("/sapi/v1/margin/order", params)

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
    ):
        body = {
            "symbol": symbol,
        }

        if order_id:
            body["orderId"] = order_id

        if new_client_order_id:
            body["newClientOrderId"] = new_client_order_id

        return self._signed_post("/sapi/v1/margin/cancel", body)

    def open_orders(self, symbol: str, limit: Optional[int] = None):
        params = {
            "symbol": symbol,
        }

        if limit is not None:
            params["limit"] = limit

        return self._signed_get("/sapi/v1/margin/openOrders", params)

    def my_trades(
        self,
        symbol: str,
        limit: Optional[int] = None,
        from_id: Optional[str] = None,
    ):
        params = {
            "symbol": symbol,
        }

        if limit is not None:
            params["limit"] = limit

        if from_id is not None:
            params["fromId"] = from_id

        return self._signed_get("/sapi/v1/margin/myTrades", params)
from typing import Any, Dict, Optional

from tools.zke_client import ZKEClient


class MarginPrivateApi:
    """
    杠杆私有接口封装

    新版文档：
    - POST /sapi/v2/margin/order
    - GET  /sapi/v2/margin/order
    - POST /sapi/v2/margin/cancel
    - GET  /sapi/v2/margin/openOrders
    - GET  /sapi/v2/margin/myTrades
    """

    def __init__(self, client: ZKEClient):
        self.client = client

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        volume,
        price=None,
        new_client_order_id: Optional[str] = None,
    ):
        body: Dict[str, Any] = {
            "symbol": symbol,
            "side": str(side).upper(),
            "type": str(order_type).upper(),
            "volume": volume,
        }

        if price is not None:
            body["price"] = price

        if new_client_order_id:
            body["newClientOrderId"] = new_client_order_id

        return self.client.request("POST", "/sapi/v2/margin/order", body=body, signed=True)

    def order_query(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
    ):
        params: Dict[str, Any] = {
            "symbol": symbol,
        }

        if order_id:
            params["orderId"] = order_id

        if new_client_order_id:
            params["newClientOrderId"] = new_client_order_id

        return self.client.request("GET", "/sapi/v2/margin/order", params=params, signed=True)

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
    ):
        body: Dict[str, Any] = {
            "symbol": symbol,
        }

        if order_id:
            body["orderId"] = order_id

        if new_client_order_id:
            body["newClientOrderId"] = new_client_order_id

        return self.client.request("POST", "/sapi/v2/margin/cancel", body=body, signed=True)

    def open_orders(self, symbol: str, limit: Optional[int] = None):
        params: Dict[str, Any] = {
            "symbol": symbol,
        }

        if limit is not None:
            params["limit"] = limit

        return self.client.request("GET", "/sapi/v2/margin/openOrders", params=params, signed=True)

    def my_trades(
        self,
        symbol: str,
        limit: Optional[int] = None,
        from_id: Optional[str] = None,
    ):
        params: Dict[str, Any] = {
            "symbol": symbol,
        }

        if limit is not None:
            params["limit"] = limit

        if from_id is not None:
            params["fromId"] = from_id

        return self.client.request("GET", "/sapi/v2/margin/myTrades", params=params, signed=True)

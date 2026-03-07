from typing import Any, Dict, Optional

from tools.zke_client import ZKEClient
from tools.common import ensure_order_type, ensure_side


class SpotPrivateApi:
    def __init__(self, client: ZKEClient):
        self.client = client

    def account(self) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/account", signed=True)

    def order_query(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        if client_order_id:
            params["newClientorderId"] = client_order_id

        return self.client.request("GET", "/sapi/v1/order", params=params, signed=True)

    def open_orders(self, symbol: str, limit: int = 100) -> Any:
        return self.client.request(
            "GET",
            "/sapi/v1/openOrders",
            params={"symbol": symbol, "limit": limit},
            signed=True
        )

    def my_trades(self, symbol: str, limit: int = 100, from_id: Optional[str] = None) -> Any:
        params: Dict[str, Any] = {"symbol": symbol, "limit": limit}
        if from_id:
            params["fromId"] = from_id

        return self.client.request("GET", "/sapi/v1/myTrades", params=params, signed=True)

    def test_order(
        self,
        symbol: str,
        volume: str,
        side: str,
        order_type: str,
        price: Optional[str] = None,
        new_client_order_id: str = "",
        recvwindow: int = 5000,
    ) -> Dict[str, Any]:
        side = ensure_side(side)
        order_type = ensure_order_type(order_type)

        body: Dict[str, Any] = {
            "symbol": symbol,
            "volume": volume,
            "side": side,
            "type": order_type,
            "recvwindow": recvwindow,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT 订单必须提供 price。")
            body["price"] = price

        if new_client_order_id:
            body["newClientorderId"] = new_client_order_id

        return self.client.request("POST", "/sapi/v1/order/test", body=body, signed=True)

    def create_order(
        self,
        symbol: str,
        volume: str,
        side: str,
        order_type: str,
        price: Optional[str] = None,
        new_client_order_id: str = "",
        recvwindow: int = 5000,
    ) -> Dict[str, Any]:
        side = ensure_side(side)
        order_type = ensure_order_type(order_type)

        body: Dict[str, Any] = {
            "symbol": symbol,
            "volume": volume,
            "side": side,
            "type": order_type,
            "recvwindow": recvwindow,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT 订单必须提供 price。")
            body["price"] = price

        if new_client_order_id:
            body["newClientOrderId"] = new_client_order_id

        return self.client.request("POST", "/sapi/v1/order", body=body, signed=True)

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"symbol": symbol}
        if order_id:
            body["orderId"] = order_id
        if client_order_id:
            body["newClientOrderId"] = client_order_id

        return self.client.request("POST", "/sapi/v1/cancel", body=body, signed=True)

    # =========================================================
    # Withdraw
    # =========================================================

    def withdraw_apply(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起提现

        你当前文档是：
        POST /sapi/v1/withdraw/apply
        """
        return self.client.request(
            "POST",
            "/sapi/v1/withdraw/apply",
            body=body,
            signed=True
        )

    def withdraw_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        查询提现记录

        你当前文档是：
        POST /sapi/v1/withdraw/query
        """
        return self.client.request(
            "POST",
            "/sapi/v1/withdraw/query",
            body=params,
            signed=True
        )
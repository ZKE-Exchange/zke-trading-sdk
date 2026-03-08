from typing import Any, Dict, Optional

from tools.zke_client import ZKEClient
from tools.common import ensure_order_type, ensure_side


class SpotPrivateApi:
    def __init__(self, client: ZKEClient):
        self.client = client

    # =========================================================
    # Account
    # =========================================================

    def account(self) -> Dict[str, Any]:
        """
        账户信息
        文档：
        GET /sapi/v1/account
        """
        return self.client.request("GET", "/sapi/v1/account", signed=True)

    # =========================================================
    # Spot Order Query / Open Orders / Trades
    # =========================================================

    def order_query(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询订单
        文档：
        GET /sapi/v2/order
        参数：
        - symbol
        - orderId
        - newClientorderId
        """
        params: Dict[str, Any] = {"symbol": symbol}

        if order_id:
            params["orderId"] = order_id
        if client_order_id:
            # 按你贴的文档字段名保持
            params["newClientorderId"] = client_order_id

        return self.client.request("GET", "/sapi/v2/order", params=params, signed=True)

    def open_orders(self, symbol: str, limit: int = 100) -> Any:
        """
        当前挂单
        文档：
        GET /sapi/v2/openOrders
        """
        return self.client.request(
            "GET",
            "/sapi/v2/openOrders",
            params={"symbol": symbol, "limit": limit},
            signed=True
        )

    def my_trades(self, symbol: str, limit: int = 100, from_id: Optional[str] = None) -> Any:
        """
        现货成交记录
        当前先用 v2，因为你现有调用参数包含 fromId
        文档：
        GET /sapi/v2/myTrades
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "limit": limit
        }

        if from_id:
            params["fromId"] = from_id

        return self.client.request("GET", "/sapi/v2/myTrades", params=params, signed=True)

    # =========================================================
    # Spot Order Create / Test / Cancel
    # =========================================================

    def test_order(
        self,
        symbol: str,
        volume: str,
        side: str,
        order_type: str,
        price: Optional[str] = None,
        new_client_order_id: str = "",
        recv_window: int = 5000,
    ) -> Dict[str, Any]:
        """
        测试下单
        文档：
        POST /sapi/v2/order/test
        """
        side = ensure_side(side)
        order_type = ensure_order_type(order_type)

        body: Dict[str, Any] = {
            "symbol": symbol,
            "volume": volume,
            "side": side,
            "type": order_type,
            "recvWindow": recv_window,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT 订单必须提供 price。")
            body["price"] = price

        if new_client_order_id:
            # 按你贴的 test 文档字段名保持
            body["newClientorderId"] = new_client_order_id

        return self.client.request("POST", "/sapi/v2/order/test", body=body, signed=True)

    def create_order(
        self,
        symbol: str,
        volume: str,
        side: str,
        order_type: str,
        price: Optional[str] = None,
        new_client_order_id: str = "",
        recv_window: int = 5000,
        trigger_price: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建订单
        文档：
        POST /sapi/v2/order
        """
        side = ensure_side(side)
        order_type = ensure_order_type(order_type)

        body: Dict[str, Any] = {
            "symbol": symbol,
            "volume": volume,
            "side": side,
            "type": order_type,
            "recvWindow": recv_window,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT 订单必须提供 price。")
            body["price"] = price

        # STOP 单时，文档要求 price + triggerPrice
        if order_type == "STOP":
            if price is None or trigger_price is None:
                raise ValueError("STOP 订单必须同时提供 price 和 trigger_price。")
            body["price"] = price
            body["triggerPrice"] = trigger_price

        if new_client_order_id:
            body["newClientOrderId"] = new_client_order_id

        return self.client.request("POST", "/sapi/v2/order", body=body, signed=True)

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        撤单
        文档：
        POST /sapi/v2/cancel
        """
        body: Dict[str, Any] = {"symbol": symbol}

        if order_id:
            body["orderId"] = order_id
        if client_order_id:
            body["newClientOrderId"] = client_order_id

        return self.client.request("POST", "/sapi/v2/cancel", body=body, signed=True)

    # =========================================================
    # Withdraw
    # =========================================================

    def withdraw_apply(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起提现
        文档：
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
        文档：
        POST /sapi/v1/withdraw/query
        """
        return self.client.request(
            "POST",
            "/sapi/v1/withdraw/query",
            body=params,
            signed=True
        )

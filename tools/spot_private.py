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

    def exchange_account(self) -> Dict[str, Any]:
        """
        查询用户现货账户资产
        文档：
        POST /sapi/v1/asset/exchange/account
        请求体：{}
        """
        return self.client.request(
            "POST",
            "/sapi/v1/asset/exchange/account",
            body={},
            signed=True,
        )

    def account_by_type(self, account_type: str) -> Dict[str, Any]:
        """
        查询用户可划转资产 / 指定账户资产
        文档：
        POST /sapi/v1/asset/account/by_type

        accountType:
        1: spot
        2: isolated
        3: cross
        4: otc
        5: contract
        """
        body = {
            "accountType": str(account_type)
        }
        return self.client.request(
            "POST",
            "/sapi/v1/asset/account/by_type",
            body=body,
            signed=True,
        )

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
            params["orderId"] = str(order_id)
        if client_order_id:
            params["newClientorderId"] = str(client_order_id)

        return self.client.request("GET", "/sapi/v2/order", params=params, signed=True)

    def open_orders(self, symbol: str, limit: int = 100) -> Any:
        """
        当前挂单
        文档：
        GET /sapi/v2/openOrders
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "limit": int(limit),
        }
        return self.client.request(
            "GET",
            "/sapi/v2/openOrders",
            params=params,
            signed=True
        )

    def my_trades(self, symbol: str, limit: int = 100, from_id: Optional[str] = None) -> Any:
        """
        现货成交记录 v2
        文档：
        GET /sapi/v2/myTrades
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "limit": int(limit),
        }

        if from_id:
            params["fromId"] = str(from_id)

        return self.client.request("GET", "/sapi/v2/myTrades", params=params, signed=True)

    def my_trades_v3(
        self,
        symbol: Optional[str] = None,
        limit: int = 50,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> Any:
        """
        现货成交记录 v3
        文档：
        GET /sapi/v3/myTrades

        说明：
        - symbol 可选；不传时会更高权重
        - startTime / endTime 按文档为最近 6 个月内，区间 <= 7 天
        """
        params: Dict[str, Any] = {
            "limit": int(limit),
        }

        if symbol:
            params["symbol"] = symbol
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)

        return self.client.request("GET", "/sapi/v3/myTrades", params=params, signed=True)

    def history_orders(
        self,
        symbol: Optional[str] = None,
        limit: int = 50,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> Any:
        """
        现货历史订单
        文档：
        GET /sapi/v3/historyOrders

        说明：
        - symbol 可选；不传时会更高权重
        - startTime / endTime 按文档为最近 6 个月内，区间 <= 7 天
        """
        params: Dict[str, Any] = {
            "limit": int(limit),
        }

        if symbol:
            params["symbol"] = symbol
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)

        return self.client.request("GET", "/sapi/v3/historyOrders", params=params, signed=True)

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
            "volume": str(volume),
            "side": side,
            "type": order_type,
            "recvWindow": int(recv_window),
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT 订单必须提供 price。")
            body["price"] = str(price)

        if new_client_order_id:
            body["newClientorderId"] = str(new_client_order_id)

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
    ) -> Dict[str, Any]:
        """
        创建订单
        文档：
        POST /sapi/v2/order

        当前按你现有 common.py，仅严格支持 LIMIT / MARKET
        """
        side = ensure_side(side)
        order_type = ensure_order_type(order_type)

        body: Dict[str, Any] = {
            "symbol": symbol,
            "volume": str(volume),
            "side": side,
            "type": order_type,
            "recvWindow": int(recv_window),
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT 订单必须提供 price。")
            body["price"] = str(price)

        if new_client_order_id:
            body["newClientOrderId"] = str(new_client_order_id)

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
            body["orderId"] = str(order_id)
        if client_order_id:
            body["newClientOrderId"] = str(client_order_id)

        return self.client.request("POST", "/sapi/v2/cancel", body=body, signed=True)

    # =========================================================
    # Asset Transfer
    # =========================================================

    def asset_transfer(
        self,
        coin_symbol: str,
        amount: str,
        from_account: str,
        to_account: str,
    ) -> Dict[str, Any]:
        """
        账户划转
        文档：
        POST /sapi/v1/asset/transfer

        fromAccount / toAccount:
        EXCHANGE / FUTURE
        """
        body: Dict[str, Any] = {
            "coinSymbol": str(coin_symbol),
            "amount": str(amount),
            "fromAccount": str(from_account),
            "toAccount": str(to_account),
        }

        return self.client.request(
            "POST",
            "/sapi/v1/asset/transfer",
            body=body,
            signed=True,
        )

    def asset_transfer_query(
        self,
        transfer_id: Optional[str] = None,
        coin_symbol: Optional[str] = None,
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        划转记录查询
        文档：
        POST /sapi/v1/asset/transferQuery
        """
        body: Dict[str, Any] = {}

        if transfer_id:
            body["transferId"] = str(transfer_id)
        if coin_symbol:
            body["coinSymbol"] = str(coin_symbol)
        if from_account:
            body["fromAccount"] = str(from_account)
        if to_account:
            body["toAccount"] = str(to_account)
        if start_time is not None:
            body["startTime"] = int(start_time)
        if end_time is not None:
            body["endTime"] = int(end_time)
        if page is not None:
            body["page"] = int(page)
        if limit is not None:
            body["limit"] = int(limit)

        return self.client.request(
            "POST",
            "/sapi/v1/asset/transferQuery",
            body=body,
            signed=True,
        )

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

class FuturesPrivateApi:
    def __init__(self, client):
        self.client = client

    def account(self):
        return self.client.request("GET", "/fapi/v1/account", signed=True)

    def order(self, contract_name: str, order_id: str = None, client_order_id: str = None):
        params = {"contractName": contract_name}
        if order_id:
            params["orderId"] = order_id
        if client_order_id:
            params["clientOrderId"] = client_order_id
        return self.client.request("GET", "/fapi/v1/order", params=params, signed=True)

    def open_orders(self, contract_name: str):
        return self.client.request(
            "GET",
            "/fapi/v1/openOrders",
            params={"contractName": contract_name},
            signed=True
        )

    def my_trades(self, contract_name: str, limit: int = 100, from_id: int = None):
        params = {
            "contractName": contract_name,
            "limit": limit
        }
        if from_id is not None:
            params["fromId"] = from_id
        return self.client.request("GET", "/fapi/v1/myTrades", params=params, signed=True)

    def order_historical(self, contract_name: str, limit: int = 100, from_id: int = None):
        body = {
            "contractName": contract_name,
            "limit": limit
        }
        if from_id is not None:
            body["fromId"] = from_id
        return self.client.request("POST", "/fapi/v1/orderHistorical", body=body, signed=True)

    def profit_historical(self, contract_name: str, limit: int = 100, from_id: int = None):
        body = {
            "contractName": contract_name,
            "limit": limit
        }
        if from_id is not None:
            body["fromId"] = from_id
        return self.client.request("POST", "/fapi/v1/profitHistorical", body=body, signed=True)

    def create_order(
        self,
        contract_name: str,
        side: str,
        open_action: str,
        position_type: int,
        order_type: str,
        volume: str,
        price: str = None,
        client_order_id: str = "",
        time_in_force: str = ""
    ):
        body = {
            "contractName": contract_name,
            "side": side.upper(),
            "open": open_action.upper(),
            "positionType": position_type,
            "type": order_type.upper(),
            "volume": volume
        }

        if price is not None:
            body["price"] = price
        if client_order_id:
            body["clientOrderId"] = client_order_id
        if time_in_force:
            body["timeInForce"] = time_in_force

        return self.client.request("POST", "/fapi/v1/order", body=body, signed=True)

    def cancel_order(self, contract_name: str, order_id: str):
        body = {
            "contractName": contract_name,
            "orderId": order_id
        }
        return self.client.request("POST", "/fapi/v1/cancel", body=body, signed=True)
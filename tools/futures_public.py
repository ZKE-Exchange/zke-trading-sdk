from tools.common import ensure_futures_interval


class FuturesPublicApi:
    def __init__(self, client):
        self.client = client

    def ping(self):
        return self.client.request("GET", "/fapi/v1/ping")

    def time(self):
        return self.client.request("GET", "/fapi/v1/time")

    def contracts(self):
        return self.client.request("GET", "/fapi/v1/contracts")

    def ticker(self, contract_name: str):
        return self.client.request(
            "GET",
            "/fapi/v1/ticker",
            params={"contractName": contract_name}
        )

    def depth(self, contract_name: str, limit: int = 100):
        return self.client.request(
            "GET",
            "/fapi/v1/depth",
            params={"contractName": contract_name, "limit": limit}
        )

    def index(self, contract_name: str):
        return self.client.request(
            "GET",
            "/fapi/v1/index",
            params={"contractName": contract_name}
        )

    def klines(self, contract_name: str, interval: str, limit: int = 100):
        interval = ensure_futures_interval(interval)
        return self.client.request(
            "GET",
            "/fapi/v1/klines",
            params={
                "contractName": contract_name,
                "interval": interval,
                "limit": limit
            }
        )
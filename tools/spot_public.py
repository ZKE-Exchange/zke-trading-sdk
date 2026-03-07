from typing import Any, Dict

from tools.zke_client import ZKEClient
from tools.common import ensure_spot_interval


class SpotPublicApi:
    def __init__(self, client: ZKEClient):
        self.client = client

    def ping(self) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/ping")

    def time(self) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/time")

    def symbols(self) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/symbols")

    def ticker(self, symbol: str) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/ticker", params={"symbol": symbol})

    def depth(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/depth", params={"symbol": symbol, "limit": limit})

    def trades(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        return self.client.request("GET", "/sapi/v1/trades", params={"symbol": symbol, "limit": limit})

    def klines(self, symbol: str, interval: str) -> Any:
        interval = ensure_spot_interval(interval)
        return self.client.request("GET", "/sapi/v1/klines", params={"symbol": symbol, "interval": interval})
from typing import Any, Dict, List, Union

from tools.common import ensure_futures_interval
from tools.zke_client import ZKEClient


class FuturesPublicApi:
    def __init__(self, client: ZKEClient):
        self.client = client

    def ping(self) -> Dict[str, Any]:
        """
        GET /fapi/v1/ping
        """
        return self.client.request("GET", "/fapi/v1/ping")

    def time(self) -> Dict[str, Any]:
        """
        GET /fapi/v1/time
        """
        return self.client.request("GET", "/fapi/v1/time")

    def contracts(self) -> List[Dict[str, Any]]:
        """
        GET /fapi/v1/contracts
        """
        return self.client.request("GET", "/fapi/v1/contracts")

    def ticker(self, contract_name: str) -> Dict[str, Any]:
        """
        GET /fapi/v1/ticker
        params: contractName
        """
        return self.client.request(
            "GET",
            "/fapi/v1/ticker",
            params={"contractName": contract_name}
        )

    def ticker_all(self) -> Dict[str, Any]:
        """
        GET /fapi/v1/ticker_all
        """
        return self.client.request("GET", "/fapi/v1/ticker_all")

    def depth(self, contract_name: str, limit: int = 100) -> Dict[str, Any]:
        """
        GET /fapi/v1/depth
        params: contractName, limit
        """
        return self.client.request(
            "GET",
            "/fapi/v1/depth",
            params={"contractName": contract_name, "limit": limit}
        )

    def index(self, contract_name: str) -> Dict[str, Any]:
        """
        GET /fapi/v1/index
        params: contractName
        """
        return self.client.request(
            "GET",
            "/fapi/v1/index",
            params={"contractName": contract_name}
        )

    def klines(
        self,
        contract_name: str,
        interval: str,
        limit: int = 100
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        GET /fapi/v1/klines
        params: contractName, interval, limit
        """
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

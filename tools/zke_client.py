import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests


class ZKEApiError(Exception):
    def __init__(self, code: Any, msg: str, payload: Optional[dict] = None):
        self.code = code
        self.msg = msg
        self.payload = payload or {}
        super().__init__(f"ZKE API Error {code}: {msg}")


class ZKEClient:
    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        api_secret: str = "",
        recv_window: int = 5000,
        timeout: int = 15,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.api_secret = api_secret or ""
        self.recv_window = recv_window
        self.timeout = timeout
        self.session = requests.Session()

    def _headers(self, signed: bool = False) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if signed and self.api_key:
            headers["X-BH-APIKEY"] = self.api_key
        return headers

    def _sign_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_secret:
            return params

        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        signed = dict(params)
        signed["signature"] = signature
        return signed

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Any:
        method = method.upper()
        params = params or {}
        body = body or {}

        url = f"{self.base_url}{path}"

        if signed:
            ts = int(time.time() * 1000)

            if method == "GET":
                params = dict(params)
                params.setdefault("timestamp", ts)
                params.setdefault("recvwindow", self.recv_window)
                params = self._sign_params(params)
            else:
                body = dict(body)
                body.setdefault("timestamp", ts)
                body.setdefault("recvwindow", self.recv_window)
                body = self._sign_params(body)

        resp = self.session.request(
            method=method,
            url=url,
            params=params if method == "GET" else None,
            json=body if method != "GET" else None,
            headers=self._headers(signed=signed),
            timeout=self.timeout,
        )

        text = resp.text.strip()

        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(f"HTTP {resp.status_code} 返回非JSON: {text}")

        if isinstance(data, dict):
            code = data.get("code")
            msg = data.get("msg", "")

            if code is not None and str(code) not in ("0", "200"):
                raise ZKEApiError(code, msg, data)

        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {text}")

        return data

    def explain_error(self, err: Exception) -> str:
        if isinstance(err, ZKEApiError):
            return f"ZKE API Error {err.code}: {err.msg}"
        return str(err)
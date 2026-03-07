import json
import threading
import time
from typing import Callable, List, Optional

import websocket

from .ws_parser import decode_ws_message, is_ping_message, build_pong


class ZKEWebSocketClient:
    def __init__(
        self,
        url: str,
        subscriptions: List[dict],
        on_message: Optional[Callable] = None,
        reconnect: bool = True,
        reconnect_delay: int = 5,
        debug: bool = False,
    ):
        self.url = url
        self.subscriptions = subscriptions
        self.on_message_cb = on_message
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        self.debug = debug

        self.ws_app = None
        self._stop = False
        self._thread = None

    def log(self, *args):
        if self.debug:
            print("[WS]", *args)

    def _on_open(self, ws):
        self.log("connected:", self.url)
        for sub in self.subscriptions:
            self.send(sub)

    def _on_message(self, ws, message):
        data = decode_ws_message(message)

        if data is None:
            return

        if is_ping_message(data):
            pong = build_pong(data)
            if pong:
                self.send(pong)
            return

        if self.on_message_cb:
            self.on_message_cb(data)

    def _on_error(self, ws, error):
        print("[WS ERROR]", error)

    def _on_close(self, ws, code, msg):
        print(f"[WS CLOSED] code={code} msg={msg}")

    def send(self, payload: dict):
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            text = json.dumps(payload, ensure_ascii=False)
            self.log("send:", text)
            self.ws_app.send(text)

    def run_forever(self):
        while not self._stop:
            try:
                self.ws_app = websocket.WebSocketApp(
                    self.url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self.ws_app.run_forever()
            except KeyboardInterrupt:
                self._stop = True
                raise
            except Exception as e:
                print("[WS RUN ERROR]", e)

            if self._stop:
                break

            if not self.reconnect:
                break

            print(f"[WS] reconnect after {self.reconnect_delay}s ...")
            time.sleep(self.reconnect_delay)

    def start_background(self):
        self._thread = threading.Thread(target=self.run_forever, daemon=True)
        self._thread.start()
        return self._thread

    def close(self):
        self._stop = True
        if self.ws_app:
            try:
                self.ws_app.close()
            except Exception:
                pass
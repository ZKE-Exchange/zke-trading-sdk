import json
import time
from typing import Optional

from .ws_client import ZKEWebSocketClient
from .ws_parser import normalize_ws_message


def _print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _norm_symbol(symbol: str) -> str:
    return str(symbol).strip().lower()


def build_sub(channel: str, cb_id: str = "1") -> dict:
    return {
        "event": "sub",
        "params": {
            "channel": channel,
            "cb_id": cb_id,
        }
    }


def build_unsub(channel: str, cb_id: str = "1") -> dict:
    return {
        "event": "unsub",
        "params": {
            "channel": channel,
            "cb_id": cb_id,
        }
    }


def build_req(channel: str, cb_id: str = "1", end_idx: Optional[str] = None, page_size: Optional[int] = None) -> dict:
    params = {
        "channel": channel,
        "cb_id": cb_id,
    }

    if end_idx is not None:
        params["endIdx"] = str(end_idx)

    if page_size is not None:
        params["pageSize"] = int(page_size)

    return {
        "event": "req",
        "params": params,
    }


def build_ticker_sub(symbol: str, cb_id: str = "1") -> dict:
    symbol = _norm_symbol(symbol)
    return build_sub(f"market_{symbol}_ticker", cb_id)


def build_depth_sub(symbol: str, step: str = "step0", cb_id: str = "1") -> dict:
    symbol = _norm_symbol(symbol)
    return build_sub(f"market_{symbol}_depth_{step}", cb_id)


def build_kline_sub(symbol: str, interval: str = "1min", cb_id: str = "1") -> dict:
    symbol = _norm_symbol(symbol)
    return build_sub(f"market_{symbol}_kline_{interval}", cb_id)


def build_trade_sub(symbol: str, cb_id: str = "1") -> dict:
    symbol = _norm_symbol(symbol)
    return build_sub(f"market_{symbol}_trade_ticker", cb_id)


def build_kline_req(symbol: str, interval: str = "1min", cb_id: str = "1", end_idx: Optional[str] = None, page_size: Optional[int] = None) -> dict:
    symbol = _norm_symbol(symbol)
    return build_req(f"market_{symbol}_kline_{interval}", cb_id, end_idx=end_idx, page_size=page_size)


def build_trade_req(symbol: str, cb_id: str = "1") -> dict:
    symbol = _norm_symbol(symbol)
    return build_req(f"market_{symbol}_trade_ticker", cb_id)


def default_message_handler(data):
    normalized = normalize_ws_message(data)
    kind = normalized.get("type", "unknown").upper()
    print(f"\n===== WS {kind} =====")
    _print_json(normalized)


def run_ws_once(
    ws_url: str,
    subscriptions: list,
    seconds: int = 30,
    debug: bool = False,
):
    client = ZKEWebSocketClient(
        url=ws_url,
        subscriptions=subscriptions,
        on_message=default_message_handler,
        reconnect=True,
        reconnect_delay=3,
        debug=debug,
    )

    thread = client.start_background()

    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

    if thread:
        thread.join(timeout=2)


def run_ws_ticker(ws_url: str, symbol: str, seconds: int = 30, debug: bool = False):
    run_ws_once(
        ws_url=ws_url,
        subscriptions=[build_ticker_sub(symbol)],
        seconds=seconds,
        debug=debug,
    )


def run_ws_depth(ws_url: str, symbol: str, step: str = "step0", seconds: int = 30, debug: bool = False):
    run_ws_once(
        ws_url=ws_url,
        subscriptions=[build_depth_sub(symbol, step=step)],
        seconds=seconds,
        debug=debug,
    )


def run_ws_kline(ws_url: str, symbol: str, interval: str = "1min", seconds: int = 30, debug: bool = False):
    run_ws_once(
        ws_url=ws_url,
        subscriptions=[build_kline_sub(symbol, interval=interval)],
        seconds=seconds,
        debug=debug,
    )


def run_ws_trades(ws_url: str, symbol: str, seconds: int = 30, debug: bool = False):
    run_ws_once(
        ws_url=ws_url,
        subscriptions=[build_trade_sub(symbol)],
        seconds=seconds,
        debug=debug,
    )


def run_ws_kline_req(
    ws_url: str,
    symbol: str,
    interval: str = "1min",
    seconds: int = 10,
    end_idx: Optional[str] = None,
    page_size: Optional[int] = None,
    debug: bool = False,
):
    run_ws_once(
        ws_url=ws_url,
        subscriptions=[build_kline_req(symbol, interval=interval, end_idx=end_idx, page_size=page_size)],
        seconds=seconds,
        debug=debug,
    )


def run_ws_trade_req(
    ws_url: str,
    symbol: str,
    seconds: int = 10,
    debug: bool = False,
):
    run_ws_once(
        ws_url=ws_url,
        subscriptions=[build_trade_req(symbol)],
        seconds=seconds,
        debug=debug,
    )
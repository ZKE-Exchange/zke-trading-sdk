import gzip
import json
from io import BytesIO
from typing import Any


def decode_ws_message(message: Any):
    """
    处理 websocket 原始消息：
    - bytes: 尝试 gzip 解压
    - str: 直接 json 解析
    """
    if isinstance(message, bytes):
        try:
            with gzip.GzipFile(fileobj=BytesIO(message)) as f:
                text = f.read().decode("utf-8")
        except Exception:
            text = message.decode("utf-8", errors="ignore")
    else:
        text = str(message)

    text = text.strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        return {"raw_text": text}


def is_ping_message(data) -> bool:
    if not isinstance(data, dict):
        return False
    return "ping" in data


def build_pong(data):
    if not isinstance(data, dict):
        return None

    if "ping" in data:
        return {"pong": data["ping"]}

    return None


def get_channel(data) -> str:
    if not isinstance(data, dict):
        return ""
    return str(data.get("channel", "")).strip()


def get_event_rep(data) -> str:
    if not isinstance(data, dict):
        return ""
    return str(data.get("event_rep", "")).strip().lower()


def detect_channel_type(data):
    """
    根据 ZKE WS 文档识别消息类型
    """
    if not isinstance(data, dict):
        return "unknown"

    channel = get_channel(data).lower()
    event_rep = get_event_rep(data)

    if "ticker" in channel and "trade_ticker" not in channel:
        return "ticker"

    if "depth" in channel:
        return "depth"

    if "kline" in channel:
        return "kline"

    if "trade_ticker" in channel:
        return "trade"

    if event_rep == "rep":
        return "reply"

    return "unknown"


def normalize_ws_message(data):
    """
    统一整理 ZKE WS 返回，方便 CLI 打印
    """
    if not isinstance(data, dict):
        return {"type": "unknown", "raw": data}

    kind = detect_channel_type(data)
    channel = get_channel(data)
    ts = data.get("ts")
    tick = data.get("tick")
    rows = data.get("data")
    status = data.get("status")
    cb_id = data.get("cb_id")

    result = {
        "type": kind,
        "channel": channel,
        "ts": ts,
    }

    if cb_id is not None:
        result["cb_id"] = cb_id

    if status is not None:
        result["status"] = status

    if isinstance(tick, dict):
        result["tick"] = tick

    if isinstance(rows, list):
        result["data"] = rows
        result["count"] = len(rows)

    if "raw_text" in data:
        result["raw_text"] = data["raw_text"]

    result["raw"] = data
    return result
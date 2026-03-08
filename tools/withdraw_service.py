import time
import uuid
from typing import Optional


def _gen_withdraw_order_id() -> str:
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:8]
    return f"wd_{ts}_{rand}"


def apply_withdraw(
    api,
    coin,
    address,
    amount,
    memo: Optional[str] = None,
    withdraw_order_id: Optional[str] = None,
):
    """
    发起提现

    新版文档:
    POST /sapi/v1/withdraw/apply

    body:
    - symbol
    - address
    - amount
    - withdrawOrderId
    - label (可选)
    """
    if not withdraw_order_id:
        withdraw_order_id = _gen_withdraw_order_id()

    body = {
        "symbol": str(coin),
        "address": address,
        "amount": amount,
        "withdrawOrderId": withdraw_order_id,
    }

    if memo:
        body["label"] = memo

    result = api.withdraw_apply(body)

    return {
        "coin": str(coin),
        "address": address,
        "amount": amount,
        "memo": memo,
        "withdraw_order_id": withdraw_order_id,
        "result": result
    }


def withdraw_history(
    api,
    coin: Optional[str] = None,
    withdraw_id: Optional[str] = None,
    withdraw_order_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: Optional[int] = None,
    limit: int = 20,
):
    """
    查询提现记录

    新版文档:
    POST /sapi/v1/withdraw/query

    body 可选:
    - symbol
    - withdrawId
    - withdrawOrderId
    - startTime
    - endTime
    - page
    """
    params = {}

    if coin:
        params["symbol"] = str(coin)

    if withdraw_id:
        params["withdrawId"] = str(withdraw_id)

    if withdraw_order_id:
        params["withdrawOrderId"] = str(withdraw_order_id)

    if start_time:
        params["startTime"] = str(start_time)

    if end_time:
        params["endTime"] = str(end_time)

    if page is not None:
        params["page"] = page

    result = api.withdraw_history(params)

    rows = []

    if isinstance(result, dict):
        data = result.get("data")

        if isinstance(data, dict):
            if isinstance(data.get("withdrawList"), list):
                rows = data["withdrawList"]
            elif isinstance(data.get("list"), list):
                rows = data["list"]

        elif isinstance(data, list):
            rows = data

        elif isinstance(result.get("list"), list):
            rows = result["list"]

    elif isinstance(result, list):
        rows = result

    clean = []

    for r in rows:
        clean.append({
            "coin": r.get("symbol"),
            "amount": r.get("amount"),
            "address": r.get("address"),
            "withdraw_id": r.get("id"),
            "withdraw_order_id": r.get("withdrawOrderId"),
            "txid": r.get("txId") or r.get("txid"),
            "fee": r.get("fee"),
            "status": r.get("status"),
            "info": r.get("info"),
            "time": r.get("applyTime") or r.get("ctime") or r.get("time"),
            "raw": r
        })

    if isinstance(limit, int) and limit > 0:
        return clean[:limit]

    return clean

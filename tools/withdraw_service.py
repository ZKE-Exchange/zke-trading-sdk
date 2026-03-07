# /www/wwwroot/zke-trading/tools/withdraw_service.py

import time
import uuid


def _gen_withdraw_order_id() -> str:
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:8]
    return f"wd_{ts}_{rand}"


def apply_withdraw(api, coin, address, amount, network=None, memo=None, withdraw_order_id=None):
    if not withdraw_order_id:
        withdraw_order_id = _gen_withdraw_order_id()

    body = {
        "symbol": coin,
        "address": address,
        "amount": amount,
        "withdrawOrderId": withdraw_order_id,
    }

    if network:
        body["network"] = network

    if memo:
        body["label"] = memo

    result = api.withdraw_apply(body)

    return {
        "coin": coin,
        "address": address,
        "amount": amount,
        "network": network,
        "memo": memo,
        "withdraw_order_id": withdraw_order_id,
        "result": result
    }


def withdraw_history(api, coin=None, limit=20):
    """
    查询提现记录

    这里改成最保守调用：
    - 不默认传 page
    - 不默认传 limit
    - 只在用户明确给 coin 时传 symbol
    """
    params = {}

    if coin:
        params["symbol"] = coin

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
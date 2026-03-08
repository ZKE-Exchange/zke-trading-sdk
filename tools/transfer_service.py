from typing import Any, Dict, List, Optional


VALID_ACCOUNT_TYPES = {"EXCHANGE", "FUTURE"}


def _normalize_account_type(value: str) -> str:
    if value is None:
        raise ValueError("账户类型不能为空。")

    v = str(value).strip().upper()

    if v not in VALID_ACCOUNT_TYPES:
        raise ValueError(f"无效账户类型: {value}，只允许 EXCHANGE / FUTURE")
    return v


def _normalize_transfer_result(result: Any) -> Dict[str, Any]:
    """
    统一整理划转返回
    文档典型成功返回：
    {
        "code": "0",
        "msg": "SUCCESS",
        "data": {
            "transferId": "xxxx"
        }
    }
    """
    if not isinstance(result, dict):
        return {
            "success": False,
            "transfer_id": None,
            "raw": result,
        }

    data = result.get("data")
    transfer_id = None

    if isinstance(data, dict):
        transfer_id = data.get("transferId")

    code = result.get("code")
    msg = result.get("msg")

    return {
        "success": str(code) == "0" if code is not None else True,
        "code": code,
        "msg": msg,
        "transfer_id": transfer_id,
        "raw": result,
    }


def _extract_transfer_rows(result: Any) -> List[Dict[str, Any]]:
    """
    统一提取划转记录列表
    文档典型结构：
    {
        "code": "0",
        "msg": "SUCCESS",
        "data": {
            "list": [...]
        }
    }
    """
    if isinstance(result, list):
        return result

    if not isinstance(result, dict):
        return []

    data = result.get("data")

    if isinstance(data, dict):
        if isinstance(data.get("list"), list):
            return data["list"]

    if isinstance(result.get("list"), list):
        return result["list"]

    return []


def transfer_between_accounts(
    api,
    coin_symbol: str,
    amount: str,
    from_account: str,
    to_account: str,
) -> Dict[str, Any]:
    """
    现货 / 合约 之间划转

    文档：
    POST /sapi/v1/asset/transfer

    fromAccount / toAccount:
    - EXCHANGE
    - FUTURE
    """
    from_acc = _normalize_account_type(from_account)
    to_acc = _normalize_account_type(to_account)

    if from_acc == to_acc:
        raise ValueError("fromAccount 和 toAccount 不能相同。")

    if not coin_symbol:
        raise ValueError("coin_symbol 不能为空。")

    if not amount:
        raise ValueError("amount 不能为空。")

    result = api.asset_transfer(
        coin_symbol=str(coin_symbol).upper(),
        amount=str(amount),
        from_account=from_acc,
        to_account=to_acc,
    )

    normalized = _normalize_transfer_result(result)
    normalized["request"] = {
        "coinSymbol": str(coin_symbol).upper(),
        "amount": str(amount),
        "fromAccount": from_acc,
        "toAccount": to_acc,
    }
    return normalized


def transfer_spot_to_futures(api, coin_symbol: str, amount: str) -> Dict[str, Any]:
    """
    现货 -> 合约
    """
    return transfer_between_accounts(
        api=api,
        coin_symbol=coin_symbol,
        amount=amount,
        from_account="EXCHANGE",
        to_account="FUTURE",
    )


def transfer_futures_to_spot(api, coin_symbol: str, amount: str) -> Dict[str, Any]:
    """
    合约 -> 现货
    """
    return transfer_between_accounts(
        api=api,
        coin_symbol=coin_symbol,
        amount=amount,
        from_account="FUTURE",
        to_account="EXCHANGE",
    )


def query_transfer_history(
    api,
    transfer_id: Optional[str] = None,
    coin_symbol: Optional[str] = None,
    from_account: Optional[str] = None,
    to_account: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
) -> Dict[str, Any]:
    """
    查询划转记录

    文档：
    POST /sapi/v1/asset/transferQuery
    """
    norm_from = _normalize_account_type(from_account) if from_account else None
    norm_to = _normalize_account_type(to_account) if to_account else None

    if not norm_from or not norm_to:
        raise ValueError("查询划转记录时必须提供 from_account 和 to_account，例如 EXCHANGE FUTURE。")

    result = api.asset_transfer_query(
        transfer_id=str(transfer_id) if transfer_id else None,
        coin_symbol=str(coin_symbol).upper() if coin_symbol else None,
        from_account=norm_from,
        to_account=norm_to,
        start_time=int(start_time) if start_time is not None else None,
        end_time=int(end_time) if end_time is not None else None,
        page=int(page) if page is not None else None,
        limit=int(limit) if limit is not None else None,
    )

    rows = _extract_transfer_rows(result)

    clean = []
    for item in rows:
        clean.append({
            "transfer_id": item.get("transferId"),
            "from_account": item.get("fromAccount"),
            "to_account": item.get("toAccount"),
            "coin_symbol": item.get("coinSymbol"),
            "amount": item.get("amount"),
            "status": item.get("status"),
            "create_time": item.get("createTime"),
            "raw": item,
        })

    return {
        "query": {
            "transferId": transfer_id,
            "coinSymbol": str(coin_symbol).upper() if coin_symbol else None,
            "fromAccount": norm_from,
            "toAccount": norm_to,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "limit": limit,
        },
        "records": clean,
        "count": len(clean),
        "raw": result,
    }

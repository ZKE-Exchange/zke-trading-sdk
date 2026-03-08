def extract_account_balances(account_data):
    """
    兼容多种账户返回结构，优先提取 balances 列表
    """
    if isinstance(account_data, list):
        return account_data

    if isinstance(account_data, dict):
        if isinstance(account_data.get("balances"), list):
            return account_data["balances"]

        data = account_data.get("data")
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            if isinstance(data.get("balances"), list):
                return data["balances"]
            if isinstance(data.get("accountList"), list):
                return data["accountList"]

    return []


def filter_nonzero_balances(balances):
    result = []

    for item in balances:
        free_val = str(item.get("free", item.get("normalBalance", "0")))
        locked_val = str(item.get("locked", "0"))

        try:
            free_num = float(free_val)
        except Exception:
            free_num = 0.0

        try:
            locked_num = float(locked_val)
        except Exception:
            locked_num = 0.0

        if free_num != 0.0 or locked_num != 0.0:
            result.append(item)

    return result


def find_asset_balance(balances, asset):
    target = str(asset).upper()

    matched = []

    for x in balances:
        asset_name = str(x.get("asset", "")).upper()
        coin_symbol = str(x.get("coinSymbol", "")).upper()
        coin_symbol_name = str(x.get("coinSymbolName", "")).upper()

        if asset_name == target or coin_symbol == target or coin_symbol_name == target:
            matched.append(x)

    return matched


def get_asset_balance_summary(balances, asset):
    matched = find_asset_balance(balances, asset)

    if not matched:
        return {
            "asset": str(asset).upper(),
            "free": "0",
            "locked": "0"
        }

    item = matched[0]

    asset_name = (
        item.get("asset")
        or item.get("coinSymbolName")
        or item.get("coinSymbol")
        or asset
    )

    free_val = item.get("free", item.get("normalBalance", "0"))
    locked_val = item.get("locked", "0")

    return {
        "asset": str(asset_name).upper(),
        "free": str(free_val),
        "locked": str(locked_val)
    }

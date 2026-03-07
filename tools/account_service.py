def extract_account_balances(account_data):
    if isinstance(account_data, list):
        return account_data

    if isinstance(account_data, dict):
        if isinstance(account_data.get("balances"), list):
            return account_data["balances"]
        if isinstance(account_data.get("data"), list):
            return account_data["data"]

    return []


def filter_nonzero_balances(balances):
    result = []

    for item in balances:
        free_val = str(item.get("free", "0"))
        locked_val = str(item.get("locked", "0"))

        try:
            free_num = float(free_val)
        except Exception:
            free_num = 0

        try:
            locked_num = float(locked_val)
        except Exception:
            locked_num = 0

        if free_num != 0 or locked_num != 0:
            result.append(item)

    return result


def find_asset_balance(balances, asset):
    asset = asset.upper()

    return [
        x for x in balances
        if str(x.get("asset", "")).upper() == asset
    ]


def get_asset_balance_summary(balances, asset):
    matched = find_asset_balance(balances, asset)

    if not matched:
        return {
            "asset": asset.upper(),
            "free": "0",
            "locked": "0"
        }

    item = matched[0]

    return {
        "asset": str(item.get("asset", asset)).upper(),
        "free": str(item.get("free", "0")),
        "locked": str(item.get("locked", "0"))
    }

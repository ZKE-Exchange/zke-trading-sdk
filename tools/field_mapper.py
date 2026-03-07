# tools/field_mapper.py


def map_side(side):
    """
    BUY -> long
    SELL -> short
    """
    if side is None:
        return "-"

    s = str(side).strip().upper()

    if s == "BUY":
        return "long"
    if s == "SELL":
        return "short"

    return s.lower()


def map_open_close(value):
    """
    OPEN -> open
    CLOSE -> close
    """
    if value is None:
        return "-"

    s = str(value).strip().upper()

    if s == "OPEN":
        return "open"
    if s == "CLOSE":
        return "close"

    return s.lower()


def map_position_type(value):
    """
    1 -> cross
    2 -> isolated
    """
    try:
        v = int(value)
    except Exception:
        return str(value)

    if v == 1:
        return "cross"
    if v == 2:
        return "isolated"

    return str(v)


def map_order_status(value):
    """
    futures status:
    0 -> init
    1 -> new
    2 -> filled
    3 -> partial
    4 -> canceled
    5 -> partial_canceled
    6 -> error
    """
    try:
        v = int(value)
    except Exception:
        return str(value)

    mapping = {
        0: "init",
        1: "new",
        2: "filled",
        3: "partial",
        4: "canceled",
        5: "partial_canceled",
        6: "error",
    }

    return mapping.get(v, str(v))


def map_spot_order_status(value):
    """
    spot status text passthrough -> normalized lowercase
    """
    if value is None:
        return "-"

    s = str(value).strip().upper()

    mapping = {
        "NEW": "new",
        "PARTIALLY_FILLED": "partial",
        "FILLED": "filled",
        "CANCELED": "canceled",
        "PENDING_CANCEL": "pending_cancel",
        "REJECTED": "rejected",
    }

    return mapping.get(s, s.lower())


def map_order_type(value):
    """
    LIMIT / MARKET -> lowercase normalized
    some futures historical records may use numbers, keep raw string
    """
    if value is None:
        return "-"

    s = str(value).strip().upper()

    mapping = {
        "LIMIT": "limit",
        "MARKET": "market",
        "IOC": "ioc",
        "FOK": "fok",
        "POST_ONLY": "post_only",
    }

    return mapping.get(s, s.lower())


def map_bool_flag(value):
    """
    True/False -> yes/no
    """
    if isinstance(value, bool):
        return "yes" if value else "no"

    if value is None:
        return "-"

    return str(value)
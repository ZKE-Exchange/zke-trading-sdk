def get_registry(public_api):
    from tools.symbol_utils import SpotSymbolRegistry
    symbols_data = public_api.symbols()
    return SpotSymbolRegistry(symbols_data)


def _resolve_symbols(registry, symbol):
    api_symbol = registry.get_api_symbol(symbol)
    display_symbol = registry.get_display_symbol(symbol)
    return api_symbol, display_symbol


def get_ticker(public_api, registry, symbol):
    api_symbol, _ = _resolve_symbols(registry, symbol)
    return public_api.ticker(api_symbol)


def get_ticker_pretty_data(public_api, registry, symbol):
    api_symbol, display_symbol = _resolve_symbols(registry, symbol)
    ticker_data = public_api.ticker(api_symbol)
    return display_symbol, ticker_data


def get_depth(public_api, registry, symbol, limit=20):
    api_symbol, _ = _resolve_symbols(registry, symbol)
    return public_api.depth(api_symbol, limit)


def get_depth_pretty_data(public_api, registry, symbol, limit=10):
    api_symbol, display_symbol = _resolve_symbols(registry, symbol)
    depth_data = public_api.depth(api_symbol, limit)
    return display_symbol, depth_data


def get_trades(public_api, registry, symbol, limit=20):
    api_symbol, _ = _resolve_symbols(registry, symbol)
    return public_api.trades(api_symbol, limit)


def get_trades_pretty_data(public_api, registry, symbol, limit=20):
    api_symbol, display_symbol = _resolve_symbols(registry, symbol)
    trades = public_api.trades(api_symbol, limit)
    return display_symbol, trades


def get_my_trades_pretty_data(private_api, registry, symbol, limit=10):
    api_symbol, display_symbol = _resolve_symbols(registry, symbol)
    trades = private_api.my_trades(api_symbol, limit)
    return display_symbol, trades


def get_klines(public_api, registry, symbol, interval):
    api_symbol, _ = _resolve_symbols(registry, symbol)
    return public_api.klines(api_symbol, interval)


def get_klines_pretty_data(public_api, registry, symbol, interval):
    api_symbol, display_symbol = _resolve_symbols(registry, symbol)
    klines = public_api.klines(api_symbol, interval)
    return display_symbol, klines

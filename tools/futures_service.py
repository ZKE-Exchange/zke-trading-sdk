class FuturesRegistry:
    def __init__(self, contracts_data):
        if isinstance(contracts_data, list):
            self.contracts = contracts_data
        else:
            self.contracts = []

        self.by_contract = {}
        self.by_simple = {}

        for item in self.contracts:
            contract_name = str(item.get("symbol", "")).upper()
            if contract_name:
                self.by_contract[contract_name] = item

                simple = contract_name
                if contract_name.startswith("E-"):
                    simple = contract_name[2:]
                elif contract_name.startswith("H-"):
                    simple = contract_name[2:]
                elif contract_name.startswith("S-"):
                    simple = contract_name[2:]

                self.by_simple[simple] = item

    def resolve_contract_name(self, symbol: str) -> str:
        raw = symbol.strip().upper()

        if raw in self.by_contract:
            return raw

        if raw in self.by_simple:
            return str(self.by_simple[raw]["symbol"]).upper()

        # 允许 BTCUSDT -> E-BTC-USDT
        if raw.endswith("USDT") and "-" not in raw:
            base = raw[:-4]
            guessed = f"E-{base}-USDT"
            if guessed in self.by_contract:
                return guessed

        raise ValueError(f"找不到合约: {symbol}")


def get_registry(futures_public_api):
    contracts = futures_public_api.contracts()
    return FuturesRegistry(contracts)


def get_ticker(futures_public_api, registry, symbol):
    contract_name = registry.resolve_contract_name(symbol)
    return futures_public_api.ticker(contract_name)


def get_ticker_pretty_data(futures_public_api, registry, symbol):
    contract_name = registry.resolve_contract_name(symbol)
    data = futures_public_api.ticker(contract_name)
    return contract_name, data


def get_depth(futures_public_api, registry, symbol, limit=20):
    contract_name = registry.resolve_contract_name(symbol)
    return futures_public_api.depth(contract_name, limit)


def get_depth_pretty_data(futures_public_api, registry, symbol, limit=10):
    contract_name = registry.resolve_contract_name(symbol)
    data = futures_public_api.depth(contract_name, limit)
    return contract_name, data


def get_index(futures_public_api, registry, symbol):
    contract_name = registry.resolve_contract_name(symbol)
    return futures_public_api.index(contract_name)


def get_klines(futures_public_api, registry, symbol, interval, limit=100):
    contract_name = registry.resolve_contract_name(symbol)
    return futures_public_api.klines(contract_name, interval, limit)
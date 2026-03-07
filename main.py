import json
import sys
from pathlib import Path
from typing import Any

from tools.zke_client import ZKEClient, ZKEApiError
from tools.spot_public import SpotPublicApi
from tools.spot_private import SpotPrivateApi
from tools.futures_public import FuturesPublicApi
from tools.futures_private import FuturesPrivateApi
from tools.margin_private import MarginPrivateApi
from tools.symbol_utils import SymbolNotFoundError, SymbolValidationError
from tools import formatters
from tools import account_service
from tools import order_service
from tools import market_service
from tools import futures_service
from tools import futures_account_service
from tools import futures_order_service
from tools import margin_order_service
from tools import withdraw_service
from tools import ws_service


CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_spot_client() -> ZKEClient:
    config = load_config()
    spot_conf = config["spot"]
    return ZKEClient(
        base_url=spot_conf["base_url"],
        api_key=spot_conf.get("api_key", ""),
        api_secret=spot_conf.get("api_secret", ""),
        recv_window=spot_conf.get("recv_window", 5000),
    )


def build_futures_client() -> ZKEClient:
    config = load_config()
    fut_conf = config["futures"]
    return ZKEClient(
        base_url=fut_conf["base_url"],
        api_key=fut_conf.get("api_key", ""),
        api_secret=fut_conf.get("api_secret", ""),
        recv_window=fut_conf.get("recv_window", 5000),
    )


def get_ws_url() -> str:
    config = load_config()
    ws_conf = config.get("ws", {})
    url = ws_conf.get("url")
    if not url:
        raise ValueError("config.json 中缺少 ws.url")
    return url


def pretty_print(data: Any):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_help():
    print(
        "现货:\n"
        "  python3 main.py ping\n"
        "  python3 main.py time\n"
        "  python3 main.py symbols\n"
        "  python3 main.py ticker BTCUSDT\n"
        "  python3 main.py ticker-pretty BTCUSDT\n"
        "  python3 main.py depth BTCUSDT 20\n"
        "  python3 main.py depth-pretty BTCUSDT 10\n"
        "  python3 main.py trades BTCUSDT 20\n"
        "  python3 main.py klines BTCUSDT 1day\n"
        "  python3 main.py account\n"
        "  python3 main.py account-nonzero\n"
        "  python3 main.py account-nonzero-pretty\n"
        "  python3 main.py account-asset USDT\n"
        "  python3 main.py balance USDT\n"
        "  python3 main.py open-orders BTCUSDT 20\n"
        "  python3 main.py open-orders-pretty BTCUSDT\n"
        "  python3 main.py order BTCUSDT <orderId>\n"
        "  python3 main.py my-trades BTCUSDT 20\n"
        "  python3 main.py my-trades-pretty BTCUSDT 10\n"
        "  python3 main.py test-order BTCUSDT BUY LIMIT 0.001 10000\n"
        "  python3 main.py create-order BTCUSDT BUY LIMIT 0.001 10000\n"
        "  python3 main.py cancel-order BTCUSDT <orderId>\n"
        "\n提现:\n"
        "  python3 main.py withdraw USDTBSC 0xabc... 20\n"
        "  python3 main.py withdraw-history\n"
        "  python3 main.py withdraw-history USDTBSC 20\n"
        "\n杠杆:\n"
        "  python3 main.py margin-create-order BTCUSDT BUY LIMIT 0.001 10000\n"
        "  python3 main.py margin-order BTCUSDT <orderId>\n"
        "  python3 main.py margin-cancel-order BTCUSDT <orderId>\n"
        "  python3 main.py margin-open-orders BTCUSDT 20\n"
        "  python3 main.py margin-my-trades BTCUSDT 20\n"
        "\n合约公共:\n"
        "  python3 main.py futures-ping\n"
        "  python3 main.py futures-time\n"
        "  python3 main.py futures-contracts\n"
        "  python3 main.py futures-ticker E-BTC-USDT\n"
        "  python3 main.py futures-ticker-pretty E-BTC-USDT\n"
        "  python3 main.py futures-depth E-BTC-USDT 20\n"
        "  python3 main.py futures-depth-pretty E-BTC-USDT 10\n"
        "  python3 main.py futures-index E-BTC-USDT\n"
        "  python3 main.py futures-index-pretty E-BTC-USDT\n"
        "  python3 main.py futures-klines E-BTC-USDT 1min 10\n"
        "\n合约私有:\n"
        "  python3 main.py futures-account\n"
        "  python3 main.py futures-balance USDT\n"
        "  python3 main.py futures-balance-pretty\n"
        "  python3 main.py futures-positions\n"
        "  python3 main.py futures-positions-pretty\n"
        "  python3 main.py futures-open-orders E-BTC-USDT\n"
        "  python3 main.py futures-order E-BTC-USDT <orderId>\n"
        "  python3 main.py futures-my-trades E-BTC-USDT 10\n"
        "  python3 main.py futures-my-trades-pretty E-BTC-USDT 10\n"
        "  python3 main.py futures-order-historical E-BTC-USDT 10\n"
        "  python3 main.py futures-order-historical-pretty E-BTC-USDT 10\n"
        "  python3 main.py futures-profit-historical E-BTC-USDT 10\n"
        "  python3 main.py futures-profit-historical-pretty E-BTC-USDT 10\n"
        "  python3 main.py futures-create-order E-BTC-USDT BUY OPEN 2 LIMIT 1 50000\n"
        "  python3 main.py futures-cancel-order E-BTC-USDT <orderId>\n"
        "\nWebSocket:\n"
        "  python3 main.py ws-ticker BTCUSDT 30\n"
        "  python3 main.py ws-depth BTCUSDT step0 30\n"
        "  python3 main.py ws-kline BTCUSDT 1min 30\n"
        "  python3 main.py ws-trades BTCUSDT 30\n"
        "  python3 main.py ws-kline-req BTCUSDT 1min 10\n"
        "  python3 main.py ws-trade-req BTCUSDT 10\n"
    )


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].strip().lower()

    spot_client = build_spot_client()
    public_api = SpotPublicApi(spot_client)
    private_api = SpotPrivateApi(spot_client)
    margin_api = MarginPrivateApi(spot_client)

    futures_client = build_futures_client()
    futures_public = FuturesPublicApi(futures_client)
    futures_private = FuturesPrivateApi(futures_client)

    try:
        registry = market_service.get_registry(public_api)
        futures_registry = futures_service.get_registry(futures_public)

        # ===== WebSocket =====
        if cmd == "ws-ticker":
            symbol = sys.argv[2]
            seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            ws_service.run_ws_ticker(get_ws_url(), symbol, seconds=seconds)
            return

        if cmd == "ws-depth":
            symbol = sys.argv[2]
            step = sys.argv[3] if len(sys.argv) > 3 else "step0"
            seconds = int(sys.argv[4]) if len(sys.argv) > 4 else 30
            ws_service.run_ws_depth(get_ws_url(), symbol, step=step, seconds=seconds)
            return

        if cmd == "ws-kline":
            symbol = sys.argv[2]
            interval = sys.argv[3] if len(sys.argv) > 3 else "1min"
            seconds = int(sys.argv[4]) if len(sys.argv) > 4 else 30
            ws_service.run_ws_kline(get_ws_url(), symbol, interval=interval, seconds=seconds)
            return

        if cmd == "ws-trades":
            symbol = sys.argv[2]
            seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            ws_service.run_ws_trades(get_ws_url(), symbol, seconds=seconds)
            return

        if cmd == "ws-kline-req":
            symbol = sys.argv[2]
            interval = sys.argv[3] if len(sys.argv) > 3 else "1min"
            seconds = int(sys.argv[4]) if len(sys.argv) > 4 else 10
            ws_service.run_ws_kline_req(get_ws_url(), symbol, interval=interval, seconds=seconds)
            return

        if cmd == "ws-trade-req":
            symbol = sys.argv[2]
            seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            ws_service.run_ws_trade_req(get_ws_url(), symbol, seconds=seconds)
            return

        # ===== 现货 =====
        if cmd == "ping":
            pretty_print(public_api.ping())
            return

        if cmd == "time":
            pretty_print(public_api.time())
            return

        if cmd == "symbols":
            pretty_print(public_api.symbols())
            return

        if cmd == "ticker":
            symbol = sys.argv[2]
            pretty_print(market_service.get_ticker(public_api, registry, symbol))
            return

        if cmd == "ticker-pretty":
            symbol = sys.argv[2]
            display_symbol, ticker_data = market_service.get_ticker_pretty_data(public_api, registry, symbol)
            formatters.print_ticker_pretty(display_symbol, ticker_data)
            return

        if cmd == "depth":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            pretty_print(market_service.get_depth(public_api, registry, symbol, limit))
            return

        if cmd == "depth-pretty":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            display_symbol, depth_data = market_service.get_depth_pretty_data(public_api, registry, symbol, limit)
            formatters.print_depth_pretty(display_symbol, depth_data, limit)
            return

        if cmd == "trades":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            pretty_print(market_service.get_trades(public_api, registry, symbol, limit))
            return

        if cmd == "klines":
            symbol = sys.argv[2]
            interval = sys.argv[3]
            pretty_print(market_service.get_klines(public_api, registry, symbol, interval))
            return

        if cmd == "account":
            pretty_print(private_api.account())
            return

        if cmd == "account-nonzero":
            account_data = private_api.account()
            balances = account_service.extract_account_balances(account_data)
            nonzero = account_service.filter_nonzero_balances(balances)
            pretty_print(nonzero)
            return

        if cmd == "account-nonzero-pretty":
            account_data = private_api.account()
            balances = account_service.extract_account_balances(account_data)
            nonzero = account_service.filter_nonzero_balances(balances)
            formatters.print_account_balances_pretty(nonzero)
            return

        if cmd == "account-asset":
            asset = sys.argv[2]
            account_data = private_api.account()
            balances = account_service.extract_account_balances(account_data)
            matched = account_service.find_asset_balance(balances, asset)
            pretty_print(matched)
            return

        if cmd == "balance":
            asset = sys.argv[2]
            account_data = private_api.account()
            balances = account_service.extract_account_balances(account_data)
            summary = account_service.get_asset_balance_summary(balances, asset)
            formatters.print_asset_balance_pretty(summary)
            return

        if cmd == "open-orders":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            api_symbol = registry.get_api_symbol(symbol)
            pretty_print(private_api.open_orders(api_symbol, limit))
            return

        if cmd == "open-orders-pretty":
            symbol = sys.argv[2]
            display_symbol = registry.get_display_symbol(symbol)
            orders = order_service.open_orders(private_api, registry, symbol)
            formatters.print_open_orders_pretty(display_symbol, orders)
            return

        if cmd == "order":
            symbol = sys.argv[2]
            order_id = sys.argv[3]
            api_symbol = registry.get_api_symbol(symbol)
            pretty_print(private_api.order_query(api_symbol, order_id=order_id))
            return

        if cmd == "my-trades":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            api_symbol = registry.get_api_symbol(symbol)
            pretty_print(private_api.my_trades(api_symbol, limit))
            return

        if cmd == "my-trades-pretty":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            display_symbol, trades = market_service.get_my_trades_pretty_data(private_api, registry, symbol, limit)
            formatters.print_my_trades_pretty(display_symbol, trades)
            return

        if cmd == "test-order":
            symbol = sys.argv[2]
            side = sys.argv[3]
            order_type = sys.argv[4]
            volume = sys.argv[5]
            price = sys.argv[6] if len(sys.argv) > 6 else None

            data, result = order_service.test_order(
                private_api, registry, symbol, side, order_type, volume, price
            )

            print("订单参数校验通过：")
            print(f"交易对: {data['display_symbol']}")
            print(f"API symbol: {data['api_symbol']}")
            print(f"数量: {data['volume']}")
            if data["price"]:
                print(f"价格: {data['price']}")
            pretty_print(result)
            return

        if cmd == "create-order":
            symbol = sys.argv[2]
            side = sys.argv[3]
            order_type = sys.argv[4]
            volume = sys.argv[5]
            price = sys.argv[6] if len(sys.argv) > 6 else None

            data, result = order_service.create_order(
                private_api, registry, symbol, side, order_type, volume, price
            )

            print("订单参数校验通过：")
            print(f"交易对: {data['display_symbol']}")
            print(f"API symbol: {data['api_symbol']}")
            print(f"数量: {data['volume']}")
            if data["price"]:
                print(f"价格: {data['price']}")
            pretty_print(result)
            return

        if cmd == "cancel-order":
            symbol = sys.argv[2]
            order_id = sys.argv[3]
            result = order_service.cancel_order(private_api, registry, symbol, order_id)
            pretty_print(result)
            return

        # ===== 提现 =====
        if cmd == "withdraw":
            coin = sys.argv[2]
            address = sys.argv[3]
            amount = sys.argv[4]
            network = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "" else None
            memo = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != "" else None

            data = withdraw_service.apply_withdraw(
                private_api,
                coin,
                address,
                amount,
                network,
                memo
            )

            pretty_print(data)
            return

        if cmd == "withdraw-history":
            coin = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "" else None
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

            rows = withdraw_service.withdraw_history(
                private_api,
                coin,
                limit
            )

            pretty_print(rows)
            return

        # ===== 杠杆 =====
        if cmd == "margin-create-order":
            symbol = sys.argv[2]
            side = sys.argv[3]
            order_type = sys.argv[4]
            volume = sys.argv[5]
            price = sys.argv[6] if len(sys.argv) > 6 else None

            data, result = margin_order_service.create_order(
                margin_api, registry, symbol, side, order_type, volume, price
            )

            print("杠杆订单参数：")
            print(f"交易对: {data['display_symbol']}")
            print(f"API symbol: {data['api_symbol']}")
            print(f"方向: {data['side']}")
            print(f"类型: {data['order_type']}")
            print(f"数量: {data['volume']}")
            if data["price"] is not None:
                print(f"价格: {data['price']}")
            pretty_print(result)
            return

        if cmd == "margin-order":
            symbol = sys.argv[2]
            order_id = sys.argv[3]
            pretty_print(
                margin_order_service.order_query(
                    margin_api, registry, symbol, order_id=order_id
                )
            )
            return

        if cmd == "margin-cancel-order":
            symbol = sys.argv[2]
            order_id = sys.argv[3]
            pretty_print(
                margin_order_service.cancel_order(
                    margin_api, registry, symbol, order_id=order_id
                )
            )
            return

        if cmd == "margin-open-orders":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            pretty_print(
                margin_order_service.open_orders(
                    margin_api, registry, symbol, limit=limit
                )
            )
            return

        if cmd == "margin-my-trades":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            pretty_print(
                margin_order_service.my_trades(
                    margin_api, registry, symbol, limit=limit
                )
            )
            return

        # ===== 合约公共 =====
        if cmd == "futures-ping":
            pretty_print(futures_public.ping())
            return

        if cmd == "futures-time":
            pretty_print(futures_public.time())
            return

        if cmd == "futures-contracts":
            pretty_print(futures_public.contracts())
            return

        if cmd == "futures-ticker":
            symbol = sys.argv[2]
            pretty_print(futures_service.get_ticker(futures_public, futures_registry, symbol))
            return

        if cmd == "futures-ticker-pretty":
            symbol = sys.argv[2]
            contract_name, data = futures_service.get_ticker_pretty_data(futures_public, futures_registry, symbol)
            formatters.print_futures_ticker_pretty(contract_name, data)
            return

        if cmd == "futures-depth":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            pretty_print(futures_service.get_depth(futures_public, futures_registry, symbol, limit))
            return

        if cmd == "futures-depth-pretty":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            contract_name, data = futures_service.get_depth_pretty_data(futures_public, futures_registry, symbol, limit)
            formatters.print_depth_pretty(contract_name, data, limit)
            return

        if cmd == "futures-index":
            symbol = sys.argv[2]
            pretty_print(futures_service.get_index(futures_public, futures_registry, symbol))
            return

        if cmd == "futures-index-pretty":
            symbol = sys.argv[2]
            contract_name = futures_registry.resolve_contract_name(symbol)
            data = futures_service.get_index(futures_public, futures_registry, symbol)
            formatters.print_futures_index_pretty(contract_name, data)
            return

        if cmd == "futures-klines":
            symbol = sys.argv[2]
            interval = sys.argv[3]
            limit = int(sys.argv[4]) if len(sys.argv) > 4 else 20
            pretty_print(futures_service.get_klines(futures_public, futures_registry, symbol, interval, limit))
            return

        # ===== 合约私有 =====
        if cmd == "futures-account":
            pretty_print(futures_private.account())
            return

        if cmd == "futures-balance":
            margin_coin = sys.argv[2]
            data = futures_private.account()
            accounts = futures_account_service.extract_accounts(data)
            summary = futures_account_service.get_margin_coin_summary(accounts, margin_coin)
            pretty_print(summary)
            return

        if cmd == "futures-balance-pretty":
            data = futures_private.account()
            formatters.print_futures_balance_pretty(data)
            return

        if cmd == "futures-positions":
            data = futures_private.account()
            accounts = futures_account_service.extract_accounts(data)
            positions = futures_account_service.flatten_positions(accounts)
            positions = futures_account_service.filter_nonzero_positions(positions)
            pretty_print(positions)
            return

        if cmd == "futures-positions-pretty":
            data = futures_private.account()
            accounts = futures_account_service.extract_accounts(data)
            positions = futures_account_service.flatten_positions(accounts)
            positions = futures_account_service.filter_nonzero_positions(positions)
            formatters.print_futures_positions_pretty(positions)
            return

        if cmd == "futures-open-orders":
            symbol = sys.argv[2]
            pretty_print(futures_order_service.open_orders(futures_private, futures_registry, symbol))
            return

        if cmd == "futures-order":
            symbol = sys.argv[2]
            order_id = sys.argv[3]
            pretty_print(
                futures_order_service.order_query(
                    futures_private, futures_registry, symbol, order_id=order_id
                )
            )
            return

        if cmd == "futures-my-trades":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            pretty_print(futures_order_service.my_trades(futures_private, futures_registry, symbol, limit))
            return

        if cmd == "futures-my-trades-pretty":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            trades = futures_order_service.my_trades(futures_private, futures_registry, symbol, limit)
            formatters.print_futures_my_trades_pretty(trades)
            return

        if cmd == "futures-order-historical":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            pretty_print(futures_order_service.order_historical(futures_private, futures_registry, symbol, limit))
            return

        if cmd == "futures-order-historical-pretty":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            orders = futures_order_service.order_historical(futures_private, futures_registry, symbol, limit)
            formatters.print_futures_order_history_pretty(orders)
            return

        if cmd == "futures-profit-historical":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            pretty_print(futures_order_service.profit_historical(futures_private, futures_registry, symbol, limit))
            return

        if cmd == "futures-profit-historical-pretty":
            symbol = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            records = futures_order_service.profit_historical(futures_private, futures_registry, symbol, limit)
            formatters.print_futures_profit_pretty(records)
            return

        if cmd == "futures-create-order":
            symbol = sys.argv[2]
            side = sys.argv[3]
            open_action = sys.argv[4]
            position_type = int(sys.argv[5])
            order_type = sys.argv[6]
            volume = sys.argv[7]
            price = sys.argv[8] if len(sys.argv) > 8 else None

            data, result = futures_order_service.create_order(
                futures_private,
                futures_registry,
                symbol,
                side,
                open_action,
                position_type,
                order_type,
                volume,
                price
            )

            print("合约订单参数：")
            print(f"合约: {data['contract_name']}")
            print(f"方向: {data['side']}")
            print(f"开平: {data['open_action']}")
            print(f"仓位类型: {data['position_type']}")
            print(f"类型: {data['order_type']}")
            print(f"数量: {data['volume']}")
            if data["price"] is not None:
                print(f"价格: {data['price']}")

            pretty_print(result)
            return

        if cmd == "futures-cancel-order":
            symbol = sys.argv[2]
            order_id = sys.argv[3]
            pretty_print(futures_order_service.cancel_order(futures_private, futures_registry, symbol, order_id))
            return

        print_help()

    except ZKEApiError as e:
        print(spot_client.explain_error(e))
    except (SymbolNotFoundError, SymbolValidationError, ValueError, IndexError) as e:
        print(f"参数校验失败: {e}")
    except Exception as e:
        print(f"程序运行失败: {e}")


if __name__ == "__main__":
    main()
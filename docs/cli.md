# CLI Usage

The SDK includes a command line interface through main.py.

## Spot

python main.py ping
python main.py ticker BTCUSDT
python main.py depth BTCUSDT 20
python main.py trades BTCUSDT 20
python main.py klines BTCUSDT 1day

## Account

python main.py account
python main.py balance USDT

## Orders

python main.py open-orders BTCUSDT
python main.py create-order BTCUSDT BUY LIMIT 0.001 10000
python main.py cancel-order BTCUSDT ORDER_ID

## Withdraw

python main.py withdraw USDTBSC 0xYourAddress 20
python main.py withdraw-history

## Futures

python main.py futures-ping
python main.py futures-ticker E-BTC-USDT
python main.py futures-positions

## WebSocket

python main.py ws-ticker BTCUSDT 30
python main.py ws-depth BTCUSDT step0 30
python main.py ws-kline BTCUSDT 1min 30
python main.py ws-trades BTCUSDT 30

# CLI Examples

Check BTC ticker

python main.py ticker BTCUSDT

Check USDT balance

python main.py balance USDT

Place spot order

python main.py create-order BTCUSDT BUY LIMIT 0.001 60000

Cancel order

python main.py cancel-order BTCUSDT ORDER_ID

View futures positions

python main.py futures-positions

Withdraw USDT

python main.py withdraw USDTBSC 0xYourAddress 20

Start ticker stream

python main.py ws-ticker BTCUSDT 30

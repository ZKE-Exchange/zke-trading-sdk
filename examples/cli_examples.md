# CLI Examples

Quick command examples for the ZKE Trading CLI.

---

# Spot Market

Check BTC ticker

```bash
python main.py ticker BTCUSDT
```

Check orderbook depth

```bash
python main.py depth BTCUSDT 20
```

Check recent trades

```bash
python main.py trades BTCUSDT 20
```

---

# Account

Check USDT balance

```bash
python main.py balance USDT
```

View account info

```bash
python main.py account
```

---

# Spot Orders

Place spot order

```bash
python main.py create-order BTCUSDT BUY LIMIT 0.001 60000
```

Cancel order

```bash
python main.py cancel-order BTCUSDT ORDER_ID
```

---

# Futures

View futures positions

```bash
python main.py futures-positions
```

Check futures ticker

```bash
python main.py futures-ticker E-BTC-USDT
```

---

# Withdraw

Withdraw USDT

```bash
python main.py withdraw USDTBSC 0xYourAddress 20
```

Check withdraw history

```bash
python main.py withdraw-history
```

---

# WebSocket Streaming

Start ticker stream

```bash
python main.py ws-ticker BTCUSDT 30
```

Stream orderbook

```bash
python main.py ws-depth BTCUSDT step0 30
```

Stream trades

```bash
python main.py ws-trades BTCUSDT 30
```

Stream kline

```bash
python main.py ws-kline BTCUSDT 1min 30
```

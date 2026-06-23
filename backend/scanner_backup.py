import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

API_KEY = "2ce4b507c77c48599f27e63ccb7b7de4"

PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "EUR/JPY",
    "GBP/JPY",
    "AUD/USD"
]

for pair in PAIRS:

    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=5min&outputsize=100&apikey={API_KEY}"

    data = requests.get(url).json()

    candles = data.get("values", [])

    if len(candles) < 30:
        print(pair, "Not enough data")
        continue

    df = pd.DataFrame(candles)

    df["close"] = df["close"].astype(float)

    df = df.iloc[::-1]

    ema9 = EMAIndicator(df["close"], window=9).ema_indicator()
    ema21 = EMAIndicator(df["close"], window=21).ema_indicator()
    rsi = RSIIndicator(df["close"], window=14).rsi()

    last_ema9 = ema9.iloc[-1]
    last_ema21 = ema21.iloc[-1]
    last_rsi = rsi.iloc[-1]

    signal = "WAIT"

    if last_ema9 > last_ema21 and last_rsi > 55:
        signal = "BUY"

    elif last_ema9 < last_ema21 and last_rsi < 45:
        signal = "SELL"

    print(
        pair,
        "| Signal:", signal,
        "| RSI:", round(last_rsi, 2)
    )
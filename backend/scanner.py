import requests
import pandas as pd

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

from datetime import datetime, timedelta
import pytz

API_KEY = "2ce4b507c77c48599f27e63ccb7b7de4"

PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "EUR/JPY",
    "GBP/JPY",
    "AUD/USD"
]

NEWS_HOURS = [13, 18, 19]

india = pytz.timezone("Asia/Kolkata")

for pair in PAIRS:

    try:

        now = datetime.now(india)

        if now.hour in NEWS_HOURS:

            print(
                f"{pair} | Signal: WAIT | RSI: 0 | Pattern: NEWS_TIME | "
                f"Confidence: 0% | Strength: NEWS | Entry: - | "
                f"Countdown: --:-- | Volatility: 0% | "
                f"Support: 0 | Resistance: 0 | Expiry: WAIT"
            )
            continue

        url = (
            f"https://api.twelvedata.com/time_series?"
            f"symbol={pair}&interval=5min&outputsize=100&apikey={API_KEY}"
        )

        data = requests.get(url).json()

        candles = data.get("values", [])

        if len(candles) < 50:
            continue

        df = pd.DataFrame(candles)

        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        df = df.iloc[::-1].reset_index(drop=True)

        ema9 = EMAIndicator(df["close"], window=9).ema_indicator()
        ema21 = EMAIndicator(df["close"], window=21).ema_indicator()

        rsi = RSIIndicator(df["close"], window=14).rsi()

        macd = MACD(df["close"])

        last = df.iloc[-1]

        last_ema9 = ema9.iloc[-1]
        last_ema21 = ema21.iloc[-1]

        last_rsi = rsi.iloc[-1]

        last_macd = macd.macd().iloc[-1]
        last_macd_signal = macd.macd_signal().iloc[-1]

        o = last["open"]
        h = last["high"]
        l = last["low"]
        c = last["close"]

        body = abs(c - o)

        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l

        pattern = "NONE"

        if body <= (h - l) * 0.10:
            pattern = "DOJI"

        elif lower_shadow > body * 2 and upper_shadow < body:
            pattern = "HAMMER"

        elif upper_shadow > body * 2 and lower_shadow < body:
            pattern = "SHOOTING_STAR"

        signal = "WAIT"
        confidence = 0

        # BUY
        if (
            last_ema9 > last_ema21
            and last_rsi > 55
            and last_macd > last_macd_signal
            and pattern != "SHOOTING_STAR"
        ):

            signal = "BUY"
            confidence = 80

            if pattern == "HAMMER":
                confidence += 15

            if last_rsi > 65:
                confidence += 5

        # SELL
        elif (
            last_ema9 < last_ema21
            and last_rsi < 45
            and last_macd < last_macd_signal
            and pattern != "HAMMER"
        ):

            signal = "SELL"
            confidence = 80

            if pattern == "SHOOTING_STAR":
                confidence += 15

            if last_rsi < 35:
                confidence += 5

        # Strength
        if confidence >= 95:
            strength = "STRONG"
        elif confidence >= 85:
            strength = "GOOD"
        elif confidence >= 70:
            strength = "NORMAL"
        else:
            strength = "WEAK"

        # Next Candle Time
        current_minute = now.minute
        next_minute = ((current_minute // 5) + 1) * 5

        if next_minute >= 60:

            entry_dt = (
                now.replace(
                    minute=0,
                    second=0,
                    microsecond=0
                )
                + timedelta(hours=1)
            )

        else:

            entry_dt = now.replace(
                minute=next_minute,
                second=0,
                microsecond=0
            )

        # Entry + Countdown
        if signal == "WAIT":

            entry = "-"
            countdown = "--:--"

        else:

            entry = entry_dt.strftime("%H:%M")

            remaining = int(
                (entry_dt - now).total_seconds()
            )

            minutes_left = remaining // 60
            seconds_left = remaining % 60

            countdown = (
                f"{minutes_left:02d}:{seconds_left:02d}"
            )

        # Volatility
        volatility = round(((h - l) / c) * 100, 2)

        # Support Resistance
        support = round(
            df["low"].tail(20).min(),
            5
        )

        resistance = round(
            df["high"].tail(20).max(),
            5
        )

        # Multi Expiry
        if confidence >= 95:
            expiry = "1M / 2M"

        elif confidence >= 90:
            expiry = "2M / 3M"

        elif confidence >= 85:
            expiry = "3M / 5M"

        elif confidence >= 80:
            expiry = "5M"

        else:
            expiry = "WAIT"

        print(
            f"{pair} | "
            f"Signal: {signal} | "
            f"RSI: {round(last_rsi,2)} | "
            f"Pattern: {pattern} | "
            f"Confidence: {confidence}% | "
            f"Strength: {strength} | "
            f"Entry: {entry} | "
            f"Countdown: {countdown} | "
            f"Volatility: {volatility}% | "
            f"Support: {support} | "
            f"Resistance: {resistance} | "
            f"Expiry: {expiry}"
        )

    except Exception as e:

        print(pair, "| ERROR:", e)
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# ============================================================
# SETTINGS
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")

PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD",
    "EUR/GBP",
    "EUR/JPY",
    "GBP/JPY",
    "CHF/JPY",
]

TIMEFRAMES = {
    "1": "1min",
    "5": "5min",
    "15": "15min",
}


# ============================================================
# RENDER HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Signal bot is running")

    def log_message(self, format, *args):
        return


def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# ============================================================
# MARKET DATA
# ============================================================

def get_market_data(symbol, interval, outputsize=100):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": TWELVE_DATA_API_KEY,
        "format": "JSON",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if "values" not in data:
            print("API ERROR:", data)
            return []

        values = data["values"]

        # Oldest -> newest
        values.reverse()

        candles = []

        for x in values:
            try:
                candles.append({
                    "open": float(x["open"]),
                    "high": float(x["high"]),
                    "low": float(x["low"]),
                    "close": float(x["close"]),
                })
            except Exception:
                continue

        return candles

    except Exception as e:
        print("Market data error:", e)
        return []


# ============================================================
# INDICATORS
# ============================================================

def ema(values, period):
    if len(values) < period:
        return None

    multiplier = 2 / (period + 1)

    result = sum(values[:period]) / period

    for price in values[period:]:
        result = (price - result) * multiplier + result

    return result


def rsi(values, period=14):
    if len(values) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, len(values)):
        change = values[i] - values[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def macd(values):
    if len(values) < 35:
        return None, None

    ema12 = ema(values, 12)
    ema26 = ema(values, 26)

    if ema12 is None or ema26 is None:
        return None, None

    macd_line = ema12 - ema26

    return macd_line, None


def bollinger(values, period=20, deviation=2):
    if len(values) < period:
        return None, None, None

    recent = values[-period:]

    middle = sum(recent) / period

    variance = sum(
        (x - middle) ** 2 for x in recent
    ) / period

    std = variance ** 0.5

    upper = middle + deviation * std
    lower = middle - deviation * std

    return upper, middle, lower


# ============================================================
# SIGNAL ENGINE
# ============================================================

def calculate_signal(candles):
    if len(candles) < 50:
        return {
            "signal": "WAIT",
            "strength": 0,
            "reason": "Not enough market data",
        }

    closes = [c["close"] for c in candles]

    price = closes[-1]

    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)

    rsi_value = rsi(closes, 14)

    macd_line, _ = macd(closes)

    upper, middle, lower = bollinger(closes, 20, 2)

    if None in (
        ema9,
        ema21,
        rsi_value,
        macd_line,
        upper,
        middle,
        lower,
    ):
        return {
            "signal": "WAIT",
            "strength": 0,
            "reason": "Indicator calculation incomplete",
        }

    call_score = 0
    put_score = 0

    # EMA TREND
    if ema9 > ema21:
        call_score += 2
    elif ema9 < ema21:
        put_score += 2

    # RSI
    if 50 < rsi_value < 70:
        call_score += 2
    elif 30 < rsi_value < 50:
        put_score += 2

    # MACD
    if macd_line > 0:
        call_score += 2
    elif macd_line < 0:
        put_score += 2

    # Bollinger
    if price > middle:
        call_score += 1
    elif price < middle:
        put_score += 1

    # Candle direction
    last_candle = candles[-1]

    if last_candle["close"] > last_candle["open"]:
        call_score += 1
    elif last_candle["close"] < last_candle["open"]:
        put_score += 1

    total = call_score + put_score

    if total == 0:
        return {
            "signal": "WAIT",
            "strength": 0,
            "reason": "No clear trend",
        }

    if call_score > put_score:
        strength = int((call_score / 8) * 100)

        if strength >= 60:
            signal = "CALL"
        else:
            signal = "WAIT"

    elif put_score > call_score:
        strength = int((put_score / 8) * 100)

        if strength >= 60:
            signal = "PUT"
        else:
            signal = "WAIT"

    else:
        signal = "WAIT"
        strength = 50

    return {
        "signal": signal,
        "strength": strength,
        "price": price,
        "ema9": ema9,
        "ema21": ema21,
        "rsi": rsi_value,
        "macd": macd_line,
        "upper": upper,
        "middle": middle,
        "lower": lower,
    }


# ============================================================
# TELEGRAM COMMANDS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 LIVE MARKET SIGNAL BOT\n\n"
        "Commands:\n"
        "/pairs - Currency pairs\n"
        "/signal EUR/USD 5 - Get live signal\n"
        "/signal GBP/JPY 1 - Get 1 minute signal\n"
        "/help - Help\n\n"
        "⚠️ Signals are based on market-data analysis."
    )

    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 HOW TO USE\n\n"
        "Example:\n"
        "/signal EUR/USD 5\n\n"
        "1 = 1 minute\n"
        "5 = 5 minutes\n"
        "15 = 15 minutes\n\n"
        "Example:\n"
        "/signal GBP/JPY 1"
    )

    await update.message.reply_text(text)


async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💱 AVAILABLE PAIRS\n\n"

    for pair in PAIRS:
        text += f"• {pair}\n"

    await update.message.reply_text(text)


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 1:
        await update.message.reply_text(
            "Use:\n/signal EUR/USD 5"
        )
        return

    symbol = context.args[0].upper()

    if symbol not in PAIRS:
        await update.message.reply_text(
            "❌ Pair not available.\n\n"
            "Use /pairs to see available pairs."
        )
        return

    timeframe = "5"

    if len(context.args) >= 2:
        timeframe = context.args[1]

    if timeframe not in TIMEFRAMES:
        await update.message.reply_text(
            "❌ Timeframe must be 1, 5 or 15."
        )
        return

    interval = TIMEFRAMES[timeframe]

    await update.message.reply_text(
        f"⏳ Getting live market data...\n\n"
        f"💱 {symbol}\n"
        f"⏱ {timeframe} MIN"
    )

    candles = get_market_data(
        symbol,
        interval,
        100
    )

    if not candles:
        await update.message.reply_text(
            "❌ Live market data could not be obtained."
        )
        return

    result = calculate_signal(candles)

    signal_name = result["signal"]
    strength = result["strength"]

    if signal_name == "CALL":
        emoji = "🟢"
    elif signal_name == "PUT":
        emoji = "🔴"
    else:
        emoji = "⚪"

    price = result.get("price", 0)
    rsi_value = result.get("rsi", 0)
    macd_value = result.get("macd", 0)

    text = (
        "📊 LIVE MARKET SIGNAL\n\n"
        f"💱 {symbol}\n"
        f"⏱ {timeframe} MIN\n\n"
        f"{emoji} {signal_name}\n\n"
        f"💰 Price: {price:.5f}\n"
        f"📈 Strength: {strength}%\n\n"
        f"EMA 9: {result.get('ema9', 0):.5f}\n"
        f"EMA 21: {result.get('ema21', 0):.5f}\n"
        f"RSI: {rsi_value:.2f}\n"
        f"MACD: {macd_value:.6f}\n\n"
        "⚠️ Analysis only — no profit guarantee."
    )

    await update.message.reply_text(text)


# ============================================================
# MAIN
# ============================================================

def main():

    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is missing.")
        return

    if not TWELVE_DATA_API_KEY:
        print("ERROR: TWELVE_DATA_API_KEY is missing.")
        return

    # Render health server
    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("pairs", pairs)
    )

    application.add_handler(
        CommandHandler("signal", signal)
    )

    print("LIVE SIGNAL BOT STARTED")

    application.run_polling()


if __name__ == "__main__":
    main()

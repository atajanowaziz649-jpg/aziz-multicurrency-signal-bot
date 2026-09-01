import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")

PAIRS = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "USDCHF": "USD/CHF",
    "AUDUSD": "AUD/USD",
    "USDCAD": "USD/CAD",
    "NZDUSD": "NZD/USD",
    "EURGBP": "EUR/GBP",
    "EURJPY": "EUR/JPY",
    "GBPJPY": "GBP/JPY",
    "CHFJPY": "CHF/JPY",
    "AUDJPY": "AUD/JPY",
    "CADJPY": "CAD/JPY",
    "EURCHF": "EUR/CHF",
    "GBPCHF": "GBP/CHF"
}


def get_signal(symbol):
    if not API_KEY:
        return "❌ API KEY ýok"

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": "1min",
        "outputsize": 50,
        "apikey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if "values" not in data:
            return "❌ Maglumat ýok"

        values = data["values"]

        closes = [float(x["close"]) for x in values]

        if len(closes) < 20:
            return "❌ Maglumat az"

        # Simple EMA
        ema_fast = sum(closes[:9]) / 9
        ema_slow = sum(closes[:20]) / 20

        # Simple momentum
        current = closes[0]
        previous = closes[1]

        if current > ema_fast and ema_fast > ema_slow and current > previous:
            return "🟢 CALL"

        if current < ema_fast and ema_fast < ema_slow and current < previous:
            return "🔴 PUT"

        return "🟡 WAIT"

    except Exception:
        return "❌ API ýalňyşlygy"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salam!\n\n"
        "📊 MULTI CURRENCY SIGNAL BOT\n\n"
        "Hakyky bazar maglumatlary esasynda signal almak üçin:\n"
        "/signal\n\n"
        "Aýratyn jübüt:\n"
        "/chfjpy\n"
        "/eurusd\n"
        "/gbpusd"
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📊 HAKYKY WALÝUTA ANALIZI\n"
    text += "⏱ Timeframe: 1 minut\n"
    text += "━━━━━━━━━━━━━━\n\n"

    for code, pair in PAIRS.items():
        result = get_signal(pair)
        text += f"💱 {pair} → {result}\n"

    text += "\n⚠️ Bu tehniki analizdir, 100% kepillik ýok."

    await update.message.reply_text(text)


async def pair_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.replace("/", "").upper()

    pair = PAIRS.get(command)

    if not pair:
        await update.message.reply_text("❌ Walýuta jübüti tapylmady.")
        return

    result = get_signal(pair)

    await update.message.reply_text(
        f"📊 {pair}\n\n"
        f"Signal: {result}\n"
        f"⏱ Timeframe: 1 minut\n\n"
        "⚠️ Tehniki analizdir."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Komandalar:\n\n"
        "/start — Başlat\n"
        "/signal — Ähli walýutalar\n"
        "/eurusd — EUR/USD\n"
        "/gbpusd — GBP/USD\n"
        "/usdjpy — USD/JPY\n"
        "/chfjpy — CHF/JPY\n"
        "/help — Kömek"
    )


def main():
    if not TOKEN:
        print("BOT_TOKEN tapylmady!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("help", help_command))

    for pair in PAIRS:
        app.add_handler(CommandHandler(pair.lower(), pair_signal))

    print("Real market signal bot işledi...")
    app.run_polling()


if __name__ == "__main__":
    main()



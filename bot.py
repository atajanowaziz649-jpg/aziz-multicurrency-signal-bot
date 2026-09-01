import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

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
    "AUD/JPY",
    "CAD/JPY",
    "EUR/CHF",
    "GBP/CHF"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salam!\n\n"
        "📊 MULTI CURRENCY SIGNAL BOT\n\n"
        "Ähli walýuta signallaryny görmek üçin:\n"
        "/signal\n\n"
        "Aýratyn jübüt üçin:\n"
        "/eurusd\n"
        "/gbpusd\n"
        "/chfjpy"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📊 WALÝUTA SIGNALLARY\n"
    text += "⏱ Möhlet: 1 minut\n"
    text += "━━━━━━━━━━━━━━\n\n"

    for pair in PAIRS:
        sig = random.choice(["🟢 CALL", "🔴 PUT"])
        text += f"💱 {pair} → {sig}\n"

    text += "\n⚠️ Signal diňe tehniki görkezme."

    await update.message.reply_text(text)

async def pair_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.replace("/", "").upper()

    pair_map = {
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
        "CHFJPY": "CHF/JPY"
    }

    pair = pair_map.get(command, command)
    sig = random.choice(["🟢 CALL", "🔴 PUT"])

    await update.message.reply_text(
        f"📊 {pair}\n\n"
        f"Signal: {sig}\n"
        f"⏱ Möhlet: 1 minut\n\n"
        "⚠️ Tehniki signal."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Komandalar:\n\n"
        "/start — Başlat\n"
        "/signal — Ähli signallar\n"
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

    for pair in [
        "eurusd", "gbpusd", "usdjpy", "usdchf",
        "audusd", "usdcad", "nzdusd", "eurgbp",
        "eurjpy", "gbpjpy", "chfjpy"
    ]:
        app.add_handler(CommandHandler(pair, pair_signal))

    print("Multi Currency Signal Bot işledi...")
    app.run_polling()

if __name__ == "__main__":
    main()

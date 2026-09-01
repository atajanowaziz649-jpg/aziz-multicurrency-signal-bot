import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
    "EUR/JPY", "GBP/JPY", "AUD/JPY", "CHF/JPY"
]

TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 Multi Currency Signal Bot\n\n"
        "💱 /pairs — Walýuta jübütleri\n"
        "⏱️ /time — Timeframe-lar\n"
        "📈 /signal — Signal\n"
    )
    await update.message.reply_text(text)

async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 Walýuta jübütleri:\n\n" +
        "\n".join(f"• {pair}" for pair in PAIRS)
    )

async def timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏱️ Timeframe-lar:\n\n" +
        "\n".join(f"• {tf}" for tf in TIMEFRAMES)
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Signal ulgamy taýýarlanýar...\n\n"
        "EMA ✅\n"
        "RSI ✅\n"
        "MACD ✅\n"
        "Bollinger Bands ✅\n"
        "ADX ✅\n"
        "Stochastic ✅\n"
        "ATR ✅\n"
        "Support/Resistance ✅\n"
        "Candlestick analysis ✅"
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN tapylmady")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pairs", pairs))
    app.add_handler(CommandHandler("time", timeframes))
    app.add_handler(CommandHandler("signal", signal))

    app.run_polling()

if __name__ == "__main__":
    main()

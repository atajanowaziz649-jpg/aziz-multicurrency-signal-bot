import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

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
    "AUD/JPY",
    "CHF/JPY",
    "GBP/CHF",
    "EUR/CHF",
    "AUD/CAD",
    "AUD/CHF",
    "CAD/JPY",
    "NZD/JPY",
    "EUR/AUD",
    "EUR/CAD",
    "GBP/AUD",
    "GBP/CAD",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Multi Currency Signal Bot\n\n"
        "💱 /pairs — Walýuta jübütleri\n"
        "🎯 /select EUR/USD — Jübüt saýla\n"
        "📈 /signal — Signal\n"
        "⏱️ /time — Timeframe"
    )


async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💱 Walýuta jübütleri:\n\n"

    for pair in PAIRS:
        text += f"• {pair}\n"

    text += "\n🎯 Saýlamak üçin:\n/select EUR/USD"

    await update.message.reply_text(text)


async def select_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❗ Jübüti şeýle saýla:\n\n"
            "/select EUR/USD"
        )
        return

    pair = context.args[0].upper().replace("-", "/")

    if pair not in PAIRS:
        await update.message.reply_text(
            "❌ Bu jübüt sanawda ýok.\n"
            "/pairs bilen elýeterli jübütleri gör."
        )
        return

    context.user_data["pair"] = pair

    await update.message.reply_text(
        f"✅ Saýlanan jübüt: {pair}\n\n"
        "Indi /signal ýaz."
    )


async def timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏱️ Timeframe-lar:\n\n"
        "• 1m\n"
        "• 3m\n"
        "• 5m\n"
        "• 15m\n"
        "• 30m"
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.user_data.get("pair", "EUR/USD")

    await update.message.reply_text(
        f"📊 {pair} — 1 minutlyk analiz\n\n"
        "EMA ⏳\n"
        "RSI ⏳\n"
        "MACD ⏳\n"
        "Bollinger Bands ⏳\n"
        "ADX ⏳\n"
        "Stochastic ⏳\n"
        "ATR ⏳\n"
        "Support/Resistance ⏳\n"
        "Candlestick ⏳\n\n"
        "⚠️ Live market data entek birikdirilmedi.\n"
        "Hakyky BUY/SELL signal üçin bazar maglumat çeşmesi gerek."
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN tapylmady")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pairs", pairs))
    app.add_handler(CommandHandler("select", select_pair))
    app.add_handler(CommandHandler("time", timeframes))
    app.add_handler(CommandHandler("signal", signal))

    print("Signal bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()



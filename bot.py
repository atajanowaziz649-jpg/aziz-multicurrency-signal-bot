import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
    "EUR/JPY", "GBP/JPY", "AUD/JPY", "CHF/JPY"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Multi Currency Signal Bot\n\n"
        "/pairs — Jübütler\n"
        "/select CHF/JPY — Jübüt saýla\n"
        "/signal — Signal al\n"
        "/time — Timeframe"
    )

async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 Walýuta jübütleri:\n\n" +
        "\n".join(f"• {pair}" for pair in PAIRS)
    )

async def select_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Mysal: /select CHF/JPY")
        return

    pair = context.args[0].upper().replace("-", "/")

    if pair not in PAIRS:
        await update.message.reply_text("❌ Bu jübüt sanawda ýok.")
        return

    context.user_data["pair"] = pair

    await update.message.reply_text(
        f"✅ Saýlanan jübüt: {pair}\n\n"
        "Indi /signal ýaz."
    )

async def timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏱️ Timeframe:\n\n"
        "1m\n3m\n5m\n15m\n30m"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.user_data.get("pair", "EUR/USD")

    await update.message.reply_text(
        f"📊 {pair}\n"
        "⏱️ Timeframe: 1 minut\n\n"
        "🔍 Analiz taýýarlanýar...\n\n"
        "⚠️ Live market data entek birikdirilmedi."
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

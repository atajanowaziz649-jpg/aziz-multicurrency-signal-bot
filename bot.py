import os
import logging
import requests
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Free demo endpoint for market data.
# Do not treat this as Pocket Option OTC data.
API_URL = "https://api.frankfurter.app"

PAIRS = {
    "EUR/USD": ("EUR", "USD"),
    "GBP/USD": ("GBP", "USD"),
    "USD/JPY": ("USD", "JPY"),
    "USD/CHF": ("USD", "CHF"),
    "AUD/USD": ("AUD", "USD"),
    "EUR/GBP": ("EUR", "GBP"),
    "EUR/JPY": ("EUR", "JPY"),
    "AUD/CAD": ("AUD", "CAD"),
    "AUD/CHF": ("AUD", "CHF"),
    "USD/CAD": ("USD", "CAD"),
}

TIMEFRAMES = {
    "30s": "30 SEC",
    "1m": "1 MIN",
    "5m": "5 MIN",
    "15m": "15 MIN",
}


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💱 EUR/USD", callback_data="pair|EUR/USD"),
            InlineKeyboardButton("💱 GBP/USD", callback_data="pair|GBP/USD"),
        ],
        [
            InlineKeyboardButton("💱 USD/JPY", callback_data="pair|USD/JPY"),
            InlineKeyboardButton("💱 USD/CHF", callback_data="pair|USD/CHF"),
        ],
        [
            InlineKeyboardButton("💱 AUD/USD", callback_data="pair|AUD/USD"),
            InlineKeyboardButton("💱 EUR/GBP", callback_data="pair|EUR/GBP"),
        ],
        [
            InlineKeyboardButton("💱 EUR/JPY", callback_data="pair|EUR/JPY"),
            InlineKeyboardButton("💱 AUD/CAD", callback_data="pair|AUD/CAD"),
        ],
        [
            InlineKeyboardButton("💱 AUD/CHF", callback_data="pair|AUD/CHF"),
            InlineKeyboardButton("💱 USD/CAD", callback_data="pair|USD/CAD"),
        ],
        [
            InlineKeyboardButton("⏱ 30 SEC", callback_data="tf|30s"),
            InlineKeyboardButton("⏱ 1 MIN", callback_data="tf|1m"),
        ],
        [
            InlineKeyboardButton("⏱ 5 MIN", callback_data="tf|5m"),
            InlineKeyboardButton("⏱ 15 MIN", callback_data="tf|15m"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pair"] = "EUR/USD"
    context.user_data["timeframe"] = "1m"

    await update.message.reply_text(
        "📊 MULTI CURRENCY SIGNAL BOT\n\n"
        "💱 Jübüt saýlaň\n"
        "⏱ Timeframe saýlaň\n\n"
        "⚠️ Maglumat ýok bolsa signal berilmez.",
        reply_markup=main_menu(),
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.user_data.get("pair", "EUR/USD")
    timeframe = context.user_data.get("timeframe", "1m")

    await send_analysis(
        update,
        pair,
        timeframe,
    )


async def send_analysis(update, pair, timeframe):
    timeframe_name = TIMEFRAMES.get(timeframe, "1 MIN")

    text = (
        f"📊 ANALIZ\n\n"
        f"💱 {pair}\n"
        f"⏱ {timeframe_name}\n\n"
        f"🔎 RSI\n"
        f"🔎 MACD\n"
        f"🔎 EMA 9/21\n"
        f"🔎 SMA\n"
        f"🔎 Bollinger Bands\n"
        f"🔎 Stochastic\n"
        f"🔎 ATR\n\n"
        f"⏳ Hakyky maglumat çeşmesi barlanýar...\n\n"
        f"⚠️ Bu wersiýa Pocket Option OTC feed-i däl.\n"
        f"⚠️ OTC diýip galp signal berilmeýär."
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("pair|"):
        pair = data.split("|", 1)[1]
        context.user_data["pair"] = pair

        await query.message.reply_text(
            f"✅ Jübüt saýlandy: {pair}\n\n"
            f"Indi timeframe saýlaň:",
            reply_markup=main_menu(),
        )

    elif data.startswith("tf|"):
        timeframe = data.split("|", 1)[1]
        context.user_data["timeframe"] = timeframe

        pair = context.user_data.get("pair", "EUR/USD")

        await query.message.reply_text(
            f"💱 {pair}\n"
            f"⏱ {TIMEFRAMES[timeframe]}\n\n"
            f"📊 Analiz taýýarlanýar..."
        )

        await send_analysis(
            update,
            pair,
            timeframe,
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 Bot işleýär.\n\n"
        "📊 Multi Currency Signal Bot\n"
        "💱 Currency analysis\n"
        "⏱ 30 SEC / 1 MIN / 5 MIN / 15 MIN"
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN tapylmady.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Signal bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()

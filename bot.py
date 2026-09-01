import os
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

PAIRS = [
    "EUR/USD OTC",
    "GBP/USD OTC",
    "USD/JPY OTC",
    "USD/CHF OTC",
    "AUD/USD OTC",
    "EUR/GBP OTC",
    "EUR/JPY OTC",
    "AUD/CAD OTC",
    "AUD/CHF OTC",
    "USD/CAD OTC",
    "NZD/JPY OTC",
    "EUR/NZD OTC",
]

TIMEFRAMES = {
    "30s": "30 SEC",
    "1m": "1 MIN",
    "5m": "5 MIN",
    "15m": "15 MIN",
}


def menu():
    keyboard = [
        [
            InlineKeyboardButton("💱 EUR/USD OTC", callback_data="pair|EUR/USD OTC"),
            InlineKeyboardButton("💱 GBP/USD OTC", callback_data="pair|GBP/USD OTC"),
        ],
        [
            InlineKeyboardButton("💱 USD/JPY OTC", callback_data="pair|USD/JPY OTC"),
            InlineKeyboardButton("💱 USD/CHF OTC", callback_data="pair|USD/CHF OTC"),
        ],
        [
            InlineKeyboardButton("💱 AUD/USD OTC", callback_data="pair|AUD/USD OTC"),
            InlineKeyboardButton("💱 EUR/JPY OTC", callback_data="pair|EUR/JPY OTC"),
        ],
        [
            InlineKeyboardButton("💱 AUD/CAD OTC", callback_data="pair|AUD/CAD OTC"),
            InlineKeyboardButton("💱 AUD/CHF OTC", callback_data="pair|AUD/CHF OTC"),
        ],
        [
            InlineKeyboardButton("⏱ 30 SEC", callback_data="tf|30s"),
            InlineKeyboardButton("⏱ 1 MIN", callback_data="tf|1m"),
        ],
        [
            InlineKeyboardButton("⏱ 5 MIN", callback_data="tf|5m"),
            InlineKeyboardButton("⏱ 15 MIN", callback_data="tf|15m"),
        ],
        [
            InlineKeyboardButton("📊 SIGNAL", callback_data="signal"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pair"] = "AUD/USD OTC"
    context.user_data["timeframe"] = "1m"

    await update.message.reply_text(
        "📊 OTC SIGNAL BOT\n\n"
        "💱 Walýuta jübüdini saýla\n"
        "⏱ Timeframe saýla\n\n"
        "Soň 📊 SIGNAL bas.",
        reply_markup=menu(),
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.user_data.get("pair", "AUD/USD OTC")
    timeframe = context.user_data.get("timeframe", "1m")

    await update.message.reply_text(
        f"📊 OTC SIGNAL\n\n"
        f"💱 {pair}\n"
        f"⏱ {TIMEFRAMES[timeframe]}\n\n"
        f"⏳ Hakyky OTC maglumat garaşylýar...\n\n"
        f"⚠️ Maglumat ýok wagty CALL/PUT döredilmeýär."
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("pair|"):
        pair = data.split("|", 1)[1]
        context.user_data["pair"] = pair

        await query.message.reply_text(
            f"✅ {pair}\n\n"
            f"⏱ Timeframe saýla:",
            reply_markup=menu(),
        )

    elif data.startswith("tf|"):
        tf = data.split("|", 1)[1]
        context.user_data["timeframe"] = tf

        await query.message.reply_text(
            f"💱 {context.user_data.get('pair', 'AUD/USD OTC')}\n"
            f"⏱ {TIMEFRAMES[tf]}\n\n"
            f"📊 Indi SIGNAL bas.",
            reply_markup=menu(),
        )

    elif data == "signal":
        pair = context.user_data.get("pair", "AUD/USD OTC")
        tf = context.user_data.get("timeframe", "1m")

        await query.message.reply_text(
            f"📊 OTC SIGNAL\n\n"
            f"💱 {pair}\n"
            f"⏱ {TIMEFRAMES[tf]}\n\n"
            f"⏳ Hakyky signal maglumat garaşylýar...\n\n"
            f"⚠️ Hakyky maglumat bolmasa signal berilmeýär."
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN tapylmady.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CallbackQueryHandler(buttons))

    print("OTC Signal Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()

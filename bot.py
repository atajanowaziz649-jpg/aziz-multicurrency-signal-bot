import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

PAIRS = [
    "EUR/USD OTC",
    "GBP/USD OTC",
    "USD/JPY OTC",
    "CHF/JPY OTC",
    "AUD/USD OTC",
    "EUR/GBP OTC",
    "USD/CHF OTC",
    "EUR/JPY OTC",
]

TIMEFRAMES = ["30 SEC", "1 MIN", "5 MIN", "15 MIN"]

user_pair = {}
user_timeframe = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💱 Walýuta saýla", callback_data="pairs")],
        [InlineKeyboardButton("⏱ Timeframe saýla", callback_data="timeframes")],
        [InlineKeyboardButton("📊 Signal al", callback_data="signal")],
    ]

    await update.message.reply_text(
        "🤖 Multi Currency OTC Signal Bot\n\n"
        "📊 Hakyky maglumat esasynda analiz ulgamy\n"
        "💱 Köp OTC walýuta\n"
        "⏱ Birnäçe timeframe\n"
        "📈 Köp indikator\n\n"
        "Aşakdan saýla:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pairs":
        keyboard = [
            [InlineKeyboardButton(p, callback_data=f"pair:{p}")]
            for p in PAIRS
        ]
        await query.edit_message_text(
            "💱 Walýutany saýla:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "timeframes":
        keyboard = [
            [InlineKeyboardButton(t, callback_data=f"time:{t}")]
            for t in TIMEFRAMES
        ]
        await query.edit_message_text(
            "⏱ Timeframe saýla:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data.startswith("pair:"):
        pair = query.data.replace("pair:", "")
        user_pair[query.from_user.id] = pair

        await query.edit_message_text(
            f"✅ Walýuta saýlandy:\n\n💱 {pair}\n\n"
            "Indi /timeframe bilen timeframe saýla."
        )

    elif query.data.startswith("time:"):
        timeframe = query.data.replace("time:", "")
        user_timeframe[query.from_user.id] = timeframe

        await query.edit_message_text(
            f"✅ Timeframe saýlandy:\n\n⏱ {timeframe}\n\n"
            "Signal almak üçin /signal ýaz."
        )

    elif query.data == "signal":
        await send_signal(query, context)


async def send_signal(query, context):
    uid = query.from_user.id

    pair = user_pair.get(uid)
    timeframe = user_timeframe.get(uid)

    if not pair or not timeframe:
        await query.edit_message_text(
            "⚠️ Ilki walýuta we timeframe saýla."
        )
        return

    await query.edit_message_text(
        "📊 Maglumat alynýar...\n"
        "🔎 RSI\n"
        "🔎 MACD\n"
        "🔎 EMA\n"
        "🔎 Bollinger Bands\n"
        "🔎 Stochastic\n\n"
        "⏳ Signal taýýarlanýar..."
    )

    # Bu ýerde hakyky bazar maglumat çeşmesi birikdiriler.
    # Maglumat ýok wagty bot signal oýlap çykarmaly däl.

    await query.message.reply_text(
        f"⚠️ Häzir {pair} üçin {timeframe} maglumat çeşmesi ýok.\n\n"
        "Şonuň üçin bot ýalan/test signal bermedi."
    )


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    pair = user_pair.get(uid)
    timeframe = user_timeframe.get(uid)

    if not pair or not timeframe:
        await update.message.reply_text(
            "⚠️ Ilki /start basyp walýuta we timeframe saýla."
        )
        return

    await update.message.reply_text(
        f"📊 ANALIZ\n\n"
        f"💱 {pair}\n"
        f"⏱ {timeframe}\n\n"
        "🔎 RSI\n"
        "🔎 MACD\n"
        "🔎 EMA\n"
        "🔎 Bollinger Bands\n"
        "🔎 Stochastic\n\n"
        "⏳ Hakyky maglumat garaşylýar...\n"
        "⚠️ Maglumat ýok wagty signal berilmeýär."
    )


async def timeframe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(t, callback_data=f"time:{t}")]
        for t in TIMEFRAMES
    ]

    await update.message.reply_text(
        "⏱ Timeframe saýla:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN tapylmady")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("timeframe", timeframe_command))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot işledi...")
    app.run_polling()


if __name__ == "__main__":
    main()

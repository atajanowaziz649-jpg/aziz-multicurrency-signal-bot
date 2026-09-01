import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
    "EUR/JPY", "GBP/JPY", "AUD/JPY", "CHF/JPY"
]

TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m"]


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Multi Currency Signal Bot is running")

    def log_message(self, format, *args):
        pass


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Multi Currency Signal Bot\n\n"
        "💱 /pairs — Walýuta jübütleri\n"
        "⏱️ /time — Timeframe-lar\n"
        "📈 /signal — Signal"
    )


async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 Walýuta jübütleri:\n\n"
        + "\n".join(f"• {pair}" for pair in PAIRS)
    )


async def timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏱️ Timeframe-lar:\n\n"
        + "\n".join(f"• {tf}" for tf in TIMEFRAMES)
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Signal analiz ulgamy\n\n"
        "EMA ✅\n"
        "RSI ✅\n"
        "MACD ✅\n"
        "Bollinger Bands ✅\n"
        "ADX ✅\n"
        "Stochastic ✅\n"
        "ATR ✅\n"
        "Support/Resistance ✅\n"
        "Candlestick ✅\n\n"
        "⏱️ Timeframe: 1m / 3m / 5m / 15m / 30m\n"
        "💱 Köp walýuta jübütleri\n\n"
        "⚠️ Hakyky BUY/SELL üçin live market data API birikdirilmeli."
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN tapylmady")

    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pairs", pairs))
    app.add_handler(CommandHandler("time", timeframes))
    app.add_handler(CommandHandler("signal", signal))

    app.run_polling()


if __name__ == "__main__":
    main()

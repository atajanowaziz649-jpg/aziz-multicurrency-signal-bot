import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 OTC Signal Bot\n\n"
        "📊 Signal almak üçin /signal ýazyň\n"
        "💱 Walýuta: CHF/JPY OTC\n"
        "⏱ Timeframe: 1 minut"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 OTC SIGNAL\n\n"
        "💱 CHF/JPY OTC\n"
        "⏱ 1 MIN\n"
        "🟢 CALL\n\n"
        "⚠️ Bu diňe test signalydyr."
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN tapylmady!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    print("Signal bot isledi...")
    app.run_polling()

if __name__ == "__main__":
    main()

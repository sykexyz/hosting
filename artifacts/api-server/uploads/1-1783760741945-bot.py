from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = "8449404840:AAHhLAN0KTtZudbSThVB7Gj7M4lidf_bIc4"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot is online!\n\n"
        "Use /ping or /info."
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    text = (
        f"👤 User: {user.full_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"💬 Chat ID: {chat.id}\n"
        f"🤖 Status: Online"
    )

    await update.message.reply_text(text)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("info", info))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
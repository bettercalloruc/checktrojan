from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from ai import ask_girlfriend_bot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

chat_histories = {}  # Sadə şəkildə yadda saxlamaq üçün

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam canım 🥰 Mən sənin sevgilinəm. Mənimlə istədiyin kimi danışa bilərsən 💌")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_history = chat_histories[user_id]
    response = ask_girlfriend_bot(user_message, chat_history)

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": response})

    await update.message.reply_text(response)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

if __name__ == "__main__":
    app.run_polling()

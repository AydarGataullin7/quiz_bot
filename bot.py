import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TG_TOKEN')


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для викторины")


def echo(update: Update, context: CallbackContext):
    user_text = update.message.text
    update.message.reply_text(user_text)


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

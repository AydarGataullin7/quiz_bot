import os
import json
import random
import redis
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TG_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

START, QUESTION = range(2)


def start(update: Update, context: CallbackContext):
    reply_markup = context.bot_data.get('reply_markup')
    update.message.reply_text("Привет! Я бот для викторины", reply_markup=reply_markup)
    return START


def handle_new_question(update: Update, context: CallbackContext):
    user_text = update.message.text
    if user_text in ['Сдаться', 'Мой счет']:
        update.message.reply_text('Нажмите "Новый вопрос" чтобы начать викторину')
        return START
    user_id = update.effective_user.id
    questions_list = context.bot_data.get('questions_list')
    redis_client = context.bot_data.get('redis_client')
    random_question = random.choice(questions_list)
    question_text = random_question[0]
    answer = random_question[1]
    redis_client.set(f'tg_user_{user_id}_answer', answer)
    if '\n' in question_text:
        question = question_text.split('\n', 1)[1]
    else:
        question = question_text
    update.message.reply_text(question)
    return QUESTION


def handle_answer(update: Update, context: CallbackContext):
    user_text = update.message.text
    if user_text == 'Новый вопрос':
        return handle_new_question(update, context)
    user_id = update.effective_user.id
    redis_client = context.bot_data.get('redis_client')
    saved_answer = redis_client.get(f'tg_user_{user_id}_answer')
    if not saved_answer:
        update.message.reply_text('Нажмите "Новый вопрос"')
    elif saved_answer.lower().strip().rstrip('.,') == user_text.lower().strip().rstrip('.,'):
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        redis_client.delete(f'tg_user_{user_id}_answer')
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')
    return QUESTION


def handle_give_up(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    redis_client = context.bot_data.get('redis_client')
    saved_answer = redis_client.get(f'tg_user_{user_id}_answer')
    if saved_answer:
        update.message.reply_text(f'Правильный ответ: {saved_answer}')
        redis_client.delete(f'tg_user_{user_id}_answer')
        update.message.text = 'Новый вопрос'
        return handle_new_question(update, context)
    return QUESTION


def main():
    if not TOKEN:
        print("Ошибка: токен не найден! Проверьте файл .env")
        return

    with open('questions.json', 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    questions_list = list(all_questions.items())

    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет'],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )

    def start_wrapper(update: Update, context: CallbackContext):
        context.bot_data['reply_markup'] = reply_markup
        return start(update, context)

    def new_question_wrapper(update: Update, context: CallbackContext):
        context.bot_data['questions_list'] = questions_list
        context.bot_data['redis_client'] = redis_client
        return handle_new_question(update, context)

    def answer_wrapper(update: Update, context: CallbackContext):
        context.bot_data['redis_client'] = redis_client
        return handle_answer(update, context)

    def give_up_wrapper(update: Update, context: CallbackContext):
        context.bot_data['redis_client'] = redis_client
        return handle_give_up(update, context)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_wrapper)],
        states={
            START: [
                MessageHandler(Filters.regex('^Новый вопрос$'), new_question_wrapper),
            ],
            QUESTION: [
                MessageHandler(Filters.regex('Сдаться'), give_up_wrapper),
                MessageHandler(Filters.text & ~Filters.command, answer_wrapper),
            ],
        },
        fallbacks=[CommandHandler('start', start_wrapper)],
    )

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

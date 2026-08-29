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
START, QUESTION = range(2)

with open('questions.json', 'r', encoding='utf-8') as f:
    all_questions = json.load(f)
questions_list = list(all_questions.items())

custom_keyboard = [
    ['Новый вопрос', 'Сдаться'],
    ['Мой счет'],
]
reply_markup = ReplyKeyboardMarkup(custom_keyboard)

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для викторины", reply_markup=reply_markup)
    return START

def new_question(update: Update, context: CallbackContext):
    user_text = update.message.text
    if user_text in ['Сдаться', 'Мой счет']:
        update.message.reply_text('Нажмите "Новый вопрос" чтобы начать викторину')
        return START
    user_id = update.effective_user.id
    random_question = random.choice(questions_list)
    question_text = random_question[0]
    answer = random_question[1]
    r.set(f'user_{user_id}_answer', answer)
    if '\n' in question_text:
        question = question_text.split('\n', 1)[1]
    else:
        question = question_text
    update.message.reply_text(question)
    return QUESTION

def check_answer(update: Update, context: CallbackContext):
    user_text = update.message.text
    if user_text == 'Новый вопрос':
        return new_question(update, context)
    user_id = update.effective_user.id
    saved_answer = r.get(f'user_{user_id}_answer')
    if not saved_answer:
        update.message.reply_text('Нажмите "Новый вопрос"')
    elif saved_answer.lower().strip().rstrip('.,') == user_text.lower().strip().rstrip('.,'):
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        r.delete(f'user_{user_id}_answer')
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')
    return QUESTION

def give_up(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    saved_answer = r.get(f'user_{user_id}_answer')
    if saved_answer:
        update.message.reply_text(f'Правильный ответ: {saved_answer}')
        r.delete(f'user_{user_id}_answer')
        update.message.text = 'Новый вопрос'
        return new_question(update, context)
    return QUESTION


def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [
                MessageHandler(Filters.regex('^Новый вопрос$'), new_question),
            ],
            QUESTION: [
                MessageHandler(Filters.regex('Сдаться'), give_up),
                MessageHandler(Filters.text & ~Filters.command, check_answer),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

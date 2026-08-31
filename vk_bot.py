import os
import json
import random
import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


def send_message(vk_api, user_id, message, keyboard=None, questions_list=None, redis_client=None):
    vk_api.messages.send(
        user_id=user_id,
        message=message,
        random_id=random.randint(1, 10000),
        keyboard=keyboard.get_keyboard() if keyboard else None
    )


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)
    return keyboard


def handle_start(event, vk_api):
    keyboard = create_keyboard()
    send_message(
        vk_api,
        event.user_id,
        'Привет! Чтобы начать нажми "Новый вопрос"',
        keyboard
    )


def handle_new_question(event, vk_api, keyboard, questions_list, redis_client):
    user_id = event.user_id
    random_question = random.choice(questions_list)
    question_text = random_question[0]
    answer = random_question[1]
    redis_client.set(f'vk_user_{user_id}_answer', answer)
    if '\n' in question_text:
        question = question_text.split('\n', 1)[1]
    else:
        question = question_text
    send_message(vk_api, user_id, question, keyboard)


def handle_give_up(event, vk_api, keyboard, questions_list, redis_client):
    user_id = event.user_id
    correct_answer = redis_client.get(f'vk_user_{user_id}_answer')
    if correct_answer:
        send_message(vk_api, user_id, f'Правильный ответ: {correct_answer}', keyboard)
        redis_client.delete(f'vk_user_{user_id}_answer')
        handle_new_question(event, vk_api, keyboard, questions_list, redis_client)
    else:
        send_message(vk_api, user_id, 'Нажми "Новый вопрос" чтобы начать', keyboard)


def handle_answer(event, vk_api, keyboard, redis_client):
    user_id = event.user_id
    user_text = event.text
    saved_answer = redis_client.get(f'vk_user_{user_id}_answer')
    if saved_answer:
        if saved_answer.lower().strip().rstrip('.,') == user_text.lower().strip().rstrip('.,'):
            send_message(vk_api, user_id, 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»', keyboard)
            redis_client.delete(f'vk_user_{user_id}_answer')
        else:
            send_message(vk_api, user_id, 'Неправильно... Попробуешь ещё раз?', keyboard)
    else:
        send_message(vk_api, user_id, 'Нажми "Новый вопрос" чтобы начать', keyboard)


def handle_message(event, vk_api, questions_list, redis_client):
    user_text = event.text
    keyboard = create_keyboard()

    if user_text == 'Начать':
        handle_start(event, vk_api)
    elif user_text == 'Новый вопрос':
        handle_new_question(event, vk_api, keyboard, questions_list, redis_client)
    elif user_text == 'Сдаться':
        handle_give_up(event, vk_api, keyboard, questions_list, redis_client)
    else:
        handle_answer(event, vk_api, keyboard, redis_client)


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv('VK_TOKEN')

    if not token:
        print("Ошибка: токен не найден! Проверьте файл .env")
        exit()

    with open('questions.json', 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    questions_list = list(all_questions.items())

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk_api, questions_list, redis_client)

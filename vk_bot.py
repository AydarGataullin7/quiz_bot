import os
import json
import random
import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

TOKEN = os.getenv('VK_TOKEN')

with open('questions.json', 'r', encoding='utf-8') as f:
    all_questions = json.load(f)
questions_list = list(all_questions.items())
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def question(event, vk_api):
    user_id = event.user_id
    user_text = event.text
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    if user_text == 'Начать':
        vk_api.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Привет! Чтобы начать нажми "Новый вопрос"'
        )

    elif user_text == 'Новый вопрос':
        random_question = random.choice(questions_list)
        question_text = random_question[0]
        answer = random_question[1]
        r.set(f'user_{user_id}_answer', answer)
        if '\n' in question_text:
            question = question_text.split('\n', 1)[1]
        else:
            question = question_text
        vk_api.messages.send(
            user_id=event.user_id,
            message=question,
            random_id=random.randint(1,10000),
            keyboard=keyboard.get_keyboard()
        )

    elif user_text == 'Сдаться':
        correct_answer = r.get(f'user_{user_id}_answer')
        if correct_answer:
            vk_api.messages.send(
                user_id=event.user_id,
                message=f'Правильный ответ: {correct_answer}',
                random_id=random.randint(1,10000),
                keyboard=keyboard.get_keyboard()
            )
            r.delete(f'user_{user_id}_answer')

            random_question = random.choice(questions_list)
            question_text = random_question[0]
            answer = random_question[1]
            r.set(f'user_{user_id}_answer', answer)
            if '\n' in question_text:
                question = question_text.split('\n', 1)[1]
            else:
                question = question_text
            vk_api.messages.send(
                user_id=event.user_id,
                message=question,
                random_id=random.randint(1,10000),
                keyboard=keyboard.get_keyboard()
            )
        else:
            vk_api.messages.send(
                user_id=event.user_id,
                message='Нажми "Новый вопрос" чтобы начать',
                random_id=random.randint(1,10000),
                keyboard=keyboard.get_keyboard()
            )

    else:
        saved_answer = r.get(f'user_{user_id}_answer')
        if saved_answer:
            if saved_answer.lower().strip().rstrip('.,') == user_text.lower().strip().rstrip('.,'):
                vk_api.messages.send(
                    user_id=event.user_id,
                    message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                    random_id=random.randint(1,10000),
                    keyboard=keyboard.get_keyboard()
                )
                r.delete(f'user_{user_id}_answer')
            else:
                vk_api.messages.send(
                    user_id=event.user_id,
                    message='Неправильно... Попробуешь ещё раз?',
                    random_id=random.randint(1,10000),
                    keyboard=keyboard.get_keyboard()
                )
        else:
            vk_api.messages.send(
                user_id=event.user_id,
                message='Нажми "Новый вопрос" чтобы начать',
                random_id=random.randint(1,10000),
                keyboard=keyboard.get_keyboard()
            )

if __name__ == "__main__":
    load_dotenv()
    vk_session = vk.VkApi(token=TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            question(event, vk_api)

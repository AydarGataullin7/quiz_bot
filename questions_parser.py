import os
import json

QUESTIONS_FOLDER = r'D:\python_scripts\quiz_bot\questions'


def main():
    all_files = os.listdir(QUESTIONS_FOLDER)
    all_questions = {}

    for questions_file in all_files:
        full_path = QUESTIONS_FOLDER + "\\" + questions_file
        with open(full_path, 'r', encoding='koi8-r') as file:
            content = file.read()

        blocks = content.split('\n\n')

        i = 0
        while i < len(blocks):
            block = blocks[i].strip()

            if block.startswith('Вопрос'):
                question_text = block

                answer_text = None
                j = i + 1
                while j < len(blocks):
                    if blocks[j].strip().startswith('Ответ'):
                        answer_text = blocks[j].replace('Ответ:', '').strip()
                        break
                    j += 1

                if question_text and answer_text:
                    all_questions[question_text] = answer_text

                i = j + 1
            else:
                i += 1

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print(f"Найдено вопросов: {len(all_questions)}")


if __name__ == "__main__":
    main()

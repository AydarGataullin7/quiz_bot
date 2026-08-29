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

        block_index = 0
        while block_index < len(blocks):
            current_block = blocks[block_index].strip()

            if current_block.startswith('Вопрос'):
                question_text = current_block

                answer_text = None
                answer_index = block_index + 1
                while answer_index < len(blocks):
                    if blocks[answer_index].strip().startswith('Ответ'):
                        answer_text = blocks[answer_index].replace('Ответ:', '').strip()
                        break
                    answer_index += 1

                if question_text and answer_text:
                    all_questions[question_text] = answer_text

                block_index = answer_index + 1
            else:
                block_index += 1

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print(f"Найдено вопросов: {len(all_questions)}")


if __name__ == "__main__":
    main()

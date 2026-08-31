import os
import json
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Парсер вопросов из текстовых файлов в JSON."
    )
    parser.add_argument(
        "--folder",
        "-f",
        type=str,
        default=r'D:\python_scripts\quiz_bot\questions',
        help="Путь к папке с файлами вопросов (по умолчанию: D:\python_scripts\quiz_bot\questions)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="questions.json",
        help="Имя выходного JSON-файла (по умолчанию: questions.json)"
    )
    return parser.parse_args()


def parse_file(file_path):
    with open(file_path, 'r', encoding='koi8-r') as file:
        content = file.read()

    blocks = content.split('\n\n')
    questions = {}

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
                questions[question_text] = answer_text

            block_index = answer_index + 1
        else:
            block_index += 1

    return questions


def main():
    args = parse_arguments()

    if not os.path.exists(args.folder):
        print(f"Ошибка: папка '{args.folder}' не найдена!")
        return

    all_questions = {}
    for questions_file in os.listdir(args.folder):
        full_path = os.path.join(args.folder, questions_file)
        questions = parse_file(full_path)
        all_questions.update(questions)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

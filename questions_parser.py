import os
import json
import argparse  # ← добавляем импорт


def main():
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
    args = parser.parse_args()

    questions_folder = args.folder
    output_file = args.output

    # === Проверка, что папка существует ===
    if not os.path.exists(questions_folder):
        print(f"Ошибка: папка '{questions_folder}' не найдена!")
        return

    # === Основной код парсера ===
    all_files = os.listdir(questions_folder)
    all_questions = {}

    for questions_file in all_files:
        full_path = os.path.join(questions_folder, questions_file)
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

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

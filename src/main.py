"""
Главный скрипт для морфологического анализа текста.

Этот скрипт координирует весь процесс:
1. Чтение текста из файла
2. Обработка текста
3. Морфологический анализ
4. Разбиение слов на слоги
5. Построение префиксного дерева
6. Визуализация результатов
"""

import os
import json
import argparse
import time
from tqdm import tqdm

from morpho_analyzer.text_processor import read_text_file, tokenize_text, clean_word, normalize_text
from morpho_analyzer.morphology import MorphologicalAnalyzer
from morpho_analyzer.syllables import split_into_syllables, get_syllabification_stats
from morpho_analyzer.trie import PrefixTree
from morpho_analyzer.visualization import (visualize_trie, visualize_parts_of_speech,
                                         visualize_syllable_statistics,
                                         visualize_trie_statistics, create_summary_report,
                                         visualize_trie_interactive, export_to_excel,
                                         create_simplified_trie)


def parse_arguments():
    """
    Обрабатывает аргументы командной строки.
    
    Returns:
        Объект с аргументами
    """
    parser = argparse.ArgumentParser(description='Морфологический анализ текста с сохранением в префиксном дереве')
    
    parser.add_argument('--input', '-i', type=str, required=True,
                      help='Путь к входному текстовому файлу')
    
    parser.add_argument('--output-dir', '-o', type=str, default='data/output',
                      help='Директория для сохранения результатов')
    
    parser.add_argument('--max-words', '-m', type=int, default=0,
                      help='Максимальное количество слов для обработки (0 = все слова)')
    
    parser.add_argument('--keep-punctuation', '-p', action='store_true',
                      help='Сохранять знаки препинания в токенизированном тексте')
    
    parser.add_argument('--trie-depth', '-d', type=int, default=5,
                      help='Максимальная глубина для визуализации префиксного дерева')
    
    parser.add_argument('--simplified-visualization', '-s', action='store_true',
                      help='Создавать упрощенную визуализацию дерева (100 слов) в дополнение к полной')
    
    parser.add_argument('--simplified-max-words', type=int, default=100,
                      help='Максимальное количество слов в упрощенной визуализации (по умолчанию 100)')
    
    return parser.parse_args()


def main():
    """
    Основная функция скрипта.
    """
    # Получаем аргументы командной строки
    args = parse_arguments()
    
    # Создаем директорию для вывода, если она не существует
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Начинаю обработку файла: {args.input}")
    start_time = time.time()
    
    # Шаг 1: Чтение текста
    print("Чтение текста из файла...")
    text = read_text_file(args.input)
    
    # Шаг 2: Обработка текста
    print("Токенизация текста...")
    tokens = tokenize_text(text, keep_punctuation=args.keep_punctuation)
    
    # Ограничиваем количество слов, если указано
    if args.max_words > 0 and len(tokens) > args.max_words:
        print(f"Ограничиваем анализ первыми {args.max_words} словами из {len(tokens)}")
        tokens = tokens[:args.max_words]
    
    # Отфильтровываем знаки препинания и пустые токены для дальнейшего анализа
    words = [token for token in tokens if token and token[0].isalpha()]
    
    # Шаг 3: Морфологический анализ
    print("Выполнение морфологического анализа...")
    morph_analyzer = MorphologicalAnalyzer()
    
    # Анализируем текст
    analyzed_text = []
    for i, token in enumerate(tqdm(tokens)):
        # Анализируем только слова (не знаки препинания)
        if token and token[0].isalpha():
            # Получаем контекст (предыдущие и следующие слова)
            prev_words = tokens[max(0, i-3):i]
            next_words = tokens[i+1:min(len(tokens), i+4)]
            
            # Выполняем морфологический анализ с разрешением омонимии
            analysis = morph_analyzer.analyze_token_with_homonym_resolution(token, prev_words, next_words)
            
            # Если слово было успешно проанализировано, добавляем его в результаты
            if analysis:
                analyzed_text.append(analysis)
    
    print(f"Проанализировано {len(analyzed_text)} слов")
    
    # Шаг 4: Разбиение слов на слоги и сбор статистики
    print("Разбиение слов на слоги...")
    syllable_data = {}
    all_words = [item['word'] for item in analyzed_text]
    
    # Собираем статистику по слогам
    syllable_stats = get_syllabification_stats(all_words)
    
    # Разбиваем каждое слово на слоги
    for item in analyzed_text:
        word = item['word']
        syllables = split_into_syllables(word)
        syllable_data[word] = syllables
        item['syllables'] = syllables
    
    # Шаг 5: Построение префиксного дерева
    print("Построение префиксного дерева...")
    trie = PrefixTree()
    
    # Добавляем слова в дерево
    for item in analyzed_text:
        trie.insert(item['syllables'], item)
    
    # Шаг 6: Визуализация результатов
    print("Создание визуализаций...")
    
    # Визуализация префиксного дерева
    trie_image_path = os.path.join(args.output_dir, "trie_visualization.png")
    visualize_trie(trie, max_depth=args.trie_depth, 
                  output_path=trie_image_path, 
                  title="Префиксное дерево слогов")
    
    # Визуализация частей речи
    pos_image_path = os.path.join(args.output_dir, "parts_of_speech.png")
    visualize_parts_of_speech(analyzed_text, 
                             output_path=pos_image_path,
                             title="Распределение частей речи в тексте")
    
    # Визуализация статистики по слогам
    syllable_image_path = os.path.join(args.output_dir, "syllable_statistics.png")
    visualize_syllable_statistics(syllable_stats,
                                output_path=syllable_image_path,
                                title="Статистика слогов")
    
    # Интерактивная HTML-визуализация префиксного дерева
    trie_html_path = os.path.join(args.output_dir, "trie_interactive.html")
    visualize_trie_interactive(trie, max_depth=args.trie_depth,
                             output_path=trie_html_path,
                             title="Интерактивное префиксное дерево слогов (полное)")
    
    # Создаем упрощенную версию дерева (хранит не более 100 слов)
    # Делаем это если указан флаг --simplified-visualization
    # Или автоматически при обработке PDF-файла
    file_extension = os.path.splitext(args.input)[1].lower()
    if args.simplified_visualization or file_extension == '.pdf':
        simplified_trie = create_simplified_trie(trie, max_words=args.simplified_max_words)
        simplified_html_path = os.path.join(args.output_dir, "trie_interactive_simplified.html")
        visualize_trie_interactive(simplified_trie, max_depth=args.trie_depth,
                               output_path=simplified_html_path,
                               title=f"Интерактивное префиксное дерево слогов (упрощенное, {args.simplified_max_words} слов)")
    
    # Визуализация статистики префиксного дерева
    trie_stats_image_path = os.path.join(args.output_dir, "trie_statistics.png")
    visualize_trie_statistics(trie.get_statistics(),
                            output_path=trie_stats_image_path,
                            title="Статистика префиксного дерева")
                            
    # Экспорт результатов в Excel с русифицированными свойствами
    excel_path = os.path.join(args.output_dir, "morphological_analysis.xlsx")
    export_to_excel(analyzed_text, 
                  output_path=excel_path, 
                  sheet_name="Морфологический анализ")
    
    # Создание отчета
    report_path = os.path.join(args.output_dir, "analysis_report.md")
    create_summary_report(analyzed_text, trie, syllable_stats, output_path=report_path)
    
    # Шаг 7: Экспорт и сохранение результатов 
    print("Сохранение результатов...")
    results_json_path = os.path.join(args.output_dir, "analysis_results.json")
    
    # Подготовка данных для сериализации
    output_data = {
        "analyzed_text": analyzed_text,
        "syllable_stats": syllable_stats,
        "trie": trie.serialize()
    }
    
    # Создаем класс пользовательского кодировщика JSON для объектов pymorphy2
    class MorphoJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            # Обрабатываем объекты pymorphy2.analyzer.Parse
            if hasattr(obj, 'tag') and hasattr(obj, 'normal_form'):
                return {
                    'normal_form': obj.normal_form,
                    'pos': str(obj.tag.POS),
                    'tag': str(obj.tag)
                }
            # Обрабатываем объекты pymorphy2.tagset.OpencorporaTag
            if hasattr(obj, 'POS') and hasattr(obj, 'grammemes'):
                return str(obj)
            # Для всех остальных типов используем стандартный механизм
            return json.JSONEncoder.default(self, obj)
    
    # Сохранение в JSON с использованием кодировщика
    with open(results_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, cls=MorphoJSONEncoder)
    
    # Вывод информации о завершении
    elapsed_time = time.time() - start_time
    print(f"Анализ завершен за {elapsed_time:.2f} секунд")
    print(f"Результаты сохранены в директории: {args.output_dir}")
    print(f"Отчет в формате Markdown: {report_path}")
    print(f"JSON с результатами анализа: {results_json_path}")
    print(f"Excel с русифицированным анализом: {excel_path}")


if __name__ == "__main__":
    main()

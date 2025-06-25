#!/usr/bin/env python3
"""
Скрипт для проверки результатов морфологического анализа,
особенно разрешения омонимов
"""

import pandas as pd
import sys

def analyze_excel_results(file_path):
    """Анализирует результаты морфологического анализа из Excel-файла"""
    
    print(f"Анализ файла: {file_path}")
    print("-" * 50)
    
    # Чтение Excel-файла
    df = pd.read_excel(file_path)
    
    # Получаем список всех омонимов из тестового файла
    homonyms = ['стекло', 'печь', 'три', 'ключи', 'лук', 'стали', 'мир', 'вести', 'коса', 'белки']
    
    # Анализируем каждый омоним
    for homonym in homonyms:
        # Фильтруем датафрейм по омониму
        homonym_entries = df[df['Слово'].str.lower() == homonym.lower()]
        
        if len(homonym_entries) == 0:
            print(f"Омоним '{homonym}' не найден в результатах анализа")
            continue
            
        print(f"\nАнализ омонима: '{homonym}' ({len(homonym_entries)} вхождений)")
        
        # Выводим информацию по каждому вхождению
        for i, entry in homonym_entries.iterrows():
            context = f"{entry.get('Предшествующее слово 3', '')} {entry.get('Предшествующее слово 2', '')} {entry.get('Предшествующее слово 1', '')} [{entry['Слово']}] {entry.get('Следующее слово 1', '')} {entry.get('Следующее слово 2', '')} {entry.get('Следующее слово 3', '')}"
            sense = entry.get('Значение омонима', 'не указано')
            pos = entry.get('Часть речи', 'не указана')
            
            print(f"  Контекст: {context.strip()}")
            print(f"  Значение: {sense}")
            print(f"  Часть речи: {pos}")
            print(f"  Морф. тэги: {entry.get('Морфологические характеристики', '')}")
            print("  " + "-" * 40)

if __name__ == "__main__":
    # Файл для анализа
    file_path = "data/output/morphological_analysis.xlsx"
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    analyze_excel_results(file_path)

"""
Тесты для модуля разделения слов на слоги.
"""

import os
import sys
import unittest

# Добавляем корневой каталог проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.morpho_analyzer.syllables import (
    split_into_syllables,
    split_word_into_syllables_alt,
    get_syllables_count,
    get_syllabification_stats
)


class TestSyllables(unittest.TestCase):
    """
    Набор тестов для функций разделения слов на слоги.
    """
    
    def test_split_into_syllables(self):
        """
        Тест основного алгоритма разделения на слоги.
        """
        # Проверяем стандартные случаи
        self.assertEqual(split_into_syllables("молоко"), ['мо', 'ло', 'ко'])
        self.assertEqual(split_into_syllables("книга"), ['кни', 'га'])
        self.assertEqual(split_into_syllables("яблоко"), ['яб', 'ло', 'ко'])
        self.assertEqual(split_into_syllables("дерево"), ['де', 'ре', 'во'])
        self.assertEqual(split_into_syllables("стол"), ['стол'])
        
        # Проверяем слова с мягким знаком
        self.assertEqual(split_into_syllables("учитель"), ['у', 'чи', 'тель'])
        
        # Проверяем слова с гласными подряд
        self.assertEqual(split_into_syllables("наука"), ['на', 'у', 'ка'])
        
        # Проверяем слова с сочетаниями согласных
        self.assertEqual(split_into_syllables("пример"), ['при', 'мер'])
        self.assertEqual(split_into_syllables("встреча"), ['встре', 'ча'])
        
        # Проверяем слова без гласных
        self.assertEqual(split_into_syllables("пст"), ['пст'])
        
        # Проверяем пустые строки и односимвольные слова
        self.assertEqual(split_into_syllables(""), [''])
        self.assertEqual(split_into_syllables("я"), ['я'])
    
    def test_split_word_into_syllables_alt(self):
        """
        Тест альтернативного алгоритма разделения на слоги.
        """
        # Проверяем стандартные случаи
        self.assertEqual(split_word_into_syllables_alt("молоко"), ['мо', 'ло', 'ко'])
        self.assertEqual(split_word_into_syllables_alt("книга"), ['кни', 'га'])
        
        # Результаты могут отличаться от основного алгоритма
        result = split_word_into_syllables_alt("пример")
        self.assertTrue(len(result) > 0)  # Проверяем, что результат не пустой
        
        # Проверяем слова без гласных
        self.assertEqual(split_word_into_syllables_alt("пст"), ['пст'])
        
        # Проверяем пустые строки и односимвольные слова
        self.assertEqual(split_word_into_syllables_alt(""), [''])
        self.assertEqual(split_word_into_syllables_alt("я"), ['я'])
    
    def test_get_syllables_count(self):
        """
        Тест подсчета количества слогов.
        """
        self.assertEqual(get_syllables_count("молоко"), 3)
        self.assertEqual(get_syllables_count("книга"), 2)
        self.assertEqual(get_syllables_count("стол"), 1)
        self.assertEqual(get_syllables_count(""), 1)  # Пустая строка считается как один слог
        self.assertEqual(get_syllables_count("я"), 1)
    
    def test_get_syllabification_stats(self):
        """
        Тест сбора статистики о слогах.
        """
        words = ["молоко", "книга", "стол", "яблоко", "пример"]
        stats = get_syllabification_stats(words)
        
        # Проверяем наличие ключей в статистике
        self.assertIn('average_syllables_per_word', stats)
        self.assertIn('syllables_distribution', stats)
        self.assertIn('most_common_syllables', stats)
        
        # Проверяем среднее количество слогов
        self.assertGreater(stats['average_syllables_per_word'], 1.0)
        self.assertLess(stats['average_syllables_per_word'], 3.0)
        
        # Проверяем распределение слов по количеству слогов
        syllable_distribution = stats['syllables_distribution']
        self.assertEqual(sum(syllable_distribution.values()), len(words))
        
        # Проверяем, что есть информация о самых частых слогах
        self.assertTrue(len(stats['most_common_syllables']) > 0)


if __name__ == '__main__':
    unittest.main()

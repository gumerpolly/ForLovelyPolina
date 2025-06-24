"""
Тесты для модуля морфологического анализа.
"""

import os
import sys
import unittest

# Добавляем корневой каталог проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.morpho_analyzer.morphology import MorphologicalAnalyzer


class TestMorphologicalAnalyzer(unittest.TestCase):
    """
    Набор тестов для класса морфологического анализатора.
    """
    
    def setUp(self):
        """
        Подготовка к тестам.
        """
        self.analyzer = MorphologicalAnalyzer()
    
    def test_analyze_word(self):
        """
        Тест анализа отдельного слова.
        """
        # Тестируем анализ существительного
        result = self.analyzer.analyze_word("книга")
        self.assertEqual(result['word'], "книга")
        self.assertEqual(result['lemma'], "книга")
        self.assertEqual(result['pos'], "NOUN")
        
        # Тестируем анализ глагола
        result = self.analyzer.analyze_word("читает")
        self.assertEqual(result['word'], "читает")
        self.assertEqual(result['lemma'], "читать")
        self.assertEqual(result['pos'], "VERB")
        
        # Тестируем анализ прилагательного
        result = self.analyzer.analyze_word("красивый")
        self.assertEqual(result['word'], "красивый")
        self.assertEqual(result['lemma'], "красивый")
        self.assertEqual(result['pos'], "ADJF")
    
    def test_extract_morphological_tags(self):
        """
        Тест извлечения морфологических тегов.
        """
        # Тест для существительного женского рода единственного числа в именительном падеже
        tags = self.analyzer.extract_morphological_tags("книга", "NOUN", {"gender": "femn", "number": "sing", "case": "nomn"})
        self.assertEqual(tags['pos'], "NOUN")
        self.assertEqual(tags['gender'], "femn")
        self.assertEqual(tags['number'], "sing")
        self.assertEqual(tags['case'], "nomn")
        
        # Тест для глагола настоящего времени
        tags = self.analyzer.extract_morphological_tags("читает", "VERB", {"tense": "pres", "person": "3per", "number": "sing"})
        self.assertEqual(tags['pos'], "VERB")
        self.assertEqual(tags['tense'], "pres")
        self.assertEqual(tags['person'], "3per")
        self.assertEqual(tags['number'], "sing")
    
    def test_homonym_resolution(self):
        """
        Тест для разрешения омонимии.
        """
        # Тест для слова "стекло" в контексте, где оно вероятнее всего существительное
        prev_words = ["прозрачное"]
        next_words = ["разбилось"]
        result = self.analyzer.analyze_token_with_homonym_resolution("стекло", prev_words, next_words)
        self.assertEqual(result['pos'], "NOUN")
        
        # Тест для слова "стекло" в контексте, где оно вероятнее всего глагол (от "стекать")
        prev_words = ["медленно"]
        next_words = ["по", "стене"]
        result = self.analyzer.analyze_token_with_homonym_resolution("стекло", prev_words, next_words)
        self.assertEqual(result['pos'], "VERB")
    
    def test_analyze_token(self):
        """
        Тест анализа токена с очисткой.
        """
        # Тест с токеном, содержащим знаки препинания
        result = self.analyzer.analyze_token("книга,")
        self.assertEqual(result['word'], "книга")
        self.assertEqual(result['lemma'], "книга")
        
        # Тест с токеном в верхнем регистре
        result = self.analyzer.analyze_token("КНИГА")
        self.assertEqual(result['word'], "книга")
        self.assertEqual(result['lemma'], "книга")


if __name__ == '__main__':
    unittest.main()

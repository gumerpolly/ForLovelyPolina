"""
Тесты для модуля обработки текста.
"""

import os
import sys
import unittest
import tempfile

# Добавляем корневой каталог проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.morpho_analyzer.text_processor import (
    read_text_file,
    normalize_text,
    tokenize_text,
    clean_word
)


class TestTextProcessor(unittest.TestCase):
    """
    Набор тестов для функций обработки текста.
    """
    
    def setUp(self):
        """
        Подготовка к тестам.
        """
        # Создаем временный файл для тестирования функции чтения
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.temp_file.write("Это тестовый текст. Проверка обработки текста!")
        self.temp_file.close()
    
    def tearDown(self):
        """
        Очистка после тестов.
        """
        # Удаляем временный файл
        os.unlink(self.temp_file.name)
    
    def test_read_text_file(self):
        """
        Тест чтения текстового файла.
        """
        text = read_text_file(self.temp_file.name)
        self.assertEqual(text, "Это тестовый текст. Проверка обработки текста!")
    
    def test_normalize_text(self):
        """
        Тест нормализации текста.
        """
        text = "  Это    тестовый\nтекст.\n\nПроверка   обработки  текста!  "
        normalized = normalize_text(text)
        self.assertEqual(normalized, "Это тестовый текст. Проверка обработки текста!")
    
    def test_tokenize_text_with_punctuation(self):
        """
        Тест токенизации текста с сохранением знаков препинания.
        """
        text = "Это тестовый текст. Проверка обработки текста!"
        tokens = tokenize_text(text, keep_punctuation=True)
        self.assertEqual(tokens, ['Это', 'тестовый', 'текст', '.', 'Проверка', 'обработки', 'текста', '!'])
    
    def test_tokenize_text_without_punctuation(self):
        """
        Тест токенизации текста без сохранения знаков препинания.
        """
        text = "Это тестовый текст. Проверка обработки текста!"
        tokens = tokenize_text(text, keep_punctuation=False)
        self.assertEqual(tokens, ['Это', 'тестовый', 'текст', 'Проверка', 'обработки', 'текста'])
    
    def test_clean_word(self):
        """
        Тест очистки слова от знаков препинания и приведения к нижнему регистру.
        """
        self.assertEqual(clean_word("Слово,"), "слово")
        self.assertEqual(clean_word("«Текст»"), "текст")
        self.assertEqual(clean_word("тест."), "тест")


if __name__ == '__main__':
    unittest.main()

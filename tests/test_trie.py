"""
Тесты для префиксного дерева (trie).
"""

import os
import sys
import unittest

# Добавляем корневой каталог проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.morpho_analyzer.trie import PrefixTree, TrieNode


class TestTrieNode(unittest.TestCase):
    """
    Набор тестов для класса узла префиксного дерева.
    """
    
    def test_init(self):
        """
        Тест инициализации узла.
        """
        node = TrieNode("ло")
        self.assertEqual(node.syllable, "ло")
        self.assertEqual(node.count, 0)
        self.assertFalse(node.is_end_of_word)
        self.assertEqual(node.children, {})
        self.assertEqual(node.word_data, [])
    
    def test_str_representation(self):
        """
        Тест строкового представления узла.
        """
        node = TrieNode("ло")
        self.assertIn("ло", str(node))
        
        node.is_end_of_word = True
        self.assertIn("end_of_word=True", str(node))
        
        node.count = 5
        self.assertIn("count=5", str(node))


class TestPrefixTree(unittest.TestCase):
    """
    Набор тестов для класса префиксного дерева.
    """
    
    def setUp(self):
        """
        Подготовка к тестам.
        """
        self.trie = PrefixTree()
    
    def test_init(self):
        """
        Тест инициализации дерева.
        """
        self.assertIsInstance(self.trie.root, TrieNode)
        self.assertEqual(self.trie.word_count, 0)
    
    def test_insert(self):
        """
        Тест вставки слова в дерево.
        """
        # Создаем тестовые данные
        syllables = ["мо", "ло", "ко"]
        word_data = {"word": "молоко", "lemma": "молоко", "pos": "NOUN"}
        
        # Вставляем слово
        self.trie.insert(syllables, word_data)
        
        # Проверяем, что счетчик слов увеличился
        self.assertEqual(self.trie.word_count, 1)
        
        # Проверяем, что узлы дерева созданы правильно
        node = self.trie.root
        self.assertIn("мо", node.children)
        
        node = node.children["мо"]
        self.assertEqual(node.count, 1)
        self.assertIn("ло", node.children)
        
        node = node.children["ло"]
        self.assertEqual(node.count, 1)
        self.assertIn("ко", node.children)
        
        node = node.children["ко"]
        self.assertEqual(node.count, 1)
        self.assertTrue(node.is_end_of_word)
        self.assertEqual(node.word_data, [word_data])
    
    def test_search(self):
        """
        Тест поиска слова в дереве.
        """
        # Вставляем тестовое слово
        syllables = ["мо", "ло", "ко"]
        word_data = {"word": "молоко", "lemma": "молоко", "pos": "NOUN"}
        self.trie.insert(syllables, word_data)
        
        # Проверяем поиск существующего слова
        result = self.trie.search(syllables)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], word_data)
        
        # Проверяем поиск несуществующего слова
        self.assertIsNone(self.trie.search(["ко", "ло", "мо"]))
        self.assertIsNone(self.trie.search(["мо", "ло"]))
    
    def test_starts_with_prefix(self):
        """
        Тест поиска слов по префиксу.
        """
        # Вставляем тестовые слова
        self.trie.insert(["мо", "ло", "ко"], {"word": "молоко", "pos": "NOUN"})
        self.trie.insert(["мо", "ло", "дой"], {"word": "молодой", "pos": "ADJF"})
        self.trie.insert(["мо", "ре"], {"word": "море", "pos": "NOUN"})
        
        # Проверяем поиск по префиксу "мо"
        results = self.trie.starts_with_prefix(["мо"])
        self.assertEqual(len(results), 3)  # Должны найтись все 3 слова
        
        # Проверяем поиск по префиксу "мо", "ло"
        results = self.trie.starts_with_prefix(["мо", "ло"])
        self.assertEqual(len(results), 2)  # Должны найтись 2 слова
        
        # Проверяем поиск по несуществующему префиксу
        results = self.trie.starts_with_prefix(["не"])
        self.assertEqual(len(results), 0)
    
    def test_get_all_words(self):
        """
        Тест получения всех слов из дерева.
        """
        # Вставляем тестовые слова
        self.trie.insert(["мо", "ло", "ко"], {"word": "молоко", "pos": "NOUN"})
        self.trie.insert(["мо", "ло", "дой"], {"word": "молодой", "pos": "ADJF"})
        self.trie.insert(["мо", "ре"], {"word": "море", "pos": "NOUN"})
        
        # Получаем все слова
        words = self.trie.get_all_words()
        
        # Проверяем результаты
        self.assertEqual(len(words), 3)
        
        # Создаем множество слов для проверки
        found_words = set()
        for syllables, word_data_list in words:
            for word_data in word_data_list:
                found_words.add(word_data["word"])
        
        # Проверяем, что все слова найдены
        self.assertSetEqual(found_words, {"молоко", "молодой", "море"})
    
    def test_get_statistics(self):
        """
        Тест получения статистики дерева.
        """
        # Вставляем тестовые слова
        self.trie.insert(["мо", "ло", "ко"], {"word": "молоко"})
        self.trie.insert(["мо", "ло", "дой"], {"word": "молодой"})
        self.trie.insert(["мо", "ре"], {"word": "море"})
        
        # Получаем статистику
        stats = self.trie.get_statistics()
        
        # Проверяем наличие ключей в статистике
        self.assertIn('word_count', stats)
        self.assertIn('node_count', stats)
        self.assertIn('max_depth', stats)
        self.assertIn('level_distribution', stats)
        self.assertIn('avg_branching', stats)
        self.assertIn('most_common_syllables', stats)
        
        # Проверяем значения статистики
        self.assertEqual(stats['word_count'], 3)
        self.assertEqual(stats['max_depth'], 3)  # максимальная глубина 3 для молоко и молодой
    
    def test_serialize_deserialize(self):
        """
        Тест сериализации и десериализации дерева.
        """
        # Вставляем тестовые слова
        self.trie.insert(["мо", "ло", "ко"], {"word": "молоко", "pos": "NOUN"})
        self.trie.insert(["мо", "ло", "дой"], {"word": "молодой", "pos": "ADJF"})
        
        # Сериализуем дерево
        serialized = self.trie.serialize()
        
        # Десериализуем дерево
        new_trie = PrefixTree.deserialize(serialized)
        
        # Проверяем, что свойства дерева сохранились
        self.assertEqual(new_trie.word_count, self.trie.word_count)
        
        # Проверяем, что слова можно найти в новом дереве
        self.assertIsNotNone(new_trie.search(["мо", "ло", "ко"]))
        self.assertIsNotNone(new_trie.search(["мо", "ло", "дой"]))


if __name__ == '__main__':
    unittest.main()

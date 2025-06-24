"""
Модуль для реализации префиксного дерева.

Этот модуль предоставляет классы и функции для создания и использования
префиксного дерева (trie) с использованием слогов в качестве ключей.
"""

from typing import Dict, List, Any, Optional, Tuple, Set


class TrieNode:
    """
    Класс, представляющий узел префиксного дерева.
    
    Attributes:
        children: Словарь дочерних узлов, где ключ - слог, значение - узел
        is_end_of_word: Флаг, указывающий, является ли узел концом слова
        word_data: Данные, сохраненные для слова, если узел является концом слова
        syllable: Слог, соответствующий данному узлу
        count: Счетчик вхождений данного узла
    """
    
    def __init__(self, syllable: str = ""):
        """
        Инициализирует узел префиксного дерева.
        
        Args:
            syllable: Слог, соответствующий данному узлу (по умолчанию пустая строка для корня)
        """
        self.children: Dict[str, TrieNode] = {}
        self.is_end_of_word: bool = False
        self.word_data: List[Dict[str, Any]] = []
        self.syllable: str = syllable
        self.count: int = 0
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление узла.
        
        Returns:
            Строковое представление узла
        """
        if self.is_end_of_word:
            return f"TrieNode('{self.syllable}', end_of_word=True, count={self.count})"
        return f"TrieNode('{self.syllable}', count={self.count})"
    
    def __repr__(self) -> str:
        """
        Возвращает строковое представление узла для отладки.
        
        Returns:
            Строковое представление узла
        """
        return self.__str__()


class PrefixTree:
    """
    Класс, реализующий префиксное дерево для хранения информации о словах.
    
    Attributes:
        root: Корневой узел дерева
        word_count: Количество слов в дереве
    """
    
    def __init__(self):
        """
        Инициализирует префиксное дерево.
        """
        self.root = TrieNode()
        self.word_count = 0
    
    def insert(self, syllables: List[str], word_data: Dict[str, Any]) -> None:
        """
        Вставляет слово в префиксное дерево.
        
        Args:
            syllables: Список слогов слова
            word_data: Данные о слове (результат морфологического анализа)
        """
        node = self.root
        
        for syllable in syllables:
            if syllable not in node.children:
                node.children[syllable] = TrieNode(syllable)
            
            node = node.children[syllable]
            node.count += 1
        
        node.is_end_of_word = True
        node.word_data.append(word_data)
        self.word_count += 1
    
    def search(self, syllables: List[str]) -> Optional[List[Dict[str, Any]]]:
        """
        Ищет слово в префиксном дереве.
        
        Args:
            syllables: Список слогов слова
            
        Returns:
            Данные о слове, если слово найдено, иначе None
        """
        node = self.root
        
        for syllable in syllables:
            if syllable not in node.children:
                return None
            
            node = node.children[syllable]
        
        if node.is_end_of_word:
            return node.word_data
        
        return None
    
    def starts_with_prefix(self, prefix_syllables: List[str]) -> List[Tuple[List[str], List[Dict[str, Any]]]]:
        """
        Находит все слова, начинающиеся с заданного префикса.
        
        Args:
            prefix_syllables: Список слогов префикса
            
        Returns:
            Список пар (слоги слова, данные о слове) для всех слов, 
            начинающихся с заданного префикса
        """
        result = []
        node = self.root
        
        # Доходим до узла, соответствующего префиксу
        for syllable in prefix_syllables:
            if syllable not in node.children:
                return []
            
            node = node.children[syllable]
        
        # Находим все слова, начинающиеся с данного префикса
        self._collect_words_from_node(node, prefix_syllables, result)
        
        return result
    
    def _collect_words_from_node(self, node: TrieNode, 
                                current_syllables: List[str], 
                                result: List[Tuple[List[str], List[Dict[str, Any]]]]) -> None:
        """
        Рекурсивно собирает все слова, начиная с заданного узла.
        
        Args:
            node: Текущий узел
            current_syllables: Список слогов от корня до текущего узла
            result: Список для сохранения результатов
        """
        if node.is_end_of_word:
            result.append((current_syllables.copy(), node.word_data))
        
        for syllable, child_node in node.children.items():
            current_syllables.append(syllable)
            self._collect_words_from_node(child_node, current_syllables, result)
            current_syllables.pop()  # Возвращаем список к исходному состоянию после рекурсии
    
    def get_all_words(self) -> List[Tuple[List[str], List[Dict[str, Any]]]]:
        """
        Возвращает все слова в дереве.
        
        Returns:
            Список пар (слоги слова, данные о слове) для всех слов в дереве
        """
        result = []
        self._collect_words_from_node(self.root, [], result)
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику о дереве.
        
        Returns:
            Словарь со статистикой:
            - количество слов
            - количество узлов
            - глубина дерева
            - средняя разветвленность
            - наиболее частые слоги
        """
        # Словарь для хранения всех узлов и их уровней
        node_levels: Dict[TrieNode, int] = {}
        # Множество всех узлов
        all_nodes: Set[TrieNode] = set()
        # Словарь для подсчета частоты слогов
        syllable_frequency: Dict[str, int] = {}
        
        # Рекурсивно обходим дерево и собираем информацию
        self._collect_node_info(self.root, 0, node_levels, all_nodes, syllable_frequency)
        
        # Максимальный уровень (глубина дерева)
        max_level = max(node_levels.values()) if node_levels else 0
        
        # Распределение узлов по уровням
        level_distribution: Dict[int, int] = {}
        for level in node_levels.values():
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # Средняя разветвленность (среднее число дочерних узлов у не конечных узлов)
        non_leaf_nodes = [node for node in all_nodes if node.children]
        avg_branching = sum(len(node.children) for node in non_leaf_nodes) / len(non_leaf_nodes) if non_leaf_nodes else 0
        
        # Наиболее частые слоги
        most_common_syllables = sorted(syllable_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'word_count': self.word_count,
            'node_count': len(all_nodes),
            'max_depth': max_level,
            'level_distribution': level_distribution,
            'avg_branching': avg_branching,
            'most_common_syllables': most_common_syllables[:20]  # Топ-20 самых частых слогов
        }
    
    def _collect_node_info(self, node: TrieNode, level: int, 
                          node_levels: Dict[TrieNode, int], 
                          all_nodes: Set[TrieNode], 
                          syllable_frequency: Dict[str, int]) -> None:
        """
        Рекурсивно обходит дерево и собирает информацию о узлах.
        
        Args:
            node: Текущий узел
            level: Уровень узла в дереве (глубина)
            node_levels: Словарь для сохранения уровней узлов
            all_nodes: Множество для сохранения всех узлов
            syllable_frequency: Словарь для подсчета частоты слогов
        """
        # Добавляем узел в множество всех узлов
        all_nodes.add(node)
        
        # Сохраняем уровень узла
        node_levels[node] = level
        
        # Увеличиваем счетчик для слога
        if node.syllable:
            syllable_frequency[node.syllable] = syllable_frequency.get(node.syllable, 0) + node.count
        
        # Рекурсивно обходим дочерние узлы
        for child_node in node.children.values():
            self._collect_node_info(child_node, level + 1, node_levels, all_nodes, syllable_frequency)
    
    def serialize(self) -> Dict[str, Any]:
        """
        Сериализует дерево в словарь.
        
        Returns:
            Словарь, представляющий дерево
        """
        return {
            'word_count': self.word_count,
            'root': self._serialize_node(self.root)
        }
    
    def _serialize_node(self, node: TrieNode) -> Dict[str, Any]:
        """
        Рекурсивно сериализует узел и его дочерние узлы.
        
        Args:
            node: Узел для сериализации
            
        Returns:
            Словарь, представляющий узел
        """
        result = {
            'syllable': node.syllable,
            'is_end_of_word': node.is_end_of_word,
            'count': node.count,
            'children': {}
        }
        
        if node.is_end_of_word:
            result['word_data'] = node.word_data
            
        for syllable, child_node in node.children.items():
            result['children'][syllable] = self._serialize_node(child_node)
            
        return result
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'PrefixTree':
        """
        Создает дерево из сериализованного словаря.
        
        Args:
            data: Словарь, представляющий сериализованное дерево
            
        Returns:
            Экземпляр префиксного дерева
        """
        tree = cls()
        tree.word_count = data['word_count']
        
        # Рекурсивно восстанавливаем узлы
        tree._deserialize_node(tree.root, data['root'])
        
        return tree
    
    def _deserialize_node(self, node: TrieNode, data: Dict[str, Any]) -> None:
        """
        Рекурсивно восстанавливает узел и его дочерние узлы из словаря.
        
        Args:
            node: Узел для заполнения
            data: Словарь с данными узла
        """
        node.syllable = data['syllable']
        node.is_end_of_word = data['is_end_of_word']
        node.count = data['count']
        
        if node.is_end_of_word and 'word_data' in data:
            node.word_data = data['word_data']
            
        for syllable, child_data in data['children'].items():
            node.children[syllable] = TrieNode()
            self._deserialize_node(node.children[syllable], child_data)

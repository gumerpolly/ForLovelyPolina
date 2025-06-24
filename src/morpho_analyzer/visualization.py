"""
Модуль для визуализации результатов морфологического анализа и префиксного дерева.

Этот модуль предоставляет функции для создания различных визуализаций:
- графическое представление префиксного дерева
- статистика морфологического анализа
- распределение частей речи
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.figure import Figure
from typing import Dict, List, Any, Tuple, Optional
import os
import numpy as np
from collections import Counter
import pandas as pd

from .trie import PrefixTree, TrieNode


def visualize_trie(trie: PrefixTree, max_depth: int = 5, 
                  output_path: Optional[str] = None,
                  title: str = "Префиксное дерево") -> Figure:
    """
    Создает визуализацию префиксного дерева.
    
    Args:
        trie: Префиксное дерево для визуализации
        max_depth: Максимальная глубина отображаемого дерева
        output_path: Путь для сохранения изображения (если None, изображение не сохраняется)
        title: Заголовок графика
        
    Returns:
        Объект Figure с визуализацией
    """
    # Создаем направленный граф
    G = nx.DiGraph()
    
    # Добавляем корневой узел
    G.add_node("ROOT", label="ROOT", syllable="", count=0)
    
    # Рекурсивно добавляем узлы и ребра
    _add_nodes_and_edges(G, "ROOT", trie.root, 1, max_depth)
    
    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Определяем позиции узлов с помощью алгоритма компоновки дерева
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog="dot")
    
    # Получаем метки и счетчики для узлов
    labels = {}
    counts = {}
    
    for node, data in G.nodes(data=True):
        if node == "ROOT":
            labels[node] = "ROOT"
        else:
            labels[node] = data.get('syllable', '')
        counts[node] = data.get('count', 0)
    
    # Нормализуем размеры узлов в зависимости от их счетчика
    node_sizes = [max(500, min(2000, 500 + 100 * counts[node])) for node in G.nodes()]
    
    # Рисуем граф
    nx.draw(G, pos, with_labels=True, labels=labels, 
            node_color='skyblue', node_size=node_sizes, 
            font_size=10, font_weight='bold', 
            arrows=True, ax=ax)
    
    # Добавляем заголовок
    plt.title(title, fontsize=15)
    
    # Сохраняем изображение, если указан путь
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
    
    return fig


def _add_nodes_and_edges(G: nx.DiGraph, parent_id: str, node: TrieNode, 
                        current_depth: int, max_depth: int) -> None:
    """
    Рекурсивно добавляет узлы и ребра в граф NetworkX.
    
    Args:
        G: Граф NetworkX
        parent_id: Идентификатор родительского узла
        node: Текущий узел Trie
        current_depth: Текущая глубина в дереве
        max_depth: Максимальная глубина для визуализации
    """
    # Если превышена максимальная глубина, останавливаемся
    if current_depth > max_depth:
        return
    
    # Добавляем дочерние узлы и ребра
    for syllable, child_node in node.children.items():
        # Создаем уникальный идентификатор для узла
        node_id = f"{parent_id}_{syllable}"
        
        # Добавляем узел с его атрибутами
        G.add_node(node_id, syllable=syllable, label=syllable, 
                  count=child_node.count, is_end=child_node.is_end_of_word)
        
        # Добавляем ребро от родительского узла к текущему
        G.add_edge(parent_id, node_id)
        
        # Рекурсивно добавляем дочерние узлы
        _add_nodes_and_edges(G, node_id, child_node, current_depth + 1, max_depth)


def visualize_parts_of_speech(analyzed_text: List[Dict[str, Any]], 
                             output_path: Optional[str] = None,
                             title: str = "Распределение частей речи") -> Figure:
    """
    Создает график распределения частей речи в тексте.
    
    Args:
        analyzed_text: Список результатов морфологического анализа
        output_path: Путь для сохранения изображения (если None, изображение не сохраняется)
        title: Заголовок графика
        
    Returns:
        Объект Figure с визуализацией
    """
    # Подсчитываем частоты частей речи
    pos_counter = Counter()
    
    for word_info in analyzed_text:
        pos = word_info.get('pos')
        if pos:  # Пропускаем None и пустые строки
            pos_counter[pos] += 1
    
    # Получаем наиболее частые части речи
    labels = []
    counts = []
    
    for pos, count in pos_counter.most_common():
        # Добавляем названия частей речи и соответствующие счетчики
        labels.append(_get_pos_name(pos))
        counts.append(count)
    
    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Создаем горизонтальный столбчатый график
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, counts, align='center', color='skyblue')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    
    # Добавляем значения на график
    for i, v in enumerate(counts):
        ax.text(v + 0.1, i, str(v), color='black', va='center')
    
    # Настраиваем оси
    ax.invert_yaxis()  # Первый элемент сверху
    ax.set_xlabel('Количество')
    ax.set_title(title)
    
    # Улучшаем компоновку
    plt.tight_layout()
    
    # Сохраняем изображение, если указан путь
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
    
    return fig


def _get_pos_name(pos_tag: str) -> str:
    """
    Преобразует тег части речи в удобочитаемое название.
    
    Args:
        pos_tag: Тег части речи от pymorphy2
        
    Returns:
        Удобочитаемое название части речи
    """
    pos_dict = {
        'NOUN': 'Существительное',
        'ADJF': 'Прилагательное (полное)',
        'ADJS': 'Прилагательное (краткое)',
        'VERB': 'Глагол',
        'INFN': 'Глагол (инфинитив)',
        'PRTF': 'Причастие (полное)',
        'PRTS': 'Причастие (краткое)',
        'GRND': 'Деепричастие',
        'NUMR': 'Числительное',
        'ADVB': 'Наречие',
        'NPRO': 'Местоимение',
        'PREP': 'Предлог',
        'CONJ': 'Союз',
        'PRCL': 'Частица',
        'INTJ': 'Междометие'
    }
    
    return pos_dict.get(pos_tag, pos_tag)


def visualize_syllable_statistics(syllable_stats: Dict[str, Any],
                                output_path: Optional[str] = None,
                                title: str = "Статистика слогов") -> Figure:
    """
    Создает визуализацию статистики по слогам.
    
    Args:
        syllable_stats: Словарь со статистикой слогов
        output_path: Путь для сохранения изображения
        title: Заголовок графика
        
    Returns:
        Объект Figure с визуализацией
    """
    # Создаем подграфики
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    
    # График 1: Распределение слов по количеству слогов
    distribution = syllable_stats['syllables_distribution']
    
    syllable_counts = sorted(distribution.keys())
    word_counts = [distribution[count] for count in syllable_counts]
    
    axs[0].bar(syllable_counts, word_counts, color='skyblue')
    axs[0].set_xlabel('Количество слогов в слове')
    axs[0].set_ylabel('Количество слов')
    axs[0].set_xticks(syllable_counts)
    axs[0].set_title('Распределение слов по количеству слогов')
    
    # График 2: Наиболее частые слоги
    most_common = syllable_stats['most_common_syllables'][:15]  # Берем только топ-15
    
    syllables = [item[0] for item in most_common]
    frequencies = [item[1] for item in most_common]
    
    # Сортируем по частоте
    sorted_indices = np.argsort(frequencies)[::-1]
    syllables = [syllables[i] for i in sorted_indices]
    frequencies = [frequencies[i] for i in sorted_indices]
    
    axs[1].barh(range(len(syllables)), frequencies, color='skyblue')
    axs[1].set_yticks(range(len(syllables)))
    axs[1].set_yticklabels(syllables)
    axs[1].invert_yaxis()  # Первый элемент сверху
    axs[1].set_xlabel('Частота')
    axs[1].set_title('Наиболее частые слоги')
    
    # Добавляем общий заголовок
    fig.suptitle(title, fontsize=16)
    
    # Улучшаем компоновку
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Сохраняем изображение, если указан путь
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
    
    return fig


def visualize_trie_statistics(trie_stats: Dict[str, Any], 
                            output_path: Optional[str] = None,
                            title: str = "Статистика префиксного дерева") -> Figure:
    """
    Создает визуализацию статистики по префиксному дереву.
    
    Args:
        trie_stats: Словарь со статистикой префиксного дерева
        output_path: Путь для сохранения изображения
        title: Заголовок графика
        
    Returns:
        Объект Figure с визуализацией
    """
    # Создаем подграфики
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    
    # График 1: Распределение узлов по уровням
    level_dist = trie_stats['level_distribution']
    
    levels = sorted(level_dist.keys())
    node_counts = [level_dist[level] for level in levels]
    
    axs[0].bar(levels, node_counts, color='skyblue')
    axs[0].set_xlabel('Уровень в дереве')
    axs[0].set_ylabel('Количество узлов')
    axs[0].set_xticks(levels)
    axs[0].set_title(f'Распределение узлов по уровням (всего узлов: {trie_stats["node_count"]})')
    
    # График 2: Наиболее частые слоги в дереве
    most_common = trie_stats['most_common_syllables'][:15]  # Берем только топ-15
    
    syllables = [item[0] for item in most_common]
    frequencies = [item[1] for item in most_common]
    
    # Сортируем по частоте
    sorted_indices = np.argsort(frequencies)[::-1]
    syllables = [syllables[i] for i in sorted_indices]
    frequencies = [frequencies[i] for i in sorted_indices]
    
    axs[1].barh(range(len(syllables)), frequencies, color='skyblue')
    axs[1].set_yticks(range(len(syllables)))
    axs[1].set_yticklabels(syllables)
    axs[1].invert_yaxis()  # Первый элемент сверху
    axs[1].set_xlabel('Частота')
    axs[1].set_title('Наиболее частые слоги в дереве')
    
    # Добавляем общий заголовок
    fig.suptitle(f"{title} (слов: {trie_stats['word_count']}, макс. глубина: {trie_stats['max_depth']})", 
                fontsize=16)
    
    # Улучшаем компоновку
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Сохраняем изображение, если указан путь
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
    
    return fig


def create_summary_report(analyzed_text: List[Dict[str, Any]], 
                         trie: PrefixTree,
                         syllable_stats: Dict[str, Any],
                         output_path: Optional[str] = None) -> str:
    """
    Создает текстовый отчет с сводной статистикой анализа.
    
    Args:
        analyzed_text: Список результатов морфологического анализа
        trie: Префиксное дерево
        syllable_stats: Статистика по слогам
        output_path: Путь для сохранения отчета (если None, отчет не сохраняется)
        
    Returns:
        Текст отчета
    """
    trie_stats = trie.get_statistics()
    
    # Подсчитываем частоты частей речи
    pos_counter = Counter()
    
    for word_info in analyzed_text:
        pos = word_info.get('pos')
        if pos:  # Пропускаем None и пустые строки
            pos_counter[pos] += 1
    
    # Формируем отчет
    report = []
    report.append("# Отчет о морфологическом анализе текста")
    report.append("\n## 1. Общая статистика\n")
    report.append(f"- Всего слов: {len(analyzed_text)}")
    report.append(f"- Уникальных слов в дереве: {trie_stats['word_count']}")
    report.append(f"- Средняя длина слова в слогах: {syllable_stats['average_syllables_per_word']:.2f}")
    report.append(f"- Всего узлов в префиксном дереве: {trie_stats['node_count']}")
    report.append(f"- Максимальная глубина дерева: {trie_stats['max_depth']}")
    report.append(f"- Средняя разветвленность: {trie_stats['avg_branching']:.2f}")
    
    report.append("\n## 2. Распределение частей речи\n")
    for pos, count in pos_counter.most_common():
        report.append(f"- {_get_pos_name(pos)}: {count} слов ({count/len(analyzed_text)*100:.1f}%)")
    
    report.append("\n## 3. Распределение слов по количеству слогов\n")
    for count in sorted(syllable_stats['syllables_distribution'].keys()):
        words_count = syllable_stats['syllables_distribution'][count]
        report.append(f"- {count} слогов: {words_count} слов")
    
    report.append("\n## 4. Наиболее частые слоги\n")
    for syllable, freq in syllable_stats['most_common_syllables'][:10]:
        report.append(f"- '{syllable}': {freq} раз")
    
    # Соединяем все строки отчета
    report_text = "\n".join(report)
    
    # Сохраняем отчет, если указан путь
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
    
    return report_text

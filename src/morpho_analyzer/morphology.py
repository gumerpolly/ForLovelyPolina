"""
Модуль для морфологического анализа текста.

Этот модуль предоставляет класс MorphologicalAnalyzer для определения морфологических
характеристик слов в тексте и снятия омонимии на основе контекста.
"""

# Импорт патча для совместимости с Python 3.11+
from . import pymorphy2_patch
# Импорт pymorphy2
import pymorphy2
from typing import Any, Dict, List, Optional, Tuple, Union
import os
import re
import json
from pathlib import Path


class MorphologicalAnalyzer:
    """
    Класс для выполнения морфологического анализа текста.
    """
    
    def __init__(self, language: str = 'ru', homonyms_file: str = None):
        """
        Инициализирует анализатор.
        
        Args:
            language: Код языка (по умолчанию 'ru' - русский)
            homonyms_file: Путь к JSON-файлу со словарем омонимов
        """
        self.language = language
        # Инициализируем морфологический анализатор
        self.analyzer = pymorphy2.MorphAnalyzer()
        
        # Загрузка словаря омонимов из JSON-файла
        if homonyms_file is None:
            # Используем путь по умолчанию относительно текущего модуля
            module_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            homonyms_file = module_dir / 'data' / 'homonyms.json'
        
        self.homonyms_dict = self._load_homonyms(homonyms_file)
        
    def analyze_word(self, word: str) -> Dict[str, Any]:
        """
        Выполняет морфологический анализ слова с помощью pymorphy2.
        
        Args:
            word: Слово для анализа
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Очищаем слово от знаков препинания и приводим к нижнему регистру
        clean_word = self._clean_word(word)
        
        # Если слово пустое после очистки, возвращаем заглушку
        if not clean_word:
            return {
                'word': word,
                'lemma': word,
                'pos': 'PUNCT',
                'tags': {}
            }
        
        # Получаем морфологический разбор с помощью pymorphy2
        parsed = self.analyzer.parse(clean_word)
        
        # Если есть результаты анализа, берем первый (наиболее вероятный)
        if parsed:
            parse = parsed[0]
            
            # Извлекаем морфологические теги
            tags = self._extract_tags(parse.tag)
            
            # Формируем результат без сохранения объектов pymorphy2
            result = {
                'word': word,
                'lemma': parse.normal_form,
                'pos': parse.tag.POS or 'UNKNOWN',
                'tags': tags
                # Не сохраняем все варианты разбора, чтобы избежать проблем сериализации
            }
            
            return result
        
        # Если анализ не удался, возвращаем заглушку
        return {
            'word': word,
            'lemma': clean_word,
            'pos': 'UNKNOWN',
            'tags': {}
        }
    
    def _clean_word(self, word: str) -> str:
        """
        Очищает слово от знаков препинания и приводит к нижнему регистру.
        
        Args:
            word: Исходное слово
            
        Returns:
            Очищенное слово
        """
        # Удаление знаков препинания и приведение к нижнему регистру
        return re.sub(r'[^а-яё]', '', word.lower())
    
    def _load_homonyms(self, homonyms_file: Union[str, Path]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Загружает словарь омонимов из JSON-файла.
        
        Args:
            homonyms_file: Путь к JSON-файлу со словарем омонимов
            
        Returns:
            Словарь омонимов
        """
        try:
            with open(homonyms_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки словаря омонимов: {e}")
            # Возвращаем пустой словарь в случае ошибки
            return {}
    
    def _extract_tags(self, tag: Any) -> Dict[str, str]:
        """
        Извлекает морфологические теги из тега pymorphy2.
        
        Args:
            tag: Тег pymorphy2
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Извлекаем все доступные грамматические категории
        tags = {}
        
        # Получаем значения основных морфологических категорий
        if hasattr(tag, 'gender'):
            tags['gender'] = tag.gender
        
        if hasattr(tag, 'number'):
            tags['number'] = tag.number
            
        if hasattr(tag, 'case'):
            tags['case'] = tag.case
            
        if hasattr(tag, 'tense'):
            tags['tense'] = tag.tense
            
        if hasattr(tag, 'person'):
            tags['person'] = tag.person
            
        if hasattr(tag, 'aspect'):
            tags['aspect'] = tag.aspect
            
        if hasattr(tag, 'mood'):
            tags['mood'] = tag.mood
            
        if hasattr(tag, 'voice'):
            tags['voice'] = tag.voice
            
        if hasattr(tag, 'animacy'):
            tags['animacy'] = tag.animacy
            
        return tags
    
    def extract_morphological_tags(self, word: str, pos: str, tags: Dict[str, str]) -> Dict[str, str]:
        """
        Извлекает морфологические теги на основе слова и его части речи.
        
        Args:
            word: Слово для анализа
            pos: Часть речи
            tags: Морфологические теги
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Заглушка - просто возвращаем те же теги с добавлением информации о части речи
        result = {'pos': pos}
        result.update(tags)
        return result
    
    def analyze_token_with_homonym_resolution(self, word: str, prev_words: List[str] = None, next_words: List[str] = None) -> Dict[str, Any]:
        """
        Анализирует слово с учетом контекста для разрешения омонимии.
        
        Args:
            word: Слово для анализа
            prev_words: Предыдущие слова в контексте
            next_words: Следующие слова в контексте
            
        Returns:
            Словарь с морфологическими характеристиками с учетом контекста
        """
        # Создаем общий контекст из предыдущих и следующих слов
        context = []
        if prev_words:
            context.extend(prev_words)
        if next_words:
            context.extend(next_words)
        
        # Используем общий механизм снятия омонимии
        return self.resolve_homonymy(word, context)
    
    def analyze_token(self, token: str) -> Dict[str, Any]:
        """
        Анализирует токен, который может включать знак препинания.
        
        Args:
            token: Строка с токеном (может содержать знаки препинания)
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Извлекаем слово из токена, удаляя знаки препинания
        word = re.sub(r'[^\w\s\-]', '', token)
        
        # Получаем знак препинания, если он есть
        punctuation = ''.join(re.findall(r'[^\w\s\-]', token))
        
        # Анализируем слово
        analysis = self.analyze_word(word)
        
        # Добавляем информацию о знаке препинания, если он есть
        if punctuation:
            analysis['punctuation'] = punctuation
        
        return analysis
    def resolve_homonymy(self, word: str, context: List[str] = None) -> Dict[str, Any]:
        """
        Разрешает омонимию на основе контекста.
        
        Args:
            word: Слово для анализа
            context: Контекст слова (окружающие слова)
            
        Returns:
            Словарь с морфологическими характеристиками наиболее вероятного варианта
        """
        # Очищаем слово от знаков препинания и приводим к нижнему регистру
        clean_word = self._clean_word(word)
        # Проверяем наличие слова в словаре омонимов
        if clean_word in self.homonyms_dict:
            parses = self.homonyms_dict[clean_word]
            
            # Детальный анализ контекста
            if context and len(context) > 0:
                context_lower = [self._clean_word(w) for w in context]
                print(f"DEBUG: Анализируем слово '{clean_word}' в контексте {context_lower}")
                
                # Вычисляем релевантность каждого варианта разбора
                match_scores = []
                
                for i, parse in enumerate(parses):
                    score = 0
                    markers = parse.get('markers', [])
                    # Подсчитываем количество совпадающих маркеров
                    matching_markers = [marker for marker in markers if marker in context_lower]
                    score = len(matching_markers)
                    
                    sense = parse['tags'].get('sense', '')
                    match_scores.append((i, score, matching_markers, sense))
                    print(f"DEBUG: Вариант {i}: значение='{sense}', совпадений={score}, маркеры={matching_markers}")
                
                # Выбираем вариант с наибольшим количеством совпадений
                match_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Если есть хотя бы одно совпадение, используем этот вариант
                if match_scores and match_scores[0][1] > 0:
                    best_match = match_scores[0]
                    best_parse = parses[best_match[0]]
                    print(f"DEBUG: Выбран вариант {best_match[0]} с {best_match[1]} совпадениями")
                    
                    # Получаем значение омонима из тегов
                    sense = best_parse['tags'].get('sense', '')
                    
                    return {
                        'word': word,
                        'lemma': best_parse['lemma'],
                        'pos': best_parse['pos'],
                        'tags': best_parse['tags'].copy(),
                        'sense': sense,  # Добавляем значение омонима на верхний уровень
                        'all_parses': []
                    }
            
            # Если контекст не помог или его нет, вернем первый (наиболее вероятный) разбор
            if parses:
                default_parse = parses[0]
                print(f"DEBUG: Используем вариант по умолчанию для '{clean_word}'")
                # Получаем значение омонима из тегов
                sense = default_parse['tags'].get('sense', '')
                return {
                    'word': word,
                    'lemma': default_parse['lemma'],
                    'pos': default_parse['pos'],
                    'tags': default_parse['tags'].copy(),
                    'sense': sense,  # Добавляем значение омонима на верхний уровень
                    'all_parses': []
                }
        
        # По умолчанию просто анализируем слово без учета контекста
        return self.analyze_word(word)
    
    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Анализирует весь текст.
        
        Args:
            text: Текст для анализа
            
        Returns:
            Список словарей с морфологическими характеристиками слов
        """
        # Разбиваем текст на предложения
        sentences = re.split(r'[.!?]+', text)
        result = []
        
        # Обрабатываем каждое предложение
        for sentence in sentences:
            # Извлекаем слова из предложения
            words = re.findall(r'[а-яёА-ЯЁ]+', sentence.lower())
            
            if not words:
                continue
                
            # Анализируем каждое слово с учетом контекста предложения
            for i, word in enumerate(words):
                # Используем контекст предложения для снятия омонимии
                # (передаем все слова предложения в качестве контекста)
                analysis = self.resolve_homonymy(word, words)
                
                # Добавляем позицию слова в предложении
                analysis['position'] = i
                analysis['sentence'] = sentence.strip()
                
                result.append(analysis)
        return result

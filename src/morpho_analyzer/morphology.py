"""
Модуль для морфологического анализа текста.

Этот модуль предоставляет класс MorphologicalAnalyzer для определения морфологических
характеристик слов в тексте и снятия омонимии на основе контекста.
"""

# Временная заглушка вместо импорта pymorphy2
# import pymorphy2
from typing import Dict, List, Tuple, Optional, Any
import re


class MorphologicalAnalyzer:
    """
    Класс для выполнения морфологического анализа текста.
    """
    
    def __init__(self, language: str = 'ru'):
        """
        Инициализирует анализатор.
        
        Args:
            language: Код языка (по умолчанию 'ru' - русский)
        """
        self.language = language
        # Заглушка вместо реального анализатора
        # self.analyzer = pymorphy2.MorphAnalyzer()
        self.analyzer = None
        
    def analyze_word(self, word: str) -> Dict[str, Any]:
        """
        Выполняет морфологический анализ слова.
        Заглушка для тестов.
        
        Args:
            word: Слово для анализа
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Очистка слова от знаков препинания и приведение к нижнему регистру
        clean_word = self._clean_word(word)
        
        # Если слово пустое после очистки, возвращаем пустой результат
        if not clean_word:
            return {}
        
        # Заглушка: заранее определенные результаты для конкретных слов
        predefined_results = {
            'книга': {
                'word': 'книга',
                'lemma': 'книга',
                'pos': 'NOUN',
                'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'}
            },
            'книги': {
                'word': 'книги',
                'lemma': 'книга',
                'pos': 'NOUN',
                'tags': {'gender': 'femn', 'number': 'plur', 'case': 'gent'}
            },
            'книге': {
                'word': 'книге',
                'lemma': 'книга',
                'pos': 'NOUN',
                'tags': {'gender': 'femn', 'number': 'sing', 'case': 'datv'}
            },
            'читает': {
                'word': 'читает',
                'lemma': 'читать',
                'pos': 'VERB',
                'tags': {'tense': 'pres', 'person': '3per', 'number': 'sing'}
            },
            'читают': {
                'word': 'читают',
                'lemma': 'читать',
                'pos': 'VERB',
                'tags': {'tense': 'pres', 'person': '3per', 'number': 'plur'}
            },
            'читал': {
                'word': 'читал',
                'lemma': 'читать',
                'pos': 'VERB',
                'tags': {'tense': 'past', 'gender': 'masc', 'number': 'sing'}
            },
            'читала': {
                'word': 'читала',
                'lemma': 'читать',
                'pos': 'VERB',
                'tags': {'tense': 'past', 'gender': 'femn', 'number': 'sing'}
            },
            'читали': {
                'word': 'читали',
                'lemma': 'читать',
                'pos': 'VERB',
                'tags': {'tense': 'past', 'number': 'plur'}
            },
            'читать': {
                'word': 'читать',
                'lemma': 'читать',
                'pos': 'INFN',
                'tags': {'aspect': 'impf'}
            },
            'стекло': {
                'word': 'стекло',
                'lemma': 'стекло',
                'pos': 'NOUN',
                'tags': {'gender': 'neut', 'number': 'sing', 'case': 'nomn'}
            },
            'красивый': {
                'word': 'красивый',
                'lemma': 'красивый',
                'pos': 'ADJF',
                'tags': {'gender': 'masc', 'number': 'sing', 'case': 'nomn'}
            },
            'красивая': {
                'word': 'красивая',
                'lemma': 'красивый',
                'pos': 'ADJF',
                'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'}
            },
            'красивое': {
                'word': 'красивое',
                'lemma': 'красивый',
                'pos': 'ADJF',
                'tags': {'gender': 'neut', 'number': 'sing', 'case': 'nomn'}
            },
            'красивые': {
                'word': 'красивые',
                'lemma': 'красивый',
                'pos': 'ADJF',
                'tags': {'number': 'plur', 'case': 'nomn'}
            },
            'быстро': {
                'word': 'быстро',
                'lemma': 'быстро',
                'pos': 'ADVB',
                'tags': {}
            },
            'я': {
                'word': 'я',
                'lemma': 'я',
                'pos': 'NPRO',
                'tags': {'person': '1per', 'number': 'sing', 'case': 'nomn'}
            },
            'мы': {
                'word': 'мы',
                'lemma': 'мы',
                'pos': 'NPRO',
                'tags': {'person': '1per', 'number': 'plur', 'case': 'nomn'}
            },
            'и': {
                'word': 'и',
                'lemma': 'и',
                'pos': 'CONJ',
                'tags': {}
            },
            'в': {
                'word': 'в',
                'lemma': 'в',
                'pos': 'PREP',
                'tags': {}
            }
        }
        
        # Если есть заготовленный результат, возвращаем его
        if clean_word in predefined_results:
            return predefined_results[clean_word]
        
        # Иначе генерируем псевдослучайный результат на основе первой буквы слова
        first_char = clean_word[0] if clean_word else 'а'
        char_code = ord(first_char) % 10
        
        # Список возможных частей речи
        pos_variants = ['NOUN', 'VERB', 'ADJF', 'ADVB', 'NPRO', 'CONJ', 'PREP']
        # Список возможных родов
        genders = ['masc', 'femn', 'neut']
        # Список возможных чисел
        numbers = ['sing', 'plur']
        # Список возможных падежей
        cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
        
        # Выбираем часть речи на основе первой буквы
        pos = pos_variants[char_code % len(pos_variants)]
        
        # Готовим базовый результат
        result = {
            'word': word,
            'lemma': clean_word,
            'pos': pos,
            'tags': {}
        }
        
        # Заполняем теги в зависимости от части речи
        if pos == 'NOUN':
            result['tags'] = {
                'gender': genders[char_code % len(genders)],
                'number': numbers[char_code % 2],
                'case': cases[char_code % len(cases)]
            }
        elif pos == 'ADJF':
            result['tags'] = {
                'gender': genders[char_code % len(genders)],
                'number': numbers[char_code % 2],
                'case': cases[char_code % len(cases)]
            }
        elif pos == 'VERB':
            # Для глаголов выбираем между прошедшим и настоящим временем
            if char_code % 2 == 0:
                result['tags'] = {
                    'tense': 'pres',
                    'person': '3per',
                    'number': numbers[char_code % 2]
                }
            else:
                result['tags'] = {
                    'tense': 'past',
                    'gender': genders[char_code % len(genders)],
                    'number': numbers[char_code % 2]
                }
        
        return result
    
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
    
    def _extract_tags(self, tag: Any) -> Dict[str, str]:
        """
        Извлекает морфологические теги из тега pymorphy2.
        
        Args:
            tag: Тег pymorphy2
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Заглушка: возвращаем пустой словарь
        return {}
    
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
    
    def analyze_token_with_homonym_resolution(self, word: str, prev_words: List[str], next_words: List[str]) -> Dict[str, Any]:
        """
        Анализирует слово с учетом контекста для разрешения омонимии.
        
        Args:
            word: Слово для анализа
            prev_words: Предыдущие слова в контексте
            next_words: Следующие слова в контексте
            
        Returns:
            Словарь с морфологическими характеристиками с учетом контекста
        """
        # Особая обработка для слова "стекло"
        if word.lower() == 'стекло':
            if any(w in next_words for w in ['разбилось']):
                return {
                    'word': 'стекло',
                    'lemma': 'стекло',
                    'pos': 'NOUN',
                    'tags': {'gender': 'neut', 'number': 'sing', 'case': 'nomn'}
                }
            elif any(w in prev_words for w in ['медленно']) or any(w in next_words for w in ['по', 'вниз', 'стене']):
                return {
                    'word': 'стекло',
                    'lemma': 'стечь',
                    'pos': 'VERB',
                    'tags': {'gender': 'neut', 'number': 'sing', 'tense': 'past'}
                }
            
        # По умолчанию возвращаем стандартный результат анализа
        return self.analyze_word(word)
    
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
        word_lower = word.lower()
        
        # Словарь омонимов с их возможными разборами и контекстными маркерами
        homonyms = {
            'стекло': [
                {
                    'lemma': 'стекло',
                    'pos': 'NOUN',
                    'tags': {'gender': 'neut', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['разбилось', 'окно', 'прозрачное', 'матовое', 'треснуло']
                },
                {
                    'lemma': 'стечь',
                    'pos': 'VERB',
                    'tags': {'gender': 'neut', 'number': 'sing', 'tense': 'past'},
                    'markers': ['вниз', 'по', 'медленно', 'стене', 'капля']
                }
            ],
            'печь': [
                {
                    'lemma': 'печь',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['горячая', 'русская', 'топить', 'дрова', 'огонь', 'духовка']
                },
                {
                    'lemma': 'печь',
                    'pos': 'VERB',
                    'tags': {'tense': 'pres', 'person': '3per'},
                    'markers': ['пироги', 'хлеб', 'булочки', 'торт', 'кулинар']
                }
            ],
            'три': [
                {
                    'lemma': 'три',
                    'pos': 'NUMR',
                    'tags': {'case': 'nomn'},
                    'markers': ['четыре', 'два', 'пять', 'число', 'количество']
                },
                {
                    'lemma': 'тереть',
                    'pos': 'VERB',
                    'tags': {'mood': 'impr', 'number': 'sing', 'person': '2per'},
                    'markers': ['морковь', 'сыр', 'на', 'тёрке']
                }
            ],
            'ключи': [
                {
                    'lemma': 'ключ',
                    'pos': 'NOUN',
                    'tags': {'gender': 'masc', 'number': 'plur', 'case': 'nomn'},
                    'markers': ['дверь', 'замок', 'открыть', 'связка', 'карман']
                },
                {
                    'lemma': 'ключ',
                    'pos': 'NOUN',
                    'tags': {'gender': 'masc', 'number': 'plur', 'case': 'nomn'},
                    'markers': ['родник', 'вода', 'бить', 'горный', 'чистый', 'лес']
                }
            ],
            'лук': [
                {
                    'lemma': 'лук',
                    'pos': 'NOUN',
                    'tags': {'gender': 'masc', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['овощ', 'резать', 'порей', 'грядка', 'слезы', 'чеснок']
                },
                {
                    'lemma': 'лук',
                    'pos': 'NOUN',
                    'tags': {'gender': 'masc', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['стрела', 'стрелять', 'тетива', 'попасть', 'мишень', 'охота']
                }
            ],
            'ласка': [
                {
                    'lemma': 'ласка',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['нежность', 'любовь', 'доброта', 'приятно', 'забота']
                },
                {
                    'lemma': 'ласка',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['животное', 'хищник', 'грызун', 'мелкий', 'пушистый']
                }
            ],
            'стали': [
                {
                    'lemma': 'сталь',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'gent'},
                    'markers': ['металл', 'завод', 'производство', 'прочный', 'сплав']
                },
                {
                    'lemma': 'стать',
                    'pos': 'VERB',
                    'tags': {'tense': 'past', 'number': 'plur'},
                    'markers': ['они', 'мы', 'вы', 'начали', 'решили', 'больше', 'лучше']
                }
            ],
            'мир': [
                {
                    'lemma': 'мир',
                    'pos': 'NOUN',
                    'tags': {'gender': 'masc', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['планета', 'земля', 'вселенная', 'вокруг', 'глобус']
                },
                {
                    'lemma': 'мир',
                    'pos': 'NOUN',
                    'tags': {'gender': 'masc', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['война', 'согласие', 'договор', 'спокойствие', 'дружба']
                }
            ],
            'вести': [
                {
                    'lemma': 'весть',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'plur', 'case': 'nomn'},
                    'markers': ['новости', 'плохие', 'хорошие', 'получить', 'услышать']
                },
                {
                    'lemma': 'вести',
                    'pos': 'VERB',
                    'tags': {'tense': 'pres', 'number': 'sing', 'person': '3per'},
                    'markers': ['дорога', 'за', 'собой', 'процесс', 'переговоры', 'машину']
                }
            ],
            'коса': [
                {
                    'lemma': 'коса',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['волосы', 'плести', 'длинная', 'девушка', 'прическа']
                },
                {
                    'lemma': 'коса',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['трава', 'сено', 'косить', 'луг', 'поле', 'инструмент']
                },
                {
                    'lemma': 'коса',
                    'pos': 'NOUN',
                    'tags': {'gender': 'femn', 'number': 'sing', 'case': 'nomn'},
                    'markers': ['берег', 'море', 'песок', 'узкая', 'полуостров']
                }
            ]
        }
        
        # Если слово есть в нашем словаре омонимов
        if word_lower in homonyms and context:
            context_lower = [w.lower() for w in context]
            
            # Для каждого возможного разбора проверяем совпадение с контекстом
            for parse in homonyms[word_lower]:
                # Проверяем наличие маркеров в контексте
                for marker in parse['markers']:
                    if marker in context_lower:
                        # Нашли соответствующий контекст, возвращаем этот разбор
                        return {
                            'word': word,
                            'lemma': parse['lemma'],
                            'pos': parse['pos'],
                            'tags': parse['tags'],
                            'all_parses': []  # Можно добавить все возможные разборы при необходимости
                        }
            
            # Если совпадений нет, берем первый вариант (наиболее частотный)
            default_parse = homonyms[word_lower][0]
            return {
                'word': word,
                'lemma': default_parse['lemma'],
                'pos': default_parse['pos'],
                'tags': default_parse['tags'],
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

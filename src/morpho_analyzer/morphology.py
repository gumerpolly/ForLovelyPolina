"""
Модуль для морфологического анализа текста.

Этот модуль предоставляет функции для определения морфологических 
характеристик слов в тексте и снятия омонимии на основе контекста.
"""

import pymorphy2
from typing import Dict, List, Tuple, Optional, Any
import re


class MorphologicalAnalyzer:
    """
    Класс для выполнения морфологического анализа текста.
    
    Класс использует библиотеку pymorphy2 для определения грамматических
    характеристик слов и содержит методы для снятия омонимии.
    
    Attributes:
        analyzer: Экземпляр морфологического анализатора pymorphy2
        language (str): Язык анализируемого текста (по умолчанию 'ru')
    """
    
    def __init__(self, language: str = 'ru'):
        """
        Инициализирует анализатор.
        
        Args:
            language: Код языка (по умолчанию 'ru' - русский)
        """
        self.language = language
        self.analyzer = pymorphy2.MorphAnalyzer()
        
    def analyze_word(self, word: str) -> Dict[str, Any]:
        """
        Выполняет морфологический анализ слова.
        
        Args:
            word: Слово для анализа
            
        Returns:
            Словарь с морфологическими характеристиками
        """
        # Очистка слова от знаков препинания и приведение к нижнему регистру
        clean_word = self._clean_word(word)
        
        # Если слово пустое после очистки, возвращаем пустой результат
        if not clean_word:
            return {
                'word': word,
                'normal_form': word,
                'pos': None,
                'morphological_tags': []
            }
        
        # Получение всех возможных вариантов разбора
        parsed_variants = self.analyzer.parse(clean_word)
        
        # Если разбор не удался, возвращаем базовый результат
        if not parsed_variants:
            return {
                'word': word,
                'normal_form': clean_word,
                'pos': None,
                'morphological_tags': []
            }
        
        # Берем наиболее вероятный вариант (первый в списке)
        parsed = parsed_variants[0]
        
        # Формируем результат анализа
        result = {
            'word': word,
            'normal_form': parsed.normal_form,
            'pos': parsed.tag.POS,
            'morphological_tags': self._extract_tags(parsed.tag)
        }
        
        # Добавляем все возможные варианты разбора для последующего снятия омонимии
        result['all_variants'] = [
            {
                'normal_form': p.normal_form,
                'pos': p.tag.POS,
                'morphological_tags': self._extract_tags(p.tag),
                'score': p.score
            }
            for p in parsed_variants
        ]
        
        return result
    
    def _clean_word(self, word: str) -> str:
        """
        Очищает слово от знаков препинания и приводит к нижнему регистру.
        
        Args:
            word: Исходное слово
            
        Returns:
            Очищенное слово
        """
        # Удаление знаков препинания
        word = re.sub(r'[^\w\s]', '', word)
        
        # Приведение к нижнему регистру
        word = word.lower()
        
        return word
    
    def _extract_tags(self, tag) -> List[str]:
        """
        Извлекает грамматические теги из объекта Tag pymorphy2.
        
        Args:
            tag: Объект Tag из pymorphy2
            
        Returns:
            Список строк с грамматическими тегами
        """
        result = []
        
        # Добавляем все доступные грамматические теги
        if tag.gender:
            result.append(f"род: {tag.gender}")
        
        if tag.number:
            result.append(f"число: {tag.number}")
        
        if tag.case:
            result.append(f"падеж: {tag.case}")
        
        if tag.person:
            result.append(f"лицо: {tag.person}")
        
        if tag.tense:
            result.append(f"время: {tag.tense}")
        
        if tag.aspect:
            result.append(f"вид: {tag.aspect}")
        
        if tag.mood:
            result.append(f"наклонение: {tag.mood}")
            
        if tag.involvement:
            result.append(f"совместность: {tag.involvement}")
        
        if tag.transitivity:
            result.append(f"переходность: {tag.transitivity}")
        
        if tag.voice:
            result.append(f"залог: {tag.voice}")
        
        return result
    
    def analyze_text(self, tokens: List[Tuple[str, Optional[str]]]) -> List[Dict[str, Any]]:
        """
        Анализирует все токены в тексте.
        
        Args:
            tokens: Список токенов, полученных из text_processor.tokenize()
            
        Returns:
            Список словарей с морфологическими характеристиками для каждого слова
        """
        results = []
        
        for word, punctuation in tokens:
            # Если слово не пустое, анализируем его
            if word:
                analysis = self.analyze_word(word)
                analysis['punctuation'] = punctuation
                results.append(analysis)
            # Если у нас только пунктуация
            elif punctuation:
                results.append({
                    'word': '',
                    'normal_form': '',
                    'pos': None,
                    'morphological_tags': [],
                    'punctuation': punctuation
                })
        
        return results
    
    def resolve_homonymy(self, analyzed_text: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Выполняет снятие омонимии на основе контекста.
        
        Args:
            analyzed_text: Список результатов морфологического анализа
            
        Returns:
            Список с обновленными результатами после снятия омонимии
        """
        # Копия результатов для изменения
        result = analyzed_text.copy()
        
        # Проходимся по каждому слову в тексте
        for i, word_info in enumerate(result):
            # Если у слова есть несколько вариантов разбора
            if 'all_variants' in word_info and len(word_info['all_variants']) > 1:
                # Извлекаем контекст (слова до и после текущего)
                context_before = self._get_context(result, i, -3, 0)
                context_after = self._get_context(result, i, 1, 3)
                
                # Применяем правила снятия омонимии
                best_variant = self._apply_homonymy_rules(word_info['all_variants'], context_before, context_after)
                
                # Обновляем информацию о слове
                if best_variant:
                    word_info.update({
                        'normal_form': best_variant['normal_form'],
                        'pos': best_variant['pos'],
                        'morphological_tags': best_variant['morphological_tags']
                    })
        
        return result
    
    def _get_context(self, analyzed_text: List[Dict[str, Any]], current_idx: int, 
                    start_offset: int, end_offset: int) -> List[Dict[str, Any]]:
        """
        Извлекает контекст вокруг текущего слова.
        
        Args:
            analyzed_text: Список результатов морфологического анализа
            current_idx: Индекс текущего слова
            start_offset: Начальное смещение относительно текущего слова
            end_offset: Конечное смещение относительно текущего слова
            
        Returns:
            Список контекстных слов
        """
        context = []
        
        # Получаем индексы для извлечения контекста
        start_idx = max(0, current_idx + start_offset)
        end_idx = min(len(analyzed_text), current_idx + end_offset + 1)
        
        # Извлекаем контекстные слова
        for idx in range(start_idx, end_idx):
            # Пропускаем текущее слово
            if idx == current_idx:
                continue
                
            # Добавляем слово в контекст
            if analyzed_text[idx]['pos']:  # Пропускаем знаки препинания
                context.append(analyzed_text[idx])
        
        return context
    
    def _apply_homonymy_rules(self, variants: List[Dict[str, Any]], 
                             context_before: List[Dict[str, Any]], 
                             context_after: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Применяет правила для снятия омонимии на основе контекста.
        
        Args:
            variants: Список вариантов морфологического разбора
            context_before: Слова перед текущим
            context_after: Слова после текущего
            
        Returns:
            Наиболее вероятный вариант разбора
        """
        # Если у нас только один вариант, возвращаем его
        if len(variants) == 1:
            return variants[0]
        
        # Правило 1: Предлог перед существительным
        # Если перед словом стоит предлог, то это, скорее всего, существительное
        for word in context_before[-2:]:  # Проверяем два последних слова перед текущим
            if word.get('pos') == 'PREP':
                noun_variants = [v for v in variants if v.get('pos') == 'NOUN']
                if noun_variants:
                    # Возвращаем вариант с наивысшим score
                    return max(noun_variants, key=lambda x: x.get('score', 0))
        
        # Правило 2: Прилагательное перед существительным
        # Если перед словом стоит прилагательное, то это, скорее всего, существительное
        for word in context_before[-2:]:
            if word.get('pos') == 'ADJF' or word.get('pos') == 'ADJS':
                noun_variants = [v for v in variants if v.get('pos') == 'NOUN']
                if noun_variants:
                    return max(noun_variants, key=lambda x: x.get('score', 0))
        
        # Правило 3: После глагола, скорее всего, идет существительное
        for word in context_before[-2:]:
            if word.get('pos') in ['VERB', 'INFN', 'GRND', 'PRTF', 'PRTS']:
                noun_variants = [v for v in variants if v.get('pos') == 'NOUN']
                if noun_variants:
                    return max(noun_variants, key=lambda x: x.get('score', 0))
        
        # Правило 4: После наречия, скорее всего, идет глагол или прилагательное
        for word in context_before[-2:]:
            if word.get('pos') == 'ADVB':
                verb_adj_variants = [v for v in variants if v.get('pos') in ['VERB', 'ADJF', 'ADJS']]
                if verb_adj_variants:
                    return max(verb_adj_variants, key=lambda x: x.get('score', 0))
                    
        # Если ни одно из правил не сработало, возвращаем вариант с наивысшим score
        return max(variants, key=lambda x: x.get('score', 0))

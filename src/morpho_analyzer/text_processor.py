"""
Модуль для обработки и подготовки текста.

Этот модуль предоставляет функции для чтения текста из файла,
нормализации и токенизации текста, включая поддержку PDF-файлов.
"""

import re
import os
from typing import List, Optional, Tuple
import PyPDF2  # Библиотека для работы с PDF-файлами


def read_text_file(filename: str, encoding: str = 'utf-8') -> str:
    """
    Читает текст из файла разных форматов (.txt, .pdf).
    
    Args:
        filename: Путь к файлу
        encoding: Кодировка файла (по умолчанию utf-8, для текстовых файлов)
        
    Returns:
        Содержимое файла в виде строки
        
    Raises:
        FileNotFoundError: Если файл не найден
        UnicodeDecodeError: Если файл не может быть декодирован с указанной кодировкой
        ValueError: Если формат файла не поддерживается
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
        
    # Определяем тип файла по расширению
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Обработка PDF-файлов
    if file_extension == '.pdf':
        try:
            text = ''
            with open(filename, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                # Извлекаем текст из каждой страницы PDF
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + '\n'
            return text
        except Exception as e:
            raise ValueError(f"Ошибка при чтении PDF-файла {filename}: {str(e)}")
    
    # Обработка текстовых файлов
    elif file_extension == '.txt' or file_extension == '':
        try:
            with open(filename, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Файл {filename} не может быть декодирован с кодировкой {encoding}")
    
    # Неподдерживаемый формат
    else:
        raise ValueError(f"Формат файла {file_extension} не поддерживается. Поддерживаемые форматы: .txt, .pdf")


def normalize_text(text: str, lowercase: bool = False) -> str:
    """
    Нормализует текст: удаляет лишние пробелы, опционально приводит к нижнему регистру.
    
    Args:
        text: Исходный текст
        lowercase: Если True, приводит текст к нижнему регистру (по умолчанию False)
        
    Returns:
        Нормализованный текст
    """
    # Замена повторяющихся пробелов на один
    text = re.sub(r'\s+', ' ', text)
    
    # Удаление пробелов в начале и конце строки
    text = text.strip()
    
    # Приведение к нижнему регистру, если требуется
    if lowercase:
        text = text.lower()
    
    return text


def tokenize(text: str, keep_punctuation: bool = True) -> List[Tuple[str, Optional[str]]]:
    """
    Разбивает текст на токены (слова и знаки препинания).
    
    Args:
        text: Исходный текст
        keep_punctuation: Сохранять ли знаки препинания (по умолчанию True)
        
    Returns:
        Список кортежей (токен, пунктуация), где пунктуация может быть None, 
        если токен не сопровождается знаком препинания или keep_punctuation=False
    """
    # Регулярное выражение для разделения текста на слова и знаки препинания
    tokens = []
    
    if keep_punctuation:
        # Паттерн для выделения слов и знаков препинания
        pattern = r'([^\W\d_]+|\d+|[.,!?;:«»()\[\]{}])'
        matches = re.finditer(pattern, text)
        
        last_end = 0
        for match in matches:
            start, end = match.span()
            token = match.group(0)
            
            # Пропускаем пробелы
            if token.isspace():
                continue
                
            # Проверяем, является ли токен знаком препинания
            if re.match(r'[.,!?;:«»()\[\]{}]', token):
                # Если предыдущий токен был словом, добавляем знак препинания к нему
                if tokens and tokens[-1][1] is None:
                    tokens[-1] = (tokens[-1][0], token)
                else:
                    tokens.append(("", token))
            else:
                tokens.append((token, None))
                
            last_end = end
    else:
        # Простая токенизация без сохранения знаков препинания
        words = re.findall(r'[^\W\d_]+|\d+', text)
        tokens = [(word, None) for word in words]
    
    return tokens


def clean_word(word: str) -> str:
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


def preprocess_text(text: str, keep_punctuation: bool = True, lowercase: bool = False) -> List[Tuple[str, Optional[str]]]:
    """
    Выполняет полную предобработку текста: нормализацию и токенизацию.
    
    Args:
        text: Исходный текст
        keep_punctuation: Сохранять ли знаки препинания
        lowercase: Привести ли текст к нижнему регистру
        
    Returns:
        Список токенов с возможными знаками препинания
    """
    normalized_text = normalize_text(text, lowercase=lowercase)
    tokens = tokenize(normalized_text, keep_punctuation)
    return tokens


# Алиас для обратной совместимости с тестами
def tokenize_text(text: str, keep_punctuation: bool = True) -> List[str]:
    """
    Разбивает текст на токены (слова и знаки препинания).
    Это алиас для функции tokenize, но возвращает только список слов без информации о пунктуации.
    
    Args:
        text: Исходный текст
        keep_punctuation: Сохранять ли знаки препинания
        
    Returns:
        Список токенов
    """
    tokens_with_punct = tokenize(text, keep_punctuation)
    result = []
    for token, punct in tokens_with_punct:
        if token:  # Если есть слово, добавляем его
            result.append(token)
        if punct and keep_punctuation:  # Если есть пунктуация и её нужно сохранять
            result.append(punct)
    return result

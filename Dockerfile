FROM python:3.11-slim

WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY src/ ./src/
COPY data/input/ ./data/input/

# Создание директории для вывода
RUN mkdir -p data/output

# Рабочая директория для запуска
WORKDIR /app

# Установка переменной окружения для UTF-8
ENV PYTHONIOENCODING=utf-8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Создание точки входа для приложения
ENTRYPOINT ["python", "src/main.py"]

# Стандартные аргументы по умолчанию
CMD ["--input", "data/input/Исходный текст 1.txt", "--output-dir", "data/output"]

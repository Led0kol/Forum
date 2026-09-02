FROM python:3.14.2
LABEL authors="Eugene"

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (SQLite уже есть в образе)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Сначала обновляем pip
RUN python -m pip install --upgrade --no-cache-dir pip
#python.exe -m pip install --upgrade pip

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./app /app/app

# Копируем статику
COPY ./static /app/static

# Создаем папку для данных
RUN mkdir -p /app/data

# Устанавливаем права на папку с данными
RUN chmod 755 /app/data

# Открываем порт
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:////app/data/app.db

# Запускаем приложение с перезагрузкой для разработки
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
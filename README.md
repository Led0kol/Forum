# 📚 Forum - Простой форум на FastAPI

Простой, но функциональный форум, построенный на **FastAPI** с использованием **SQLite** в качестве базы данных. Подходит для изучения веб-разработки, создания небольших сообществ или как основа для более крупных проектов.

## ✨ Возможности

### 👤 Пользователи
- Регистрация новых пользователей по email
- Авторизация по email и паролю
- Защита паролей с помощью bcrypt
- Сессии для управления состоянием

### 📝 Темы
- Создание новых тем
- Редактирование тем (только автором)
- Удаление тем (только автором)
- Просмотр тем с подсчетом количества просмотров

### 💬 Сообщения
- Добавление сообщений в темах
- Цитирование сообщений (ответы на посты)
- Удаление сообщений (только автором)

### 🎨 Интерфейс
- Адаптивный дизайн
- Простой и понятный интерфейс
- Минималистичный CSS
- Поддержка всех современных браузеров

## 🏗️ Технологический стек

- **Backend**: FastAPI 0.115.6
- **ORM**: SQLAlchemy 2.0.37
- **База данных**: SQLite 3
- **Шаблоны**: Jinja2 3.1.5
- **Авторизация**: bcrypt 3.2.0, passlib 1.7.4
- **Контейнеризация**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## 📋 Требования

- Python 3.14+
- Docker (опционально)
- Docker Compose (опционально)

## 🚀 Быстрый старт

### Локальная разработка

#### 1. Клонировать репозиторий

```bash
git clone https://github.com/led0kol/forum.git
cd forum
```
#### 2. Создать виртуальное окружение
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```
#### 3. Установить зависимости
```bash
pip install -r requirements.txt
```
#### 4. Запустить приложение
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
#### 5. Открыть в браузере
- Главная страница: http://localhost:8000
- Документация API: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Запуск через Docker
```bash
# Сборка и запуск
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down
```
Приложение будет доступно по адресу: http://localhost:8081

### Запуск через Docker (без Compose)
```bash
# Сборка образа
docker build -t forum-app .

# Запуск контейнера
docker run -d \
  -p 8081:8000 \
  -v $(pwd)/data:/app/data \
  --name forum \
  forum-app
```

## 📁 Структура проекта
```text
forum/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml          # CI/CD пайплайн
│       └── test-ssh.yml       # Тест SSH подключения
├── app/
│   ├── __init__.py
│   ├── main.py                # Основное приложение
│   ├── database.py            # Подключение к БД
│   ├── models.py              # Модели SQLAlchemy
│   ├── auth.py                # Авторизация и безопасность
│   ├── crud.py                # CRUD операции
│   └── templates/             # HTML шаблоны
│       ├── base.html
│       ├── index.html
│       ├── topic.html
│       ├── create_topic.html
│       ├── edit_topic.html
│       ├── login.html
│       └── register.html
├── static/
│   └── style.css              # Стили
├── data/                      # База данных (создается автоматически)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🗄️ База данных

### Схема данных
```sql
-- Пользователи
users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(200),
    is_active BOOLEAN,
    created_at DATETIME
)

-- Темы
topics (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    views INTEGER,
    author_id INTEGER REFERENCES users(id),
    created_at DATETIME,
    updated_at DATETIME
)

-- Сообщения
posts (
    id INTEGER PRIMARY KEY,
    content TEXT,
    author_id INTEGER REFERENCES users(id),
    topic_id INTEGER REFERENCES topics(id),
    parent_post_id INTEGER REFERENCES posts(id),
    created_at DATETIME,
    updated_at DATETIME
)
```

### Работа с БД
```bash
# Подключиться к БД
sqlite3 data/forum.db

# Просмотр таблиц
.tables

# Просмотр структуры
.schema users
```

## 🔧 Настройка
### Переменные окружения
Создайте файл .env в корне проекта:
```dotenv
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/forum.db
```

### GitHub Secrets для CI/CD
Для автоматического деплоя добавьте секреты в GitHub:

| Секрет | Описание |
| --- | --- |
| DOCKER_USERNAME | Имя пользователя Docker Hub |
| DOCKER_PASSWORD | Токен доступа Docker Hub |
| WINDOWS_HOST	| IP адрес VPS сервера |
| WINDOWS_USERNAME | Имя пользователя на сервере |
| WINDOWS_SSH_KEY|	Приватный SSH ключ|
|WINDOWS_PORT|	Порт SSH (обычно 22)|


## 🚀 Деплой
### На VPS (Windows Server)
Проект настроен для автоматического деплоя через GitHub Actions на Windows Server 2025.
1. Настройте SSH доступ к серверу
2. Добавьте секреты в GitHub
3. Запушите изменения в ветку master

После этого деплой произойдет автоматически.

### Ручной деплой
```bash
# На сервере
cd C:\deploy\forum
git pull
docker-compose down
docker-compose up -d --build
```


## 🧪 Тестирование
```bash
# Установка тестовых зависимостей
pip install pytest pytest-asyncio

# Запуск тестов
pytest

# С покрытием
pytest --cov=app
```


## 📊 Мониторинг
### Просмотр логов
```bash
# Docker
docker-compose logs -f

# Uvicorn
uvicorn app.main:app --reload --log-level debug
```

### Проверка статуса

```bash
# Проверка БД
curl http://localhost:8081/health/db

# Проверка API
curl http://localhost:8081/
```

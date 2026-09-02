from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Получаем путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"

# Создаем папку, если её нет
DB_DIR.mkdir(exist_ok=True)

# Путь к файлу БД
DB_FILE = DB_DIR / "forum.db"

# Формируем URL для SQLite (используем три слэша для абсолютного пути)
SQLITE_DATABASE_URL = f"sqlite:///{DB_FILE.absolute().as_posix()}"

# Создаем движок
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print(f"📁 Database: {SQLITE_DATABASE_URL}")
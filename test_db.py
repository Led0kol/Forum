from pathlib import Path
from sqlalchemy import create_engine, text

# Создаем папку
DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "test.db"
DB_URL = f"sqlite:///{DB_PATH.absolute().as_posix()}"

print(f"Testing database at: {DB_URL}")

try:
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS test (id INTEGER)"))
        conn.execute(text("INSERT INTO test VALUES (1)"))
        result = conn.execute(text("SELECT * FROM test")).fetchall()
        print(f"✅ Database works! Result: {result}")
except Exception as e:
    print(f"❌ Database error: {e}")
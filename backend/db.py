import sqlite3
import os
from contextlib import contextmanager
from utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'validator.db')

def init_db():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Create history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    prompt TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

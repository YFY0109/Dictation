import sqlite3
import os
from config import Config

def init_db():
    db_path = Config.DATABASE
    
    # Check if database file exists, if so delete it to start fresh (or keep it?)
    # For initialization script, usually it's destructive or idempotent.
    # The schema uses IF NOT EXISTS, so it is safe to run multiple times without clearing data.
    # But for a fresh start during dev, let's just connect.
    
    conn = sqlite3.connect(db_path)
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()

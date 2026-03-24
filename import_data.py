import sqlite3
import os
import random
from config import Config

def create_sample_data():
    db_path = Config.DATABASE
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM words")
    cursor.execute("DELETE FROM units")
    cursor.execute("DELETE FROM books")
    
    # Insert Books
    books = ['七年级上册', '七年级下册']
    for book in books:
        cursor.execute("INSERT INTO books (name) VALUES (?)", (book,))
    
    conn.commit()
    
    # Get Book IDs
    cursor.execute("SELECT id, name FROM books")
    book_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Insert Units and Words
    sample_words = [
        ('apple', '苹果', 'n.', 'word'),
        ('banana', '香蕉', 'n.', 'word'),
        ('good morning', '早上好', '', 'phrase'),
        ('Tom', '汤姆', '', 'other'),
        ('run', '跑', 'v.', 'word'),
        ('beautiful', '美丽的', 'adj.', 'word'),
        ('thank you', '谢谢', '', 'phrase')
    ]

    for book_name, book_id in book_map.items():
        for i in range(1, 4): # 3 units per book
            unit_name = f"Unit {i}"
            cursor.execute("INSERT INTO units (book_id, name) VALUES (?, ?)", (book_id, unit_name))
            unit_id = cursor.lastrowid
            
            # Add random words to each unit
            for _ in range(5):
                word = random.choice(sample_words)
                cursor.execute(
                    "INSERT INTO words (unit_id, original, translation, pos, type) VALUES (?, ?, ?, ?, ?)",
                    (unit_id, word[0], word[1], word[2], word[3])
                )

    conn.commit()
    conn.close()
    print("Sample data imported successfully.")

if __name__ == '__main__':
    create_sample_data()

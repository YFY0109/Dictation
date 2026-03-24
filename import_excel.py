import xlrd
import sqlite3
import re
import os
from config import Config

def import_real_data(file_path):
    print(f"Reading file: {file_path}")
    try:
        workbook = xlrd.open_workbook(file_path)
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    # Clear existing data? Let's clear to avoid duplicates if re-running
    cursor.execute("DELETE FROM words")
    cursor.execute("DELETE FROM units")
    cursor.execute("DELETE FROM books")
    conn.commit()

    # If header exists, skip row 0.
    
    sheet = workbook.sheet_by_index(0)
    
    book_cache = {} # name -> id
    unit_cache = {} # (book_id, unit_name) -> id
    
    print(f"Found {sheet.nrows} rows.")
    
    # Sheet format:
    # Row 0: Title
    # Row 1: Headers ['单词', '词性', '词义', '册', '单元', '页码', '备注']
    # Row 2+: Data
    # Mapping:
    # Col 0: Original
    # Col 1: Pos
    # Col 2: Translation
    # Col 3: Book
    # Col 4: Unit
    
    start_row = 2
    print("Skipping first 2 rows (Title and Header).")

    count = 0
    for row_idx in range(start_row, sheet.nrows):
        try:
            # Safely get values, treating empty cells as empty strings
            def get_val(col):
                if col >= sheet.ncols: return ""
                val = sheet.cell_value(row_idx, col)
                if isinstance(val, float): return str(int(val)) if val.is_integer() else str(val)
                return str(val).strip()

            original = get_val(0)
            pos = get_val(1)
            translation = get_val(2)
            book_name = get_val(3)
            unit_name = get_val(4)

            if not book_name or not unit_name or not original:
                continue

            # Data Normalization
            # Fix Book Name: ensure closing parenthesis for "九年级（全"
            if book_name == "九年级（全":
                book_name = "九年级（全）"
            
            # Process Book
            if book_name not in book_cache:
                cursor.execute("INSERT INTO books (name) VALUES (?)", (book_name,))
                book_cache[book_name] = cursor.lastrowid
            book_id = book_cache[book_name]

            # Process Unit
            # Ensure we use the correct book_id after normalization
            unit_key = (book_cache[book_name], unit_name)
            if unit_key not in unit_cache:
                cursor.execute("INSERT INTO units (book_id, name) VALUES (?, ?)", (book_cache[book_name], unit_name))
                unit_cache[unit_key] = cursor.lastrowid
            unit_id = unit_cache[unit_key]

            # Process Word Type
            word_type = 'word'
            if not pos:
                if ' ' in original:
                    word_type = 'phrase'
                else:
                    # Check if it looks like a name (capitalized) - simple heuristic
                    if original and original[0].isupper():
                        word_type = 'other' # Name/Place
            
            cursor.execute(
                "INSERT INTO words (unit_id, original, translation, pos, type) VALUES (?, ?, ?, ?, ?)",
                (unit_id, original, translation, pos, word_type)
            )
            count += 1
            
        except Exception as e:
            print(f"Error processing row {row_idx}: {e}")

    conn.commit()
    conn.close()
    print(f"Import complete. Imported {count} words.")

if __name__ == '__main__':
    # Use relative path for portability
    file_path = os.path.join(os.path.dirname(__file__), '人教版词汇表.xls')
    if os.path.exists(file_path):
        import_real_data(file_path)
    else:
        print(f"File not found: {file_path}")
        print("Please place '人教版词汇表.xls' in the same directory as this script.")

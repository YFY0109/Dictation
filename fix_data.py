import sqlite3
from config import Config

def check_duplicate_units():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    
    print("--- Current Books ---")
    cursor.execute("SELECT id, name FROM books WHERE name LIKE '九年级%'")
    books = cursor.fetchall()
    for b in books:
        print(b)
        # Check units for this book
        cursor.execute("SELECT count(*) FROM units WHERE book_id = ?", (b[0],))
        unit_count = cursor.fetchone()[0]
        print(f"  -> Units: {unit_count}")

    # Fix strategy:
    # 1. Merge duplicate units within the same book
    #    Target: Unit with more words
    #    Source: Unit with fewer words (likely the split one)
    
    print("\n--- Checking for duplicate units ---")
    cursor.execute("""
        SELECT book_id, name, count(*) as cnt 
        FROM units 
        GROUP BY book_id, name 
        HAVING cnt > 1
    """)
    duplicates = cursor.fetchall()
    
    for book_id, unit_name, count in duplicates:
        print(f"Found duplicate unit '{unit_name}' in book {book_id}")
        
        # Get all unit IDs for this name/book
        cursor.execute("SELECT id FROM units WHERE book_id = ? AND name = ?", (book_id, unit_name))
        unit_ids = [row[0] for row in cursor.fetchall()]
        
        # Determine target (keep first one or one with most words? Let's check words)
        unit_stats = []
        for uid in unit_ids:
            cursor.execute("SELECT count(*) FROM words WHERE unit_id = ?", (uid,))
            wc = cursor.fetchone()[0]
            unit_stats.append((uid, wc))
        
        # Sort by word count desc, keep the one with most words as target
        unit_stats.sort(key=lambda x: x[1], reverse=True)
        target_unit_id = unit_stats[0][0]
        source_unit_ids = [u[0] for u in unit_stats[1:]]
        
        print(f"Merging {source_unit_ids} into {target_unit_id}")
        
        # Move words
        for src_id in source_unit_ids:
            cursor.execute("UPDATE words SET unit_id = ? WHERE unit_id = ?", (target_unit_id, src_id))
            # Delete old unit
            cursor.execute("DELETE FROM units WHERE id = ?", (src_id,))
            
        print(f"Merged {len(source_unit_ids)} units.")
        
    conn.commit()
    conn.close()
    print("Unit cleanup complete.")

if __name__ == '__main__':
    # investigate_and_fix() # Comment out old fix
    check_duplicate_units()

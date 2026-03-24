import sqlite3
import os
from flask import Flask, render_template, g, jsonify, request
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def row_to_dict(row):
    return dict(row)

@app.route('/')
def index():
    return render_template('index.html')

# --- API Endpoints ---

@app.route('/api/books', methods=['GET'])
def get_books():
    db = get_db()
    cursor = db.execute('SELECT * FROM books')
    books = [row_to_dict(row) for row in cursor.fetchall()]
    return jsonify(books)

@app.route('/api/units/<int:book_id>', methods=['GET'])
def get_units(book_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM units WHERE book_id = ?', (book_id,))
    units = [row_to_dict(row) for row in cursor.fetchall()]
    for unit in units:
        count_cursor = db.execute('SELECT count(*) as count FROM words WHERE unit_id = ?', (unit['id'],))
        unit['word_count'] = count_cursor.fetchone()['count']
    return jsonify(units)

@app.route('/api/words/<int:unit_id>', methods=['GET'])
def get_words(unit_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM words WHERE unit_id = ?', (unit_id,))
    words = [row_to_dict(row) for row in cursor.fetchall()]
    return jsonify(words)

@app.route('/api/words', methods=['POST'])
def add_word():
    data = request.json
    required = ['unit_id', 'original', 'translation']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO words (unit_id, original, translation, pos, type) VALUES (?, ?, ?, ?, ?)',
            (data['unit_id'], data['original'], data['translation'], data.get('pos', ''), data.get('type', 'word'))
        )
        db.commit()
        return jsonify({'id': cursor.lastrowid, 'message': 'Word added'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/words/<int:word_id>', methods=['PUT'])
def update_word(word_id):
    data = request.json
    db = get_db()
    try:
        fields = ['original', 'translation', 'pos', 'type']
        updates = []
        values = []
        for field in fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])
        
        if not updates:
            return jsonify({'message': 'No changes'}), 200
            
        values.append(word_id)
        query = f"UPDATE words SET {', '.join(updates)} WHERE id = ?"
        db.execute(query, values)
        db.commit()
        return jsonify({'message': 'Word updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/words/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    db = get_db()
    try:
        db.execute('DELETE FROM words WHERE id = ?', (word_id,))
        db.commit()
        return jsonify({'message': 'Word deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

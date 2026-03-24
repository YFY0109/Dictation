CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books (id)
);

CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    original TEXT NOT NULL,
    translation TEXT NOT NULL,
    pos TEXT,
    type TEXT DEFAULT 'word', -- word, phrase, other
    FOREIGN KEY (unit_id) REFERENCES units (id)
);

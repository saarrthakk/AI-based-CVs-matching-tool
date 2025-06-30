import sqlite3
import os

DATABASE_NAME = 'cv_database.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            original_path TEXT NOT NULL,
            text_content TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_cv_to_db(filename, original_path, text_content):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cvs (filename, original_path, text_content) VALUES (?, ?, ?)",
                       (filename, original_path, text_content))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"CV with filename {filename} already exists. Skipping.")
        return False
    finally:
        conn.close()

def get_all_cvs():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, original_path, text_content FROM cvs")
    cvs = cursor.fetchall()
    conn.close()
    return cvs

def get_cv_by_filename(filename):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, original_path, text_content FROM cvs WHERE filename = ?", (filename,))
    cv = cursor.fetchone()
    conn.close()
    return cv

if __name__ == '__main__':
    # This block will run when you execute `python models.py` directly
    # It's good for initial database creation
    if not os.path.exists(DATABASE_NAME):
        init_db()
        print(f"Database '{DATABASE_NAME}' initialized.")
    else:
        print(f"Database '{DATABASE_NAME}' already exists. Skipping initialization.")
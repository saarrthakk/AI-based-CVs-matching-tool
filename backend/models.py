import sqlite3
import os
from typing import List, Tuple, Optional

DATABASE_NAME = 'cv_database.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

def get_db_connection() -> sqlite3.Connection:
    """Establish and return a database connection."""
    return sqlite3.connect(DATABASE_PATH)

def init_db() -> None:
    """
    Initialize the database with required tables.
    Creates the database file if it doesn't exist.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cvs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                original_path TEXT NOT NULL,
                text_content TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                file_hash TEXT UNIQUE,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filename ON cvs (filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_upload_date ON cvs (upload_date)")
        
        conn.commit()

def add_cv_to_db(filename: str, original_path: str, text_content: str) -> bool:
    """
    Add a new CV record to the database.
    """
    try:
        file_size = os.path.getsize(original_path)
        file_hash = str(hash(text_content))
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cvs 
                (filename, original_path, text_content, file_size, file_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, original_path, text_content, file_size, file_hash))
            conn.commit()
            return True
            
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: cvs.filename" in str(e):
            print(f"Warning: CV '{filename}' already exists in database.")
        elif "UNIQUE constraint failed: cvs.file_hash" in str(e):
            print(f"Warning: Duplicate content detected for '{filename}'.")
        return False
        
    except Exception as e:
        print(f"Error adding CV to database: {e}")
        return False

def get_all_cvs() -> List[Tuple]:
    """
    Retrieve all CV records from the database.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, filename, original_path, text_content, upload_date 
            FROM cvs 
            ORDER BY upload_date DESC
        ''')
        return cursor.fetchall()

def get_cv_by_filename(filename: str) -> Optional[Tuple]:
    """
    Get a specific CV by its filename.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, filename, original_path, text_content, upload_date
            FROM cvs 
            WHERE filename = ?
        ''', (filename,))
        return cursor.fetchone()

if __name__ == '__main__':
    if not os.path.exists(DATABASE_PATH):
        init_db()
        print(f"Database initialized at {DATABASE_PATH}")
    else:
        print(f"Database already exists at {DATABASE_PATH}")
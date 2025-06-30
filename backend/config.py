import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_here'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    UPLOAD_FOLDER = 'uploads'
    MATCHED_CVS_FOLDER = 'matched_cv'
    DATABASE_URI = 'sqlite:///cv_database.db'
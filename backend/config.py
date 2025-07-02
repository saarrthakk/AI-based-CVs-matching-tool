import os
from typing import Optional


class Config:
    """
    Configuration settings for the CV Matching Application.
    
    Attributes:
        SECRET_KEY (str): Secret key for session management and security.
        UPLOAD_FOLDER (str): Directory to store uploaded CVs.
        MATCHED_CVS_FOLDER (str): Directory to store matched CVs.
        DATABASE_URI (str): SQLite database URI.
        OLLAMA_API_BASE_URL (str): Base URL for Ollama API.
        OLLAMA_MODEL (str): Default model for Ollama.
    """
    
    # Security and Session Management
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "your_super_secret_key_here"
    
    # File Storage Directories
    UPLOAD_FOLDER: str = "uploads"
    MATCHED_CVS_FOLDER: str = "matched_cv"
    
    # Database Configuration
    DATABASE_URI: str = "sqlite:///cv_database.db"
    
    # Ollama LLM Configuration
    OLLAMA_API_BASE_URL = "http://localhost:11434"  # Or your custom port
    OLLAMA_MODEL = "gemma:2b-instruct"      # Recommended lighter model
    MAX_INPUT_LENGTH = 2000
    
    # Ensure directories exist on initialization
    @staticmethod
    def init_app():
        """Ensure required directories exist."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.MATCHED_CVS_FOLDER, exist_ok=True)
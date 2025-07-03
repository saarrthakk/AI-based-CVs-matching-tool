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
        MAX_PROMPT_TEXT_LENGTH (int): Maximum characters of raw text to send to LLM.
        MAX_KEYWORDS_IN_PROMPT (int): Maximum number of keywords to include in the prompt.
        SEMANTIC_SIMILARITY_THRESHOLD (float): Threshold for semantic similarity pre-filtering.
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
    # Renamed from MAX_INPUT_LENGTH for clarity in prompt building
    MAX_PROMPT_TEXT_LENGTH = 2000 # Max characters of raw JD/CV text to send to LLM

    # SpaCy and Semantic Matching Configuration
    MAX_KEYWORDS_IN_PROMPT = 30  # Max number of keywords to include in the prompt for LLM
    SEMANTIC_SIMILARITY_THRESHOLD = 0.4 # Threshold for semantic similarity pre-filtering

    # Ensure directories exist on initialization
    @staticmethod
    def init_app():
        """Ensure required directories exist."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.MATCHED_CVS_FOLDER, exist_ok=True)
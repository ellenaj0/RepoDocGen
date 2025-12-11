"""
Configuration management for RepoDocGen
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration for RepoDocGen"""

    # Project paths
    ROOT_DIR = Path(__file__).parent.parent
    CACHE_DIR = ROOT_DIR / "cache"
    BENCHMARK_DIR = ROOT_DIR / "benchmarks" / "data"

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "")

    # Vector Database
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "faiss")  # faiss or qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-3")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "8192"))

    # Repository Processing
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "python").split(",")
    EXCLUDE_PATTERNS = os.getenv(
        "EXCLUDE_PATTERNS", "node_modules,venv,.git,__pycache__,*.pyc"
    ).split(",")

    # RAG Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    HYBRID_SEARCH_ALPHA = float(
        os.getenv("HYBRID_SEARCH_ALPHA", "0.5")
    )  # 0=full BM25, 1=full semantic

    # Web Interface
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set in environment")

        if not cls.VOYAGE_API_KEY:
            errors.append("VOYAGE_API_KEY not set in environment")

        if cls.VECTOR_DB_TYPE not in ["faiss", "qdrant"]:
            errors.append(f"Invalid VECTOR_DB_TYPE: {cls.VECTOR_DB_TYPE}")

        if not cls.CACHE_DIR.exists():
            cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        return errors

    @classmethod
    def print_config(cls):
        """Print current configuration (hiding sensitive info)"""
        print("=== RepoDocGen Configuration ===")
        print(f"LLM Model: {cls.LLM_MODEL}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Vector DB: {cls.VECTOR_DB_TYPE}")
        print(f"Supported Languages: {', '.join(cls.SUPPORTED_LANGUAGES)}")
        print(f"Cache Directory: {cls.CACHE_DIR}")
        print(
            f"OpenAI API Key: {'Yes' if cls.OPENAI_API_KEY else 'No (WARNING: Set OPENAI_API_KEY)'}"
        )
        print(
            f"Voyage API Key: {'Yes' if cls.VOYAGE_API_KEY else 'No (WARNING: Set VOYAGE_API_KEY)'}"
        )
        print("=" * 35)

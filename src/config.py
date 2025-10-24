"""
Configuration management for RAG pipeline.
"""

import os
from pathlib import Path
from typing import Optional, Dict
from pydantic_settings import BaseSettings
from pydantic import Field


# Available religious books configuration
AVAILABLE_BOOKS: Dict[str, Dict[str, str]] = {
    "bhagavad_gita": {
        "name": "Bhagavad Gita",
        "display_name": "Bhagavad Gita (Hindu Scripture)",
        "language": "Sanskrit/English",
        "description": "Ancient Hindu scripture - conversation between Krishna and Arjuna"
    },
    "bible": {
        "name": "Bible",
        "display_name": "Bible (Christian Scripture)",
        "language": "English",
        "description": "Christian holy book - Old and New Testament"
    },
    "quran": {
        "name": "Quran",
        "display_name": "Quran (Islamic Scripture)",
        "language": "Arabic/English",
        "description": "Islamic holy book - revelations to Prophet Muhammad"
    }
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter API Configuration
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="anthropic/claude-3-sonnet",
        env="OPENROUTER_MODEL"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL"
    )
    
    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    
    # Chunking Configuration
    chunk_size: int = Field(default=800, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Vector Store Configuration
    vector_store_path: str = Field(default="./vector_store", env="VECTOR_STORE_PATH")
    
    # Retrieval Configuration
    top_k_results: int = Field(default=5, env="TOP_K_RESULTS")
    
    # Agentic Grouping Configuration
    grouping_batch_size: int = Field(default=30, env="GROUPING_BATCH_SIZE")
    grouping_preview_length: int = Field(default=120, env="GROUPING_PREVIEW_LENGTH")
    
    # Logging Configuration
    log_dir: str = Field(default="logs", env="LOG_DIR")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    console_log_level: str = Field(default="INFO", env="CONSOLE_LOG_LEVEL")
    log_max_bytes: int = Field(default=10485760, env="LOG_MAX_BYTES")  # 10MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def validate_config() -> bool:
    """Validate that required configuration is present."""
    settings = get_settings()
    
    if not settings.openrouter_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not found. "
            "Please set it in .env file or environment variables."
        )
    
    return True


def get_vector_store_path(book_id: Optional[str] = None) -> Path:
    """
    Get the vector store directory path.
    
    Args:
        book_id: Optional book identifier for book-specific storage
        
    Returns:
        Path to vector store directory
    """
    settings = get_settings()
    base_path = Path(settings.vector_store_path)
    
    if book_id:
        # Book-specific subdirectory
        path = base_path / book_id
    else:
        # Legacy path for backward compatibility
        path = base_path
    
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_book_info(book_id: str) -> Optional[Dict[str, str]]:
    """
    Get information about a specific book.
    
    Args:
        book_id: Book identifier
        
    Returns:
        Book information dictionary or None if not found
    """
    return AVAILABLE_BOOKS.get(book_id)


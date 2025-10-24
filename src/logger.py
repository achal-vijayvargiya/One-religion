"""
Centralized logging configuration for the RAG pipeline.
Provides file-based logging with rotation and configurable levels.
"""

import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        # Set UTF-8 encoding for Windows console
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
    except Exception:
        # Fallback: if that doesn't work, just continue
        pass


class LoggerSetup:
    """Centralized logging configuration."""
    
    _initialized = False
    _log_dir = Path("logs")
    
    @classmethod
    def setup(
        cls,
        log_dir: str = "logs",
        log_level: str = "INFO",
        console_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """
        Setup logging configuration for the application.
        
        Args:
            log_dir: Directory for log files
            log_level: File log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_level: Console log level
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        if cls._initialized:
            return
        
        # Create log directory
        cls._log_dir = Path(log_dir)
        cls._log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # File handler for all logs
        all_logs_file = cls._log_dir / f"rag_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            all_logs_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # File handler for errors only
        error_log_file = cls._log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, console_level.upper()))
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Silence noisy libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("faiss").setLevel(logging.WARNING)
        logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
        
        cls._initialized = True
        
        # Log initialization
        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info(f"Logging initialized - Files in: {cls._log_dir.absolute()}")
        logger.info(f"File log level: {log_level} | Console log level: {console_level}")
        logger.info("=" * 80)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a module.
        
        Args:
            name: Name of the module (typically __name__)
            
        Returns:
            Logger instance
        """
        if not cls._initialized:
            # Initialize with defaults if not already done
            cls.setup()
        
        return logging.getLogger(name)
    
    @classmethod
    def get_log_dir(cls) -> Path:
        """Get the log directory path."""
        return cls._log_dir


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Name of the module (use __name__)
        
    Returns:
        Logger instance
    """
    return LoggerSetup.get_logger(name)


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: Optional[str] = None,
    console_level: Optional[str] = None,
):
    """
    Setup logging with optional custom configuration.
    
    Args:
        log_dir: Directory for log files
        log_level: File log level
        console_level: Console log level
    """
    # Try to import settings
    try:
        from src.config import get_settings
        settings = get_settings()
        
        LoggerSetup.setup(
            log_dir=log_dir or settings.log_dir,
            log_level=log_level or settings.log_level,
            console_level=console_level or settings.console_log_level,
            max_bytes=settings.log_max_bytes,
            backup_count=settings.log_backup_count,
        )
    except Exception:
        # Fallback to defaults if config not available
        LoggerSetup.setup(
            log_dir=log_dir or "logs",
            log_level=log_level or "INFO",
            console_level=console_level or "INFO",
        )


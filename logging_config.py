"""Logging configuration for the project."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path(__file__).resolve().parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "app.log"
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the specified name.
    
    Args:
        name: The name of the logger (typically __name__).
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

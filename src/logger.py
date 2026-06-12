"""Logging configuration for NarrativeWatch AI."""

import logging
import os
from logging.handlers import RotatingFileHandler

try:
    from src.config import get_config
    config = get_config()
except ImportError:
    from config import get_config
    config = get_config()


def setup_logger(name: str) -> logging.Logger:
    """Setup logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(config.LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Create module logger
logger = setup_logger(__name__)

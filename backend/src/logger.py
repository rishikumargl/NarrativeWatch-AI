"""Logging configuration for NarrativeWatch AI."""

import logging
import os
from logging.handlers import RotatingFileHandler

from src.config import config


def setup_logger(name: str) -> logging.Logger:
    """Setup logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


# Create module logger
logger = setup_logger(__name__)

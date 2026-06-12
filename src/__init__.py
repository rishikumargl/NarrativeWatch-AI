"""NarrativeWatch AI - Multi-Agent Social Media Intelligence Platform."""

__version__ = "1.0.0"
__author__ = "NarrativeWatch Team"

from src.config import settings
from src.logger import logger, setup_logger

__all__ = [
    "settings",
    "logger",
    "setup_logger",
]

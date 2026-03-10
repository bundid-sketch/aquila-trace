"""
AquilaTrace - Multi-layered Intelligence Platform for Financial Crime Detection
Version 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AquilaTrace Team"
__description__ = "Advanced ML, Graph Analytics, NLP, and Blockchain Analysis Platform"

from .core.logger import setup_logging
from .core.config import Config

# Initialize logging on import
logger = setup_logging(__name__)

__all__ = [
    "Config",
    "setup_logging",
    "logger",
]

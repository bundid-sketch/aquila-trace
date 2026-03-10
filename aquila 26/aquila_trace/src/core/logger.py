"""Logging configuration for AquilaTrace platform."""

import logging
import logging.handlers
from pathlib import Path
from pythonjsonlogger import jsonlogger
from typing import Optional


def setup_logging(
    name: Optional[str] = None,
    level: str = "INFO",
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """
    Configure logging with both console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name or "aquila_trace")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console Handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        timestamp=True
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler with JSON formatting
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "aquila_trace.log",
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "aquila_trace_errors.log",
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    logger.addHandler(error_handler)
    
    return logger

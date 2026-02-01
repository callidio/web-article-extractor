"""Structured logging configuration for web article extractor."""

import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up structured JSON logger.

    Args:
        name: Logger name
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "web_article_extractor") -> logging.Logger:
    """
    Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

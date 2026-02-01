"""Tests for logger module."""

import logging

from web_article_extractor.logger import get_logger, setup_logger


class TestLogger:
    """Tests for logger module."""

    def test_setup_logger_default_level(self):
        """Test logger setup with default level."""
        logger = setup_logger("test_logger", "INFO")
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logger_debug_level(self):
        """Test logger setup with DEBUG level."""
        logger = setup_logger("test_logger_debug", "DEBUG")
        assert logger.level == logging.DEBUG

    def test_setup_logger_warning_level(self):
        """Test logger setup with WARNING level."""
        logger = setup_logger("test_logger_warning", "WARNING")
        assert logger.level == logging.WARNING

    def test_setup_logger_error_level(self):
        """Test logger setup with ERROR level."""
        logger = setup_logger("test_logger_error", "ERROR")
        assert logger.level == logging.ERROR

    def test_setup_logger_critical_level(self):
        """Test logger setup with CRITICAL level."""
        logger = setup_logger("test_logger_critical", "CRITICAL")
        assert logger.level == logging.CRITICAL

    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test_get_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_get_logger"

    def test_get_logger_default_name(self):
        """Test getting logger with default name."""
        logger = get_logger()
        assert logger.name == "web_article_extractor"

    def test_logger_no_propagation(self):
        """Test that logger doesn't propagate to root."""
        logger = setup_logger("test_no_propagate", "INFO")
        assert logger.propagate is False

    def test_logger_handler_cleared(self):
        """Test that existing handlers are cleared."""
        logger_name = "test_handler_clear"
        logger1 = setup_logger(logger_name, "INFO")
        initial_handlers = len(logger1.handlers)

        logger2 = setup_logger(logger_name, "DEBUG")
        # Should have same number of handlers (old ones cleared)
        assert len(logger2.handlers) == initial_handlers

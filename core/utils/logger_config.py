"""
Centralized logging configuration for the Playwright framework.

Usage:
    1. Configure logging once in conftest.py:
        from core.utils.logger_config import configure_logging
        configure_logging(level=logging.DEBUG, log_to_file=True)
    
    2. Use logger in any module:
        import logging
        logger = logging.getLogger(__name__)
    
    3. Or use the helper function:
        from core.utils.logger_config import get_logger
        logger = get_logger(__name__)

Environment Variables:
    - DEBUG=true/false - Controls log level (DEBUG vs INFO)
    - CI=true/false - Enables file logging in CI environments
"""
import logging
import sys
from pathlib import Path
from typing import Optional

# Default configuration
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
FILE_LOG_FORMAT = "%(asctime)s - %(name)s - [%(levelname)s] - %(funcName)s:%(lineno)d - %(message)s"

# Track if logging is already configured
_logging_configured = False


def configure_logging(
    level: int = DEFAULT_LOG_LEVEL,
    log_to_file: bool = False,
    log_dir: str = DEFAULT_LOG_DIR,
    console_format: Optional[str] = None,
    file_format: Optional[str] = None
) -> None:
    """
    Configure logging for the entire framework.
    Should be called once at the start of test execution (e.g., in conftest.py).
    
    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
        log_to_file: Whether to enable file logging
        log_dir: Directory for log files
        console_format: Custom format for console output
        file_format: Custom format for file output
    """
    global _logging_configured
    
    if _logging_configured:
        return
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        console_format or DEFAULT_LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_path / "test_execution.log",
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            file_format or FILE_LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    
    Example:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)

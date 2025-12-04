"""
VAANI Logging Utility
Centralized logging configuration for VAANI project.

Usage:
    from utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processing request")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def get_logger(name, log_file=None, level=logging.INFO):
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path
        level: Logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_logging(log_dir='logs', level=logging.INFO):
    """
    Setup logging for the entire application.
    
    Args:
        log_dir: Directory for log files
        level: Logging level
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'vaani_{timestamp}.log'
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file


class LoggerMixin:
    """Mixin class to add logging capability to any class."""
    
    @property
    def logger(self):
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


# Example usage
if __name__ == "__main__":
    # Setup logging
    log_file = setup_logging()
    print(f"Logging to: {log_file}")
    
    # Get logger
    logger = get_logger(__name__)
    
    # Test logging
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test LoggerMixin
    class TestClass(LoggerMixin):
        def do_something(self):
            self.logger.info("Doing something")
    
    test = TestClass()
    test.do_something()


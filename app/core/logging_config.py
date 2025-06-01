import logging
import sys
from typing import List, Dict, Any
import os
from pydantic import BaseModel

# Import colorlog for colored terminal output
try:
    import colorlog
    has_colorlog = True
except ImportError:
    has_colorlog = False
    print("For colored logs, install colorlog: pip install colorlog")

class LogConfig(BaseModel):
    """Logging configuration"""
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    USE_COLORS: bool = os.getenv("USE_COLORS", "true").lower() in ("true", "1", "yes")
    LOG_FILE: str = os.getenv("LOG_FILE", "")  # Empty means log to console only

def configure_logging():
    """Configure logging for the application"""
    config = LogConfig()
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.LOG_LEVEL)
    
    # Remove existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Create formatter - use colorlog if available and colors are enabled
    if has_colorlog and config.USE_COLORS:
        # Define color scheme for different log levels
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(color_formatter)
    else:
        # Use standard formatter if colorlog not available
        formatter = logging.Formatter(config.LOG_FORMAT)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handler (if LOG_FILE is specified)
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels if needed
    for logger_name in ["uvicorn", "uvicorn.access"]:
        logging.getLogger(logger_name).handlers = []
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Set some common libraries to WARNING to reduce noise
    for logger_name in ["httpx", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Log the configuration
    logging.info(f"Logging configured with level: {config.LOG_LEVEL}")
    if config.USE_COLORS and has_colorlog:
        logging.info("Using colored log output")
    if config.LOG_FILE:
        logging.info(f"Logging to file: {config.LOG_FILE}")
        
    return root_logger

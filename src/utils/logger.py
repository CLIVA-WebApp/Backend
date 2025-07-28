import logging
import sys
from typing import Any
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/app.log")
    ]
)

logger = logging.getLogger("git-merge-resolver")

def log_info(message: str, **kwargs: Any) -> None:
    """Log info message"""
    logger.info(message, extra=kwargs)

def log_error(message: str, **kwargs: Any) -> None:
    """Log error message"""
    logger.error(message, extra=kwargs)

def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message"""
    logger.warning(message, extra=kwargs)

def log_debug(message: str, **kwargs: Any) -> None:
    """Log debug message"""
    logger.debug(message, extra=kwargs) 
import logging
import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Read the log level from the environment variable (default to INFO if missing)
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Configure the root/base logger format
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance for a given module name."""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger

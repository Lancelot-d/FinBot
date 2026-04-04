"""Logger configuration for the Reddit API service."""

import logging
import os
import sys


def _parse_log_level(level_name: str) -> int:
    """Convert log level string to a logging level constant."""
    return getattr(logging, level_name.upper(), logging.INFO)


LOG_LEVEL = _parse_log_level(os.getenv("LOG_LEVEL", "INFO"))
LOG_FILE = os.getenv("LOG_FILE", "")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """Configure application-wide logging to stdout (Docker-friendly)."""
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    has_stdout_handler = any(
        isinstance(handler, logging.StreamHandler)
        for handler in root_logger.handlers
    )
    if not has_stdout_handler:
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)

    if LOG_FILE:
        has_file_handler = any(
            isinstance(handler, logging.FileHandler)
            and handler.baseFilename.endswith(LOG_FILE)
            for handler in root_logger.handlers
        )
        if not has_file_handler:
            file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)


configure_logging()
logger = logging.getLogger("reddit_api")

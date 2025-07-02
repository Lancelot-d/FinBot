import logging

logger = logging.getLogger("stream_logger")
logger.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    fmt="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M"
)

# File handler
file_handler = logging.FileHandler("app.log", encoding="utf-8", mode="a")
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

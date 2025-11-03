import logging
from pathlib import Path
from typing import Optional


class Log:
    """Simple logging wrapper with optional file output."""

    def __init__(self, log_file: Optional[str] = None):
        log_format = "[%(levelname)s] [%(name)s] %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(file_handler)

    def info(self, class_name: str, message: str):
        logging.getLogger(class_name).info(message)

    def warning(self, class_name: str, message: str):
        logging.getLogger(class_name).warning(message)

    def error(self, class_name: str, message: str):
        logging.getLogger(class_name).error(message)

    def debug(self, class_name: str, message: str):
        logging.getLogger(class_name).debug(message)

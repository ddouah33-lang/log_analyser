"""Configuration des logs : un fichier de log par module (logs/<module>.log)."""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(module_name):
    """Retourne un logger dedie au module (fichier avec rotation + console)."""
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger(module_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter(FORMAT)

    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{module_name}.log"),
        maxBytes=100_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger

"""
Simple logging utility for the Data Insights app.

Provides a single function `get_logger(name, level=logging.INFO, file_path=None)`
that returns a configured logger with a console handler. Optionally writes to a
rotating file if `file_path` is provided.

Usage:
    from utils.logger import get_logger
    logger = get_logger("myagent")
    logger.info("starting up")
"""
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional


def get_logger(name: str = "app", level: int = logging.INFO, file_path: Optional[str] = None) -> logging.Logger:
    """Create or return a logger configured to write to console (and file).

    - Avoids configuring the same logger twice (idempotent).
    - Keeps format simple and human-readable for console output.
    - If file_path is provided, adds a RotatingFileHandler for persisted logs.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    fmt_console = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt_console)
    logger.addHandler(ch)

    if file_path:
        fmt_file = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(module)s:%(lineno)d - %(message)s")
        fh = RotatingFileHandler(file_path, maxBytes=5_000_000, backupCount=3)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt_file)
        logger.addHandler(fh)

    # Prevent messages from being propagated to the root logger twice
    logger.propagate = False
    return logger


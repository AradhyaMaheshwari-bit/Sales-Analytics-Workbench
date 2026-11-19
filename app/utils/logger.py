"""Structured application logging without sensitive data."""

import logging

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure(level: int = logging.INFO) -> logging.Logger:
    """Configure the root logger once at application start."""
    logging.basicConfig(level=level, format=_LOG_FORMAT)
    return logging.getLogger("workbench")


logger = configure()

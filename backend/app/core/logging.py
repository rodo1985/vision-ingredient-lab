"""Logging setup utilities for the backend application."""

import logging
from logging.config import dictConfig


def configure_logging(log_level: str = "INFO") -> None:
    """Configure application logging with a predictable console formatter.

    Parameters:
        log_level: The root log level to apply to the console handler.

    Returns:
        None

    Raises:
        ValueError: If an empty log level is provided.

    Example:
        >>> configure_logging("DEBUG")
    """

    if not log_level:
        raise ValueError("log_level must be a non-empty string")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": log_level.upper(),
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level.upper(),
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger.

    Parameters:
        name: The logger namespace, usually `__name__`.

    Returns:
        logging.Logger: Configured logger instance for the module.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.name == __name__
        True
    """

    return logging.getLogger(name)

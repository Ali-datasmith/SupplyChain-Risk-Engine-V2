"""Loguru telemetry configuration."""
import sys

from loguru import logger


def configure_logging():
    """Configure loguru sinks. Safe to call multiple times."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

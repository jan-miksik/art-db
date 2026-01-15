"""Shared test utilities and helpers."""

from contextlib import contextmanager
import logging


class DummyImage:
    """Mimics the weaviate response object shape"""
    def __init__(self, artwork_id, author_id):
        self.properties = {
            "artwork_psql_id": artwork_id,
            "author_psql_id": author_id,
        }


@contextmanager
def suppress_logger(name, level=logging.CRITICAL):
    """Temporarily raise logger level to suppress noisy logs."""
    logger = logging.getLogger(name)
    previous_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(previous_level)

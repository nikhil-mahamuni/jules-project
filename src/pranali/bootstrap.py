import sys
from src.pranali.logging.setup import setup_logging
from src.pranali.config import settings

def bootstrap():
    """Initialize application dependencies like logging."""
    setup_logging(level=settings.logging.level, json_format=settings.logging.json_format)

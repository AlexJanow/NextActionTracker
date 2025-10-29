"""Structured logging configuration for Next Action Tracker API."""

import os
import sys
import structlog
from structlog.stdlib import LoggerFactory


def setup_logging():
    """Configure structured logging for the application."""
    
    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add timestamp
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            # Add context from request
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # JSON formatting for production, pretty for development
            structlog.dev.ConsoleRenderer() if os.getenv("ENVIRONMENT") == "development" 
            else structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level, logging.INFO),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)


def get_logger(name: str = None):
    """Get a structured logger instance."""
    return structlog.get_logger(name)
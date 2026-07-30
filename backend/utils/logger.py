import logging
import os
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Get a structured logger for the given name.
    Handlers are configured to output cleanly formatted logs to stdout.
    """
    logger = logging.getLogger(name)
    
    # Configure only if it hasn't been configured yet
    if not logger.handlers:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level, logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent double logging
        logger.propagate = False
        
    return logger

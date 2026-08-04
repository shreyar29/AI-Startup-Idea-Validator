import logging
import os
import sys

try:
    from rich.logging import RichHandler
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

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
        
        if RICH_AVAILABLE:
            console = Console(stderr=False)
            handler = RichHandler(
                console=console, 
                show_time=True, 
                show_path=True, 
                rich_tracebacks=True,
                omit_repeated_times=False
            )
            formatter = logging.Formatter("%(message)s")
        else:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler.setLevel(getattr(logging, log_level, logging.INFO))
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Add FileHandler for SSE streaming
        try:
            file_handler = logging.FileHandler("validation.log", mode="a", encoding="utf-8")
            file_formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            logger.addHandler(file_handler)
        except Exception:
            pass
        
        # Prevent double logging
        logger.propagate = False
        
    return logger

import logging

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given name.
    Handlers are expected to be configured once at the application entry point
    (e.g., via logging.basicConfig) to prevent duplicate log entries.
    """
    return logging.getLogger(name)

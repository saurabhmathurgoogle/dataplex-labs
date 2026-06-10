import logging
import sys

_logger = None

def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger
    _logger = logging.getLogger("glossary_migration")
    _logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stdout_handler.setFormatter(formatter)
    _logger.addHandler(stdout_handler)
    _logger.propagate = False
    return _logger

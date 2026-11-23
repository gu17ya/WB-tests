import logging

from utils.environment import get_string_environment


def get_logger(name: str) -> logging.Logger:
    """Output and format are handled by pytest (see pytest.ini), so logs land in the HTML report."""
    logger = logging.getLogger(name)
    logger.setLevel(get_string_environment("LOG_LEVEL", required=False, default="INFO"))
    return logger

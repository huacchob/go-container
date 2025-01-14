"""Utility functions"""

import logging
import os
from glob import glob
from logging import Logger, StreamHandler
from typing import List, Optional, TextIO

from dotenv import load_dotenv


def find_file_path(
    target_file_name: str,
    source_file_name: str,
) -> str:
    """Find the path to the file.

    Args:
        target_file_name (str): The name of the target file.
        source_file_name (Optional[str  |  None], optional):
            name of the file you are using this function in. Defaults to None.

    Raises:
        ValueError: Source file name is not specified
        ValueError: File `target_file_name` exists in multiple directories
        ValueError: File `target_file_name` not found

    Returns:
        Optional[str | None]: The path to the file or None if not found
    """
    if not source_file_name:
        raise ValueError("Source file name is not specified")

    globs: List[str] = glob(pathname=f"**/{target_file_name}", recursive=True)
    if len(globs) == 1:
        return globs[0]
    elif len(globs) > 1:
        raise ValueError(
            f"File {target_file_name} exists in multiple directories",
        )
    else:
        raise ValueError(f"File {target_file_name} not found")


def load_secrets_from_file(
    target_file_name: str,
    source_file_name: str,
) -> None:
    """Load secrets from .env file

    Args:
        target_file_name (str): The name of the target file.
        source_file_name (Optional[str  |  None]):
            name of the file you are using this function in. Defaults to None.

    Raises:
        ValueError: File name must end with .env
        ValueError: File `target_file_name` not found
    """
    if not target_file_name.endswith(".env"):
        raise ValueError("File name must end with .env")
    dotenv_path: Optional[str] = find_file_path(
        target_file_name=target_file_name,
        source_file_name=source_file_name,
    )
    load_dotenv(dotenv_path=dotenv_path)


def get_secret(secret_name: str) -> str:
    """Get secret from environment

    Args:
        secret_name (str): The name of the secret.

    Raises:
        ValueError: Secret `secret_name` not found

    Returns:
        str: The value of the secret
    """
    secret_value: Optional[str | None] = os.environ.get(
        secret_name,
        default=None,
    )
    if not secret_value:
        raise ValueError(f"Secret {secret_name} not found")
    return secret_value


def configure_logger(name: str, logger_level_str: str = "DEFAULT") -> Logger:
    """Create logger

    Args:
        name (str): The name of the file you are using this function in.
            Pass __name__ to get the name of the file you are using
            this function in.
        logger_level_str (str): The level of the logger.

    Raises:
        ValueError: Invalid logging level

    Returns:
        logger (Logger): The logger
    """
    logger_level: str = logger_level_str.upper()
    if logger_level not in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "DEFAULT",
    ]:
        raise ValueError("Invalid logging level")

    logger_mappings: dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "DEFAULT": logging.INFO,
    }
    level: int = logger_mappings[logger_level]

    logger: Logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    console_handler: StreamHandler[TextIO] = StreamHandler()
    console_handler.setLevel(level=logging.INFO)

    logger.addHandler(hdlr=console_handler)

    return logger

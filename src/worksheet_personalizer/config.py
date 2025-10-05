"""Configuration and constants for worksheet personalization.

This module defines configuration settings, constants, and logging setup
for the worksheet personalizer application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Physical constants for layout
PHOTO_SIZE_CM: float = 1.5  # Photo size (long side) in centimeters
PHOTO_MARGIN_CM: float = 0.5  # Margin from top-right corner in centimeters

# DPI settings for different formats
DPI_PDF: int = 72  # Standard PDF DPI (PostScript points)
DPI_IMAGE: int = 300  # High-quality image DPI

# Font settings
FONT_NAME: str = "Helvetica"  # Default font for PDF text
FONT_SIZE: int = 12  # Default font size in points

# Default output directory
DEFAULT_OUTPUT_DIR: str = "./output"


class Settings(BaseSettings):
    """Application settings with environment variable support.

    Settings can be overridden via environment variables with the prefix
    WORKSHEET_. For example: WORKSHEET_OUTPUT_DIR=/path/to/output

    Attributes:
        output_dir: Default output directory for personalized worksheets
        photo_size_cm: Photo size (long side) in centimeters
        photo_margin_cm: Margin from top-right corner in centimeters
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        add_name_default: Whether to add student names by default
    """

    model_config = SettingsConfigDict(
        env_prefix="WORKSHEET_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    output_dir: Path = Field(default=Path(DEFAULT_OUTPUT_DIR))
    photo_size_cm: float = Field(default=PHOTO_SIZE_CM, gt=0, le=10)
    photo_margin_cm: float = Field(default=PHOTO_MARGIN_CM, ge=0, le=5)
    log_level: str = Field(default="INFO")
    add_name_default: bool = Field(default=False)


def setup_logging(level: Optional[str] = None) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               If None, uses the level from Settings.

    Example:
        >>> setup_logging("DEBUG")
        >>> logging.info("This is an info message")
    """
    if level is None:
        settings = Settings()
        level = settings.log_level

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("reportlab").setLevel(logging.WARNING)


def get_settings() -> Settings:
    """Get the application settings instance.

    Returns:
        Settings instance with values from environment variables or defaults
    """
    return Settings()

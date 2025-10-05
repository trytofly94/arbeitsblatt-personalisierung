"""Image processing for worksheet personalization.

This module handles image-format worksheet personalization using Pillow (PIL)
for image manipulation and compositing.
"""

import logging
from pathlib import Path
from typing import Any, Union

from PIL import Image
from PIL.ImageFont import FreeTypeFont
from PIL.ImageFont import ImageFont as ImageFontType

from worksheet_personalizer.config import (
    DPI_IMAGE,
    FONT_SIZE,
    PHOTO_MARGIN_CM,
    PHOTO_SIZE_CM,
)
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.utils.image_utils import (
    cm_to_pixels,
    ensure_rgb,
    render_text_on_image,
    scale_photo,
)

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles personalization of image worksheets with student photos and names.

    This class creates personalized image worksheets by compositing student photos
    (and optionally names) onto the original worksheet image.

    Attributes:
        worksheet_path: Path to the original worksheet image
        add_name: Whether to include student name alongside photo
    """

    # Supported image formats
    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg"}

    def __init__(self, worksheet_path: Path, add_name: bool = False) -> None:
        """Initialize image processor.

        Args:
            worksheet_path: Path to the original worksheet image
            add_name: Whether to add student name to the worksheet

        Raises:
            FileNotFoundError: If worksheet file doesn't exist
            ValueError: If file is not a supported image format
        """
        if not worksheet_path.exists():
            raise FileNotFoundError(f"Worksheet file not found: {worksheet_path}")

        if worksheet_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {worksheet_path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        self.worksheet_path = worksheet_path
        self.add_name = add_name

        logger.info(f"Initialized image processor for: {worksheet_path.name}")

    def _load_worksheet(self) -> Image.Image:
        """Load the worksheet image and preserve DPI information.

        Returns:
            PIL Image object of the worksheet

        Raises:
            ValueError: If image cannot be loaded
        """
        try:
            worksheet = Image.open(self.worksheet_path)

            # Store original DPI if available
            dpi = worksheet.info.get("dpi", (DPI_IMAGE, DPI_IMAGE))
            if isinstance(dpi, tuple):
                self._worksheet_dpi = int(dpi[0])
            else:
                self._worksheet_dpi = DPI_IMAGE

            logger.debug(
                f"Loaded worksheet: {worksheet.size[0]}x{worksheet.size[1]} pixels, "
                f"DPI: {self._worksheet_dpi}"
            )

            return worksheet

        except Exception as e:
            raise ValueError(f"Error loading worksheet image: {e}") from e

    def personalize_for_student(self, student: Student, output_path: Path) -> None:
        """Create a personalized worksheet for a specific student.

        Args:
            student: Student object with name and photo
            output_path: Path where the personalized image will be saved

        Raises:
            ValueError: If personalization fails
            IOError: If file cannot be written
        """
        logger.info(f"Personalizing worksheet for: {student.name}")

        try:
            # Load worksheet
            worksheet = self._load_worksheet()
            worksheet = ensure_rgb(worksheet)  # Ensure RGB mode for compositing

            # Load and process student photo
            photo = Image.open(student.photo_path)
            photo = ensure_rgb(photo)
            photo = scale_photo(photo, PHOTO_SIZE_CM, self._worksheet_dpi)

            # Calculate position (top-right with margin)
            margin_pixels = cm_to_pixels(PHOTO_MARGIN_CM, self._worksheet_dpi)
            photo_width, photo_height = photo.size
            worksheet_width, worksheet_height = worksheet.size

            x_position = worksheet_width - photo_width - margin_pixels
            y_position = margin_pixels

            # Paste photo onto worksheet
            worksheet.paste(photo, (x_position, y_position))

            logger.debug(
                f"Pasted photo at position ({x_position}, {y_position}), "
                f"size {photo_width}x{photo_height} pixels"
            )

            # Add student name if requested
            if self.add_name:
                # Calculate name position (to the left of the photo)
                name_margin = 10  # Small margin from photo edge
                name_x = x_position - name_margin
                name_y = y_position + (photo_height // 2)

                # Scale font size based on DPI
                scaled_font_size = int(FONT_SIZE * (self._worksheet_dpi / 72))

                # Render text (right-aligned to align with photo)
                # Note: We'll position the text and then right-align it manually
                # by calculating text width
                from PIL import ImageDraw, ImageFont

                # Create a temporary draw object to measure text
                draw = ImageDraw.Draw(worksheet)
                font: Union[FreeTypeFont, ImageFontType]
                try:
                    font = ImageFont.truetype("Arial.ttf", scaled_font_size)
                except OSError:
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", scaled_font_size)
                    except OSError:
                        font = ImageFont.load_default()
                        logger.warning("Using default font for name rendering")

                # Get text bounding box to calculate width
                bbox = draw.textbbox((0, 0), student.name, font=font)
                text_width = bbox[2] - bbox[0]

                # Adjust x position for right alignment
                text_x = name_x - text_width

                # Render the name
                render_text_on_image(
                    worksheet,
                    student.name,
                    (text_x, name_y),
                    font_size=scaled_font_size,
                )

                logger.debug(
                    f"Added name '{student.name}' at position ({text_x}, {name_y})"
                )

            # Save the personalized worksheet
            # Preserve original format and DPI
            save_kwargs: dict[str, Any] = {
                "dpi": (self._worksheet_dpi, self._worksheet_dpi)
            }

            # Determine output format from extension
            output_format = output_path.suffix.lower().replace(".", "").upper()
            if output_format == "JPG":
                output_format = "JPEG"

            worksheet.save(output_path, format=output_format, **save_kwargs)

            logger.info(f"Created personalized image: {output_path}")

        except Exception as e:
            raise ValueError(
                f"Error personalizing worksheet for {student.name}: {e}"
            ) from e

"""PDF processing for worksheet personalization.

This module handles PDF-specific worksheet personalization using PyPDF2
for reading/writing PDFs and reportlab for creating overlays.
"""

import io
import logging
from pathlib import Path
from typing import Literal

from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from worksheet_personalizer.config import (
    A4_HEIGHT_CM,
    A4_WIDTH_CM,
    DPI_PDF,
    PHOTO_SIZE_CM,
)
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.settings_manager import SettingsManager
from worksheet_personalizer.utils.image_utils import (
    cm_to_pixels,
    ensure_rgb,
    scale_photo,
)

logger = logging.getLogger(__name__)

NamePosition = Literal["beside_photo", "center", "left", "right"]

# Register Norddruck font
_NORDDRUCK_REGISTERED = False

def _register_norddruck_font() -> str:
    """Register Norddruck font with ReportLab.

    Returns:
        Font name to use ('Norddruck' or 'Helvetica' as fallback)
    """
    global _NORDDRUCK_REGISTERED

    if _NORDDRUCK_REGISTERED:
        return 'Norddruck'

    try:
        # Get path to font file in package
        font_path = Path(__file__).parent.parent / "fonts" / "NORDDRUC.TTF"

        if font_path.exists():
            pdfmetrics.registerFont(TTFont('Norddruck', str(font_path)))
            _NORDDRUCK_REGISTERED = True
            logger.info("Norddruck font registered successfully")
            return 'Norddruck'
        else:
            logger.warning(f"Norddruck font not found at {font_path}, using Helvetica")
            return 'Helvetica'
    except Exception as e:
        logger.warning(f"Could not register Norddruck font: {e}, using Helvetica")
        return 'Helvetica'


class PDFProcessor:
    """Handles personalization of PDF worksheets with student photos and names.

    This class creates personalized PDF worksheets by overlaying student photos
    (and optionally names) on the original worksheet PDF.

    Attributes:
        worksheet_path: Path to the original worksheet PDF
        add_name: Whether to include student name alongside photo
    """

    def __init__(self, worksheet_path: Path, add_name: bool = False) -> None:
        """Initialize PDF processor.

        Args:
            worksheet_path: Path to the original worksheet PDF
            add_name: Whether to add student name to the worksheet

        Raises:
            FileNotFoundError: If worksheet file doesn't exist
            ValueError: If file is not a valid PDF
        """
        if not worksheet_path.exists():
            raise FileNotFoundError(f"Worksheet file not found: {worksheet_path}")

        if worksheet_path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {worksheet_path}")

        self.worksheet_path = worksheet_path
        self.add_name = add_name

        # Register and get font name
        self.font_name = _register_norddruck_font()

        # Load settings from settings manager
        self.settings_manager = SettingsManager()
        self.photo_size_cm = self.settings_manager.get("photo_size_cm", PHOTO_SIZE_CM)

        # Get font_size from settings or calculate dynamically
        self.font_size = self.settings_manager.get("font_size", None)
        self.name_position: NamePosition = self.settings_manager.get("name_position", "beside_photo")

        logger.info(f"Initialized PDF processor for: {worksheet_path.name}")
        logger.debug(f"Settings: font={self.font_name}, photo_size={self.photo_size_cm}cm, "
                    f"font_size={'dynamic' if self.font_size is None else self.font_size}, "
                    f"name_position={self.name_position}")

    def _get_page_dimensions(self) -> tuple[float, float]:
        """Get the dimensions of the first page in the PDF.

        Returns:
            Tuple of (width, height) in points

        Raises:
            ValueError: If PDF cannot be read or has no pages
        """
        try:
            reader = PdfReader(str(self.worksheet_path))

            if len(reader.pages) == 0:
                raise ValueError("PDF has no pages")

            page = reader.pages[0]
            mediabox = page.mediabox

            width = float(mediabox.width)
            height = float(mediabox.height)

            logger.debug(f"PDF page dimensions: {width}x{height} points")
            return width, height

        except Exception as e:
            raise ValueError(f"Error reading PDF dimensions: {e}") from e

    def _calculate_a4_dpi(self) -> float:
        """Calculate the effective DPI of the PDF assuming A4 print size.

        This ensures consistent photo sizing regardless of PDF resolution.
        The calculation assumes the PDF will be printed on DIN A4 paper.

        Returns:
            Effective DPI for the PDF based on A4 dimensions

        Example:
            If PDF is 595x842 points and A4 is 21x29.7 cm:
            DPI = 595 / (21 / 2.54) = 72 (standard PDF DPI)
        """
        page_width, page_height = self._get_page_dimensions()

        # Convert A4 dimensions from cm to inches
        a4_width_inches = A4_WIDTH_CM / 2.54
        a4_height_inches = A4_HEIGHT_CM / 2.54

        # Calculate DPI based on width (more reliable than height)
        effective_dpi = page_width / a4_width_inches

        logger.debug(
            f"Calculated effective DPI: {effective_dpi:.1f} "
            f"(page width: {page_width} points, A4 width: {a4_width_inches:.2f} inches)"
        )

        return effective_dpi

    def _create_overlay(self, student: Student) -> io.BytesIO:
        """Create a PDF overlay with student photo and optional name.

        Args:
            student: Student object with name and photo path

        Returns:
            BytesIO buffer containing the overlay PDF

        Raises:
            ValueError: If photo cannot be processed
        """
        # Get page dimensions
        page_width, page_height = self._get_page_dimensions()

        # Calculate effective DPI for A4 print size
        effective_dpi = self._calculate_a4_dpi()

        # Calculate dynamic font size if not set (2.25% of PDF height)
        font_size = self.font_size if self.font_size is not None else page_height * 0.0225

        # Calculate dynamic margins proportional to page size
        margin_right = page_width * 0.035   # ~3.5% of width
        margin_top = page_height * 0.025    # ~2.5% of height

        # Create a buffer for the overlay PDF
        buffer = io.BytesIO()

        # Create canvas for drawing
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        try:
            # Load and process student photo
            photo = Image.open(student.photo_path)
            photo = ensure_rgb(photo)  # Convert to RGB if needed
            photo = scale_photo(photo, self.photo_size_cm, effective_dpi)

            # Convert photo to ReportLab ImageReader
            photo_buffer = io.BytesIO()
            photo.save(photo_buffer, format="JPEG")
            photo_buffer.seek(0)
            photo_reader = ImageReader(photo_buffer)

            # Calculate position (top-right with dynamic margin)
            photo_width, photo_height = photo.size

            x_position = page_width - photo_width - margin_right
            y_position = page_height - photo_height - margin_top

            # Draw photo
            c.drawImage(
                photo_reader,
                x_position,
                y_position,
                width=photo_width,
                height=photo_height,
                preserveAspectRatio=True,
            )

            logger.debug(
                f"Added photo at position ({x_position:.1f}, {y_position:.1f}), "
                f"size {photo_width}x{photo_height} points"
            )

            # Add student name if requested
            if self.add_name:
                c.setFont(self.font_name, font_size)

                # Calculate dynamic gap between name and photo (1.3% of width)
                text_photo_gap = page_width * 0.013

                if self.name_position == "beside_photo":
                    # Position name to the left of the photo with dynamic formatting
                    text = f"Name: {student.name}"
                    text_width = c.stringWidth(text, self.font_name, font_size)

                    # Calculate name position, ensuring it doesn't go off the left edge
                    name_x = x_position - text_width - text_photo_gap
                    # Ensure minimum margin on the left (3.5% like margin_right)
                    min_x = page_width * 0.035
                    name_x = max(name_x, min_x)

                    name_y = y_position + (photo_height / 2) - (font_size / 3)
                    c.drawString(name_x, name_y, text)

                elif self.name_position == "center":
                    # Center of the page
                    name_x = page_width / 2
                    name_y = page_height - margin_top - (font_size / 2)
                    c.drawCentredString(name_x, name_y, student.name)

                elif self.name_position == "left":
                    # Left side of the page
                    name_x = margin_right
                    name_y = page_height - margin_top - (font_size / 2)
                    c.drawString(name_x, name_y, student.name)

                elif self.name_position == "right":
                    # Right side of the page (above photo)
                    name_x = page_width - margin_right
                    name_y = y_position - font_size - text_photo_gap
                    c.drawRightString(name_x, name_y, student.name)

                logger.debug(
                    f"Added name '{student.name}' at position {self.name_position}"
                )

            # Finalize the canvas
            c.save()

            # Reset buffer position
            buffer.seek(0)

            return buffer

        except Exception as e:
            raise ValueError(f"Error creating overlay for {student.name}: {e}") from e

    def personalize_for_student(self, student: Student, output_path: Path) -> None:
        """Create a personalized worksheet for a specific student.

        Args:
            student: Student object with name and photo
            output_path: Path where the personalized PDF will be saved

        Raises:
            ValueError: If personalization fails
            IOError: If file cannot be written
        """
        logger.info(f"Personalizing worksheet for: {student.name}")

        try:
            # Read original PDF
            reader = PdfReader(str(self.worksheet_path))
            writer = PdfWriter()

            # Create overlay
            overlay_buffer = self._create_overlay(student)
            overlay_reader = PdfReader(overlay_buffer)
            overlay_page = overlay_reader.pages[0]

            # Merge overlay with each page of the original PDF
            for page_num, page in enumerate(reader.pages):
                # Merge overlay with the page
                page.merge_page(overlay_page)
                writer.add_page(page)

                logger.debug(f"Processed page {page_num + 1}/{len(reader.pages)}")

            # Write output PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            logger.info(f"Created personalized PDF: {output_path}")

        except Exception as e:
            raise ValueError(
                f"Error personalizing worksheet for {student.name}: {e}"
            ) from e

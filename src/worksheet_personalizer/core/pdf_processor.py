"""PDF processing for worksheet personalization.

This module handles PDF-specific worksheet personalization using PyPDF2
for reading/writing PDFs and reportlab for creating overlays.
"""

import io
import logging
from pathlib import Path

from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from worksheet_personalizer.config import (
    DPI_PDF,
    FONT_NAME,
    FONT_SIZE,
    PHOTO_MARGIN_CM,
    PHOTO_SIZE_CM,
)
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.utils.image_utils import cm_to_pixels, ensure_rgb, scale_photo

logger = logging.getLogger(__name__)


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

        logger.info(f"Initialized PDF processor for: {worksheet_path.name}")

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

        # Create a buffer for the overlay PDF
        buffer = io.BytesIO()

        # Create canvas for drawing
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        try:
            # Load and process student photo
            photo = Image.open(student.photo_path)
            photo = ensure_rgb(photo)  # Convert to RGB if needed
            photo = scale_photo(photo, PHOTO_SIZE_CM, DPI_PDF)

            # Convert photo to ReportLab ImageReader
            photo_buffer = io.BytesIO()
            photo.save(photo_buffer, format="JPEG")
            photo_buffer.seek(0)
            photo_reader = ImageReader(photo_buffer)

            # Calculate position (top-right with margin)
            margin_points = cm_to_pixels(PHOTO_MARGIN_CM, DPI_PDF)
            photo_width, photo_height = photo.size

            x_position = page_width - photo_width - margin_points
            y_position = page_height - photo_height - margin_points

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
                # Position name to the left of the photo
                name_x = x_position - 5  # 5 points margin from photo
                name_y = y_position + (photo_height / 2) - (FONT_SIZE / 2)

                c.setFont(FONT_NAME, FONT_SIZE)
                c.drawRightString(name_x, name_y, student.name)

                logger.debug(f"Added name '{student.name}' at position ({name_x:.1f}, {name_y:.1f})")

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

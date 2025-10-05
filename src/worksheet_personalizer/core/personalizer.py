"""Worksheet personalization orchestration.

This module provides the main WorksheetPersonalizer class that orchestrates
the entire personalization process, handling both PDF and image formats.
"""

import logging
from pathlib import Path
from typing import Union

from worksheet_personalizer.core.image_processor import ImageProcessor
from worksheet_personalizer.core.pdf_processor import PDFProcessor
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.utils.file_handler import (
    discover_student_photos,
    ensure_output_dir,
    generate_output_filename,
)

logger = logging.getLogger(__name__)


class WorksheetPersonalizer:
    """Orchestrates the worksheet personalization process.

    This class handles the complete workflow of personalizing worksheets:
    - Detecting the input format (PDF or image)
    - Discovering student photos
    - Creating personalized worksheets for all students
    - Managing output directory

    Attributes:
        worksheet_path: Path to the worksheet file
        students_folder: Path to folder containing student photos
        output_folder: Path to output directory
        add_name: Whether to add student names to worksheets
    """

    def __init__(
        self,
        worksheet_path: Path,
        students_folder: Path,
        output_folder: Path,
        add_name: bool = False,
    ) -> None:
        """Initialize the worksheet personalizer.

        Args:
            worksheet_path: Path to the worksheet file (PDF or image)
            students_folder: Path to folder containing student photos
            output_folder: Path where personalized worksheets will be saved
            add_name: Whether to add student names to worksheets

        Raises:
            FileNotFoundError: If worksheet or students folder doesn't exist
            ValueError: If worksheet format is not supported
        """
        if not worksheet_path.exists():
            raise FileNotFoundError(f"Worksheet file not found: {worksheet_path}")

        if not students_folder.exists():
            raise FileNotFoundError(f"Students folder not found: {students_folder}")

        self.worksheet_path = worksheet_path
        self.students_folder = students_folder
        self.output_folder = output_folder
        self.add_name = add_name

        # Detect format and create appropriate processor
        self.format = self._detect_format()
        self.processor = self._get_processor()

        logger.info(
            f"Initialized WorksheetPersonalizer: "
            f"format={self.format}, add_name={add_name}"
        )

    def _detect_format(self) -> str:
        """Detect the worksheet format based on file extension.

        Returns:
            Format string: "pdf" or "image"

        Raises:
            ValueError: If format is not supported
        """
        extension = self.worksheet_path.suffix.lower()

        if extension == ".pdf":
            return "pdf"
        elif extension in {".png", ".jpg", ".jpeg"}:
            return "image"
        else:
            raise ValueError(
                f"Unsupported worksheet format: {extension}. "
                f"Supported formats: .pdf, .png, .jpg, .jpeg"
            )

    def _get_processor(self) -> Union[PDFProcessor, ImageProcessor]:
        """Get the appropriate processor based on detected format.

        Returns:
            PDFProcessor or ImageProcessor instance

        Raises:
            ValueError: If format is invalid
        """
        if self.format == "pdf":
            return PDFProcessor(self.worksheet_path, self.add_name)
        elif self.format == "image":
            return ImageProcessor(self.worksheet_path, self.add_name)
        else:
            raise ValueError(f"Invalid format: {self.format}")

    def process_all(self) -> list[Path]:
        """Process worksheets for all students in the folder.

        This method:
        1. Discovers all student photos in the students folder
        2. Ensures the output directory exists
        3. Creates a personalized worksheet for each student
        4. Returns the list of created files

        Returns:
            List of paths to created personalized worksheets

        Raises:
            ValueError: If no students found or processing fails
            IOError: If files cannot be written
        """
        logger.info("Starting batch personalization process")

        # Discover students
        students = discover_student_photos(self.students_folder)
        logger.info(f"Found {len(students)} student(s) to process")

        # Ensure output directory exists
        ensure_output_dir(self.output_folder)

        # Process each student
        created_files: list[Path] = []
        errors: list[tuple[Student, Exception]] = []

        for i, student in enumerate(students, 1):
            try:
                logger.info(f"Processing {i}/{len(students)}: {student.name}")

                # Generate output filename
                output_path = generate_output_filename(
                    self.worksheet_path, student.name, self.output_folder
                )

                # Personalize worksheet
                self.processor.personalize_for_student(student, output_path)

                created_files.append(output_path)
                logger.info(f"✓ Successfully created: {output_path.name}")

            except Exception as e:
                logger.error(f"✗ Error processing {student.name}: {e}")
                errors.append((student, e))
                continue

        # Summary
        logger.info(
            f"\nPersonalization complete: {len(created_files)} successful, "
            f"{len(errors)} failed"
        )

        if errors:
            logger.warning("\nFailed students:")
            for student, error in errors:
                logger.warning(f"  - {student.name}: {error}")

        if not created_files:
            raise ValueError("No worksheets were successfully created")

        return created_files

    def process_single(self, student: Student) -> Path:
        """Process worksheet for a single student.

        Args:
            student: Student object with name and photo path

        Returns:
            Path to the created personalized worksheet

        Raises:
            ValueError: If processing fails
        """
        logger.info(f"Processing single student: {student.name}")

        # Ensure output directory exists
        ensure_output_dir(self.output_folder)

        # Generate output filename
        output_path = generate_output_filename(
            self.worksheet_path, student.name, self.output_folder
        )

        # Personalize worksheet
        self.processor.personalize_for_student(student, output_path)

        logger.info(f"Created: {output_path}")
        return output_path

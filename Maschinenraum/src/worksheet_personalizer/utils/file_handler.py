"""File handling utilities for worksheet personalization.

This module provides functions for discovering student photos and managing
output directories.
"""

import logging
from pathlib import Path

from worksheet_personalizer.models.student import Student

logger = logging.getLogger(__name__)


def discover_student_photos(folder: Path) -> list[Student]:
    """Discover and create Student objects from photos in a folder.

    Scans the given folder for image files (jpg, jpeg, png) and creates
    a Student object for each file. Student names are extracted from
    filenames (without extension, underscores replaced with spaces).

    Args:
        folder: Path to folder containing student photos

    Returns:
        List of Student objects, sorted by name

    Raises:
        FileNotFoundError: If the folder doesn't exist
        ValueError: If no valid student photos are found

    Example:
        >>> students = discover_student_photos(Path("./students"))
        >>> len(students)
        3
        >>> students[0].name
        'anna schmidt'
    """
    if not folder.exists():
        raise FileNotFoundError(f"Students folder does not exist: {folder}")

    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")

    # Find all image files
    image_extensions = Student.ALLOWED_EXTENSIONS
    photo_files: list[Path] = []

    for ext in image_extensions:
        # Search for files with each extension (case-insensitive)
        photo_files.extend(folder.glob(f"*{ext}"))
        photo_files.extend(folder.glob(f"*{ext.upper()}"))

    if not photo_files:
        raise ValueError(
            f"No valid student photos found in {folder}. "
            f"Expected formats: {', '.join(image_extensions)}"
        )

    # Create Student objects
    students: list[Student] = []
    for photo_path in photo_files:
        try:
            student = Student.from_photo_path(photo_path)
            students.append(student)
            logger.debug(f"Discovered student: {student.name} ({photo_path.name})")
        except ValueError as e:
            logger.warning(f"Skipping invalid photo {photo_path.name}: {e}")
            continue

    if not students:
        raise ValueError(f"No valid student photos could be loaded from {folder}")

    # Sort by name for consistent processing order
    students.sort(key=lambda s: s.name.lower())

    logger.info(f"Discovered {len(students)} student(s) in {folder}")
    return students


def ensure_output_dir(path: Path) -> None:
    """Ensure that an output directory exists, creating it if necessary.

    Args:
        path: Path to the output directory

    Raises:
        ValueError: If path exists but is not a directory
        PermissionError: If directory cannot be created

    Example:
        >>> ensure_output_dir(Path("./output"))
        >>> Path("./output").exists()
        True
    """
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"Output path exists but is not a directory: {path}")
        logger.debug(f"Output directory already exists: {path}")
    else:
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {path}")
        except PermissionError as e:
            raise PermissionError(f"Cannot create output directory {path}: {e}") from e


def generate_output_filename(
    worksheet_path: Path, student_name: str, output_dir: Path
) -> Path:
    """Generate output filename for a personalized worksheet.

    The output filename follows the pattern:
    [original_name]_[student_name].[extension]

    Args:
        worksheet_path: Path to the original worksheet
        student_name: Name of the student
        output_dir: Directory where the output file will be saved

    Returns:
        Full path to the output file

    Example:
        >>> path = generate_output_filename(
        ...     Path("math_test.pdf"),
        ...     "max mustermann",
        ...     Path("./output")
        ... )
        >>> path.name
        'math_test_max_mustermann.pdf'
    """
    # Get original filename without extension
    original_name = worksheet_path.stem

    # Convert student name to filename-safe format (spaces to underscores)
    safe_student_name = student_name.replace(" ", "_").lower()

    # Get file extension
    extension = worksheet_path.suffix

    # Construct output filename
    output_filename = f"{original_name}_{safe_student_name}{extension}"

    return output_dir / output_filename

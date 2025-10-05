"""Tests for image processor."""

from pathlib import Path

import pytest
from PIL import Image

from worksheet_personalizer.core.image_processor import ImageProcessor
from worksheet_personalizer.models.student import Student


def test_image_processor_initialization(sample_worksheet_image: Path) -> None:
    """Test initializing image processor."""
    processor = ImageProcessor(sample_worksheet_image, add_name=False)

    assert processor.worksheet_path == sample_worksheet_image
    assert processor.add_name is False


def test_image_processor_initialization_with_name(sample_worksheet_image: Path) -> None:
    """Test initializing image processor with add_name option."""
    processor = ImageProcessor(sample_worksheet_image, add_name=True)

    assert processor.add_name is True


def test_image_processor_nonexistent_file(temp_dir: Path) -> None:
    """Test that error is raised for non-existent image file."""
    nonexistent = temp_dir / "nonexistent.png"

    with pytest.raises(FileNotFoundError):
        ImageProcessor(nonexistent)


def test_image_processor_unsupported_format(temp_dir: Path) -> None:
    """Test that error is raised for unsupported image format."""
    pdf_file = temp_dir / "file.pdf"
    pdf_file.write_bytes(b"fake pdf")

    with pytest.raises(ValueError, match="Unsupported image format"):
        ImageProcessor(pdf_file)


def test_image_processor_load_worksheet(sample_worksheet_image: Path) -> None:
    """Test loading worksheet image."""
    processor = ImageProcessor(sample_worksheet_image)

    worksheet = processor._load_worksheet()

    assert isinstance(worksheet, Image.Image)
    assert worksheet.size == (800, 1000)


def test_image_processor_personalize_for_student(
    sample_worksheet_image: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test personalizing image for a student."""
    processor = ImageProcessor(sample_worksheet_image, add_name=False)
    student = Student.from_photo_path(sample_student_photo)
    output_path = output_dir / "personalized.png"

    # Personalize the worksheet
    processor.personalize_for_student(student, output_path)

    # Check that output file was created
    assert output_path.exists()
    assert output_path.suffix == ".png"

    # Check that output is a valid image
    img = Image.open(output_path)
    assert img.size == (800, 1000)  # Same dimensions as original


def test_image_processor_personalize_with_name(
    sample_worksheet_image: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test personalizing image with student name."""
    processor = ImageProcessor(sample_worksheet_image, add_name=True)
    student = Student.from_photo_path(sample_student_photo)
    output_path = output_dir / "personalized_with_name.png"

    # Personalize the worksheet
    processor.personalize_for_student(student, output_path)

    # Check that output file was created
    assert output_path.exists()

    # Check that output is a valid image
    img = Image.open(output_path)
    assert img.size == (800, 1000)


def test_image_processor_preserves_dimensions(
    sample_worksheet_image: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test that image processor preserves worksheet dimensions."""
    processor = ImageProcessor(sample_worksheet_image)
    student = Student.from_photo_path(sample_student_photo)
    output_path = output_dir / "output.png"

    # Get original dimensions
    original_img = Image.open(sample_worksheet_image)
    original_size = original_img.size

    # Personalize
    processor.personalize_for_student(student, output_path)

    # Check dimensions are preserved
    output_img = Image.open(output_path)
    assert output_img.size == original_size


def test_image_processor_different_formats(
    sample_worksheet_image: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test that processor can save in different formats."""
    processor = ImageProcessor(sample_worksheet_image)
    student = Student.from_photo_path(sample_student_photo)

    # Save as JPG
    jpg_output = output_dir / "output.jpg"
    processor.personalize_for_student(student, jpg_output)
    assert jpg_output.exists()

    # Verify it's a valid JPG
    img = Image.open(jpg_output)
    assert img.format == "JPEG"

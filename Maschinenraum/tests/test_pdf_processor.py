"""Tests for PDF processor."""

from pathlib import Path

import pytest
from PyPDF2 import PdfReader

from worksheet_personalizer.core.pdf_processor import PDFProcessor
from worksheet_personalizer.models.student import Student


def test_pdf_processor_initialization(sample_worksheet_pdf: Path) -> None:
    """Test initializing PDF processor."""
    processor = PDFProcessor(sample_worksheet_pdf, add_name=False)

    assert processor.worksheet_path == sample_worksheet_pdf
    assert processor.add_name is False


def test_pdf_processor_initialization_with_name(sample_worksheet_pdf: Path) -> None:
    """Test initializing PDF processor with add_name option."""
    processor = PDFProcessor(sample_worksheet_pdf, add_name=True)

    assert processor.add_name is True


def test_pdf_processor_nonexistent_file(temp_dir: Path) -> None:
    """Test that error is raised for non-existent PDF file."""
    nonexistent = temp_dir / "nonexistent.pdf"

    with pytest.raises(FileNotFoundError):
        PDFProcessor(nonexistent)


def test_pdf_processor_non_pdf_file(temp_dir: Path) -> None:
    """Test that error is raised for non-PDF file."""
    image_file = temp_dir / "image.png"
    image_file.write_bytes(b"fake image")

    with pytest.raises(ValueError, match="Not a PDF file"):
        PDFProcessor(image_file)


def test_pdf_processor_get_page_dimensions(sample_worksheet_pdf: Path) -> None:
    """Test getting PDF page dimensions."""
    processor = PDFProcessor(sample_worksheet_pdf)

    width, height = processor._get_page_dimensions()

    # Letter size is 612x792 points
    assert width == 612.0
    assert height == 792.0


def test_pdf_processor_personalize_for_student(
    sample_worksheet_pdf: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test personalizing PDF for a student."""
    processor = PDFProcessor(sample_worksheet_pdf, add_name=False)
    student = Student.from_photo_path(sample_student_photo)
    output_path = output_dir / "personalized.pdf"

    # Personalize the worksheet
    processor.personalize_for_student(student, output_path)

    # Check that output file was created
    assert output_path.exists()
    assert output_path.suffix == ".pdf"

    # Check that output is a valid PDF
    reader = PdfReader(str(output_path))
    assert len(reader.pages) > 0


def test_pdf_processor_personalize_with_name(
    sample_worksheet_pdf: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test personalizing PDF with student name."""
    processor = PDFProcessor(sample_worksheet_pdf, add_name=True)
    student = Student.from_photo_path(sample_student_photo)
    output_path = output_dir / "personalized_with_name.pdf"

    # Personalize the worksheet
    processor.personalize_for_student(student, output_path)

    # Check that output file was created
    assert output_path.exists()

    # Check that output is a valid PDF
    reader = PdfReader(str(output_path))
    assert len(reader.pages) > 0


def test_pdf_processor_preserves_page_count(
    sample_worksheet_pdf: Path,
    sample_student_photo: Path,
    output_dir: Path,
) -> None:
    """Test that PDF processor preserves the page count."""
    processor = PDFProcessor(sample_worksheet_pdf)
    student = Student.from_photo_path(sample_student_photo)
    output_path = output_dir / "output.pdf"

    # Get original page count
    original_reader = PdfReader(str(sample_worksheet_pdf))
    original_pages = len(original_reader.pages)

    # Personalize
    processor.personalize_for_student(student, output_path)

    # Check page count is preserved
    output_reader = PdfReader(str(output_path))
    assert len(output_reader.pages) == original_pages

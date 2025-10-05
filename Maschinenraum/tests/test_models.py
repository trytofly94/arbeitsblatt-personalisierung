"""Tests for data models."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from worksheet_personalizer.models.student import Student


def test_student_creation_with_valid_photo(sample_student_photo: Path) -> None:
    """Test creating a Student with valid photo path."""
    student = Student(name="Max Mustermann", photo_path=sample_student_photo)

    assert student.name == "Max Mustermann"
    assert student.photo_path == sample_student_photo
    assert student.photo_path.exists()


def test_student_from_photo_path(sample_student_photo: Path) -> None:
    """Test creating Student from photo path (extracts name from filename)."""
    student = Student.from_photo_path(sample_student_photo)

    assert student.name == "max mustermann"  # Underscores replaced with spaces
    assert student.photo_path == sample_student_photo


def test_student_validation_nonexistent_photo(temp_dir: Path) -> None:
    """Test that validation fails for non-existent photo."""
    nonexistent_path = temp_dir / "nonexistent.jpg"

    with pytest.raises(ValidationError) as exc_info:
        Student(name="Test Student", photo_path=nonexistent_path)

    assert "does not exist" in str(exc_info.value)


def test_student_validation_invalid_extension(temp_dir: Path) -> None:
    """Test that validation fails for invalid photo extension."""
    invalid_file = temp_dir / "photo.txt"
    invalid_file.write_text("not an image")

    with pytest.raises(ValidationError) as exc_info:
        Student(name="Test Student", photo_path=invalid_file)

    assert "Invalid photo format" in str(exc_info.value)


def test_student_validation_directory_path(temp_dir: Path) -> None:
    """Test that validation fails when photo_path is a directory."""
    with pytest.raises(ValidationError) as exc_info:
        Student(name="Test Student", photo_path=temp_dir)

    assert "not a file" in str(exc_info.value)


def test_student_str_representation(sample_student_photo: Path) -> None:
    """Test string representation of Student."""
    student = Student(name="Max Mustermann", photo_path=sample_student_photo)
    str_repr = str(student)

    assert "Max Mustermann" in str_repr
    assert "max_mustermann.jpg" in str_repr

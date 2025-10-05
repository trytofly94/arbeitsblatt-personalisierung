"""Tests for file handling utilities."""

from pathlib import Path

import pytest

from worksheet_personalizer.utils.file_handler import (
    discover_student_photos,
    ensure_output_dir,
    generate_output_filename,
)


def test_discover_student_photos(sample_students_folder: Path) -> None:
    """Test discovering student photos in a folder."""
    students = discover_student_photos(sample_students_folder)

    assert len(students) == 3
    assert all(student.photo_path.exists() for student in students)

    # Check names are sorted
    names = [s.name for s in students]
    assert names == sorted(names, key=str.lower)


def test_discover_student_photos_nonexistent_folder(temp_dir: Path) -> None:
    """Test that error is raised for non-existent folder."""
    nonexistent = temp_dir / "nonexistent"

    with pytest.raises(FileNotFoundError):
        discover_student_photos(nonexistent)


def test_discover_student_photos_not_a_directory(temp_dir: Path) -> None:
    """Test that error is raised when path is not a directory."""
    file_path = temp_dir / "file.txt"
    file_path.write_text("test")

    with pytest.raises(ValueError, match="not a directory"):
        discover_student_photos(file_path)


def test_discover_student_photos_empty_folder(temp_dir: Path) -> None:
    """Test that error is raised when no valid photos found."""
    empty_folder = temp_dir / "empty"
    empty_folder.mkdir()

    with pytest.raises(ValueError, match="No valid student photos found"):
        discover_student_photos(empty_folder)


def test_ensure_output_dir_creates_directory(temp_dir: Path) -> None:
    """Test that output directory is created if it doesn't exist."""
    output_path = temp_dir / "new_output"

    assert not output_path.exists()

    ensure_output_dir(output_path)

    assert output_path.exists()
    assert output_path.is_dir()


def test_ensure_output_dir_existing_directory(temp_dir: Path) -> None:
    """Test that no error when directory already exists."""
    existing_dir = temp_dir / "existing"
    existing_dir.mkdir()

    # Should not raise any error
    ensure_output_dir(existing_dir)

    assert existing_dir.exists()
    assert existing_dir.is_dir()


def test_ensure_output_dir_path_is_file(temp_dir: Path) -> None:
    """Test that error is raised when path exists but is a file."""
    file_path = temp_dir / "file.txt"
    file_path.write_text("test")

    with pytest.raises(ValueError, match="not a directory"):
        ensure_output_dir(file_path)


def test_generate_output_filename(temp_dir: Path) -> None:
    """Test generating output filename."""
    worksheet_path = Path("math_test.pdf")
    student_name = "Max Mustermann"
    output_dir = temp_dir / "output"

    result = generate_output_filename(worksheet_path, student_name, output_dir)

    assert result.parent == output_dir
    assert result.name == "math_test_max_mustermann.pdf"
    assert result.suffix == ".pdf"


def test_generate_output_filename_with_spaces(temp_dir: Path) -> None:
    """Test that spaces in student name are converted to underscores."""
    worksheet_path = Path("worksheet.png")
    student_name = "Anna Marie Schmidt"
    output_dir = temp_dir

    result = generate_output_filename(worksheet_path, student_name, output_dir)

    assert result.name == "worksheet_anna_marie_schmidt.png"
    assert " " not in result.stem

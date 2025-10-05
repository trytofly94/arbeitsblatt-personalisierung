"""Tests for worksheet personalizer orchestration."""

from pathlib import Path

import pytest

from worksheet_personalizer.core.personalizer import WorksheetPersonalizer


def test_personalizer_initialization_pdf(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test initializing personalizer with PDF worksheet."""
    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_pdf,
        students_folder=sample_students_folder,
        output_folder=output_dir,
        add_name=False,
    )

    assert personalizer.format == "pdf"
    assert personalizer.add_name is False


def test_personalizer_initialization_image(
    sample_worksheet_image: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test initializing personalizer with image worksheet."""
    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_image,
        students_folder=sample_students_folder,
        output_folder=output_dir,
        add_name=True,
    )

    assert personalizer.format == "image"
    assert personalizer.add_name is True


def test_personalizer_nonexistent_worksheet(
    temp_dir: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test that error is raised for non-existent worksheet."""
    nonexistent = temp_dir / "nonexistent.pdf"

    with pytest.raises(FileNotFoundError):
        WorksheetPersonalizer(
            worksheet_path=nonexistent,
            students_folder=sample_students_folder,
            output_folder=output_dir,
        )


def test_personalizer_nonexistent_students_folder(
    sample_worksheet_pdf: Path,
    temp_dir: Path,
    output_dir: Path,
) -> None:
    """Test that error is raised for non-existent students folder."""
    nonexistent = temp_dir / "nonexistent"

    with pytest.raises(FileNotFoundError):
        WorksheetPersonalizer(
            worksheet_path=sample_worksheet_pdf,
            students_folder=nonexistent,
            output_folder=output_dir,
        )


def test_personalizer_unsupported_format(
    temp_dir: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test that error is raised for unsupported worksheet format."""
    unsupported = temp_dir / "worksheet.docx"
    unsupported.write_bytes(b"fake docx")

    with pytest.raises(ValueError, match="Unsupported worksheet format"):
        WorksheetPersonalizer(
            worksheet_path=unsupported,
            students_folder=sample_students_folder,
            output_folder=output_dir,
        )


def test_personalizer_process_all_pdf(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test processing all students with PDF worksheet."""
    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_pdf,
        students_folder=sample_students_folder,
        output_folder=output_dir,
    )

    created_files = personalizer.process_all()

    # Should create 3 files (one per student)
    assert len(created_files) == 3

    # All files should exist
    for file_path in created_files:
        assert file_path.exists()
        assert file_path.suffix == ".pdf"
        assert file_path.parent == output_dir


def test_personalizer_process_all_image(
    sample_worksheet_image: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test processing all students with image worksheet."""
    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_image,
        students_folder=sample_students_folder,
        output_folder=output_dir,
    )

    created_files = personalizer.process_all()

    # Should create 3 files (one per student)
    assert len(created_files) == 3

    # All files should exist
    for file_path in created_files:
        assert file_path.exists()
        assert file_path.suffix == ".png"


def test_personalizer_process_single(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    sample_students: list,
    output_dir: Path,
) -> None:
    """Test processing a single student."""
    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_pdf,
        students_folder=sample_students_folder,
        output_folder=output_dir,
    )

    student = sample_students[0]
    output_path = personalizer.process_single(student)

    assert output_path.exists()
    assert output_path.suffix == ".pdf"
    assert student.name.replace(" ", "_") in output_path.name


def test_personalizer_creates_output_directory(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    temp_dir: Path,
) -> None:
    """Test that personalizer creates output directory if it doesn't exist."""
    output_dir = temp_dir / "new_output"
    assert not output_dir.exists()

    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_pdf,
        students_folder=sample_students_folder,
        output_folder=output_dir,
    )

    personalizer.process_all()

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_personalizer_with_add_name(
    sample_worksheet_image: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test that add_name option is passed to processor."""
    personalizer = WorksheetPersonalizer(
        worksheet_path=sample_worksheet_image,
        students_folder=sample_students_folder,
        output_folder=output_dir,
        add_name=True,
    )

    assert personalizer.processor.add_name is True

    created_files = personalizer.process_all()
    assert len(created_files) > 0

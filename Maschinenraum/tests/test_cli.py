"""Tests for CLI interface."""

from pathlib import Path

from click.testing import CliRunner

from worksheet_personalizer.cli import personalize


def test_cli_help() -> None:
    """Test CLI help message."""
    runner = CliRunner()
    result = runner.invoke(personalize, ["--help"])

    assert result.exit_code == 0
    assert "Personalize worksheets with student photos" in result.output
    assert "--worksheet" in result.output
    assert "--students-folder" in result.output
    assert "--output-folder" in result.output


def test_cli_missing_required_arguments() -> None:
    """Test that CLI fails when required arguments are missing."""
    runner = CliRunner()

    # Missing all arguments
    result = runner.invoke(personalize, [])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_cli_personalize_pdf_success(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test successful PDF personalization via CLI."""
    runner = CliRunner()

    result = runner.invoke(
        personalize,
        [
            "--worksheet",
            str(sample_worksheet_pdf),
            "--students-folder",
            str(sample_students_folder),
            "--output-folder",
            str(output_dir),
            "--no-preview",
        ],
    )

    assert result.exit_code == 0
    assert "Success" in result.output
    assert "Created 3 personalized worksheet(s)" in result.output


def test_cli_personalize_image_success(
    sample_worksheet_image: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test successful image personalization via CLI."""
    runner = CliRunner()

    result = runner.invoke(
        personalize,
        [
            "--worksheet",
            str(sample_worksheet_image),
            "--students-folder",
            str(sample_students_folder),
            "--output-folder",
            str(output_dir),
            "--no-preview",
        ],
    )

    assert result.exit_code == 0
    assert "Success" in result.output


def test_cli_with_add_name_flag(
    sample_worksheet_image: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test CLI with --add-name flag."""
    runner = CliRunner()

    result = runner.invoke(
        personalize,
        [
            "--worksheet",
            str(sample_worksheet_image),
            "--students-folder",
            str(sample_students_folder),
            "--output-folder",
            str(output_dir),
            "--add-name",
            "--no-preview",
        ],
    )

    assert result.exit_code == 0
    assert "Add Names: True" in result.output


def test_cli_with_verbose_flag(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test CLI with --verbose flag."""
    runner = CliRunner()

    result = runner.invoke(
        personalize,
        [
            "--worksheet",
            str(sample_worksheet_pdf),
            "--students-folder",
            str(sample_students_folder),
            "--output-folder",
            str(output_dir),
            "--verbose",
            "--no-preview",
        ],
    )

    assert result.exit_code == 0


def test_cli_nonexistent_worksheet(
    temp_dir: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test CLI with non-existent worksheet file."""
    runner = CliRunner()
    nonexistent = temp_dir / "nonexistent.pdf"

    result = runner.invoke(
        personalize,
        [
            "--worksheet",
            str(nonexistent),
            "--students-folder",
            str(sample_students_folder),
            "--output-folder",
            str(output_dir),
        ],
    )

    assert result.exit_code != 0
    # Click handles path validation, so this should fail before our code runs


def test_cli_nonexistent_students_folder(
    sample_worksheet_pdf: Path,
    temp_dir: Path,
    output_dir: Path,
) -> None:
    """Test CLI with non-existent students folder."""
    runner = CliRunner()
    nonexistent = temp_dir / "nonexistent"

    result = runner.invoke(
        personalize,
        [
            "--worksheet",
            str(sample_worksheet_pdf),
            "--students-folder",
            str(nonexistent),
            "--output-folder",
            str(output_dir),
        ],
    )

    assert result.exit_code != 0


def test_cli_short_options(
    sample_worksheet_pdf: Path,
    sample_students_folder: Path,
    output_dir: Path,
) -> None:
    """Test CLI with short option flags."""
    runner = CliRunner()

    result = runner.invoke(
        personalize,
        [
            "-w",
            str(sample_worksheet_pdf),
            "-s",
            str(sample_students_folder),
            "-o",
            str(output_dir),
            "-n",  # add-name
            "--no-preview",
        ],
    )

    assert result.exit_code == 0
    assert "Success" in result.output

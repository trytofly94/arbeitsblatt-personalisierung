"""Pytest configuration and fixtures for worksheet personalization tests."""

from pathlib import Path
from typing import Iterator

import pytest
from PIL import Image, ImageDraw

from worksheet_personalizer.models.student import Student


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_worksheet_image(temp_dir: Path) -> Path:
    """Create a sample worksheet image for testing.

    Returns:
        Path to a simple PNG worksheet image
    """
    worksheet_path = temp_dir / "worksheet.png"

    # Create a simple 800x1000 pixel white image with some text
    img = Image.new("RGB", (800, 1000), color="white")
    draw = ImageDraw.Draw(img)

    # Add some "worksheet content" (just text for testing)
    draw.rectangle([50, 50, 750, 950], outline="black", width=2)
    draw.text((100, 100), "Math Worksheet", fill="black")
    draw.text((100, 150), "Name: ______________", fill="black")
    draw.text((100, 200), "Date: ______________", fill="black")

    # Save with 300 DPI
    img.save(worksheet_path, dpi=(300, 300))

    return worksheet_path


@pytest.fixture
def sample_worksheet_pdf(temp_dir: Path) -> Path:
    """Create a sample worksheet PDF for testing.

    Returns:
        Path to a simple PDF worksheet
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    pdf_path = temp_dir / "worksheet.pdf"

    # Create a simple PDF
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "Math Test")
    c.drawString(100, 700, "Name: ______________")
    c.drawString(100, 650, "Date: ______________")
    c.save()

    return pdf_path


@pytest.fixture
def sample_student_photo(temp_dir: Path) -> Path:
    """Create a sample student photo for testing.

    Returns:
        Path to a sample photo (JPG)
    """
    photo_path = temp_dir / "max_mustermann.jpg"

    # Create a simple colored image (300x400 pixels)
    img = Image.new("RGB", (300, 400), color="lightblue")
    draw = ImageDraw.Draw(img)

    # Draw a simple face representation
    draw.ellipse([100, 100, 200, 200], fill="yellow", outline="black")  # Face
    draw.ellipse([130, 140, 145, 155], fill="black")  # Left eye
    draw.ellipse([155, 140, 170, 155], fill="black")  # Right eye
    draw.arc([130, 160, 170, 180], start=0, end=180, fill="black")  # Smile

    img.save(photo_path, quality=95)

    return photo_path


@pytest.fixture
def sample_students_folder(temp_dir: Path) -> Path:
    """Create a folder with multiple sample student photos.

    Returns:
        Path to folder containing 3 student photos
    """
    students_folder = temp_dir / "students"
    students_folder.mkdir()

    # Create 3 different student photos
    students_data = [
        ("max_mustermann.jpg", "lightblue"),
        ("anna_schmidt.jpg", "lightpink"),
        ("tom_mueller.png", "lightgreen"),
    ]

    for filename, color in students_data:
        photo_path = students_folder / filename

        # Create a simple colored image
        img = Image.new("RGB", (300, 400), color=color)
        draw = ImageDraw.Draw(img)

        # Draw simple face
        draw.ellipse([100, 100, 200, 200], fill="yellow", outline="black")
        draw.ellipse([130, 140, 145, 155], fill="black")
        draw.ellipse([155, 140, 170, 155], fill="black")
        draw.arc([130, 160, 170, 180], start=0, end=180, fill="black")

        # Save in appropriate format
        if filename.endswith(".png"):
            img.save(photo_path)
        else:
            img.save(photo_path, quality=95)

    return students_folder


@pytest.fixture
def sample_students(sample_students_folder: Path) -> list[Student]:
    """Create a list of Student objects from sample photos.

    Returns:
        List of 3 Student objects
    """
    photos = sorted(sample_students_folder.glob("*.[jp][pn][g]*"))
    return [Student.from_photo_path(photo) for photo in photos]


@pytest.fixture
def output_dir(temp_dir: Path) -> Iterator[Path]:
    """Provide an output directory for tests.

    Returns:
        Path to output directory (created if needed)
    """
    out_dir = temp_dir / "output"
    out_dir.mkdir(exist_ok=True)
    yield out_dir

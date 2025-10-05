"""Student data model for worksheet personalization.

This module defines the Student data model using Pydantic for validation
and type safety.
"""

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, field_validator


class Student(BaseModel):
    """Represents a student with name and photo.

    Attributes:
        name: The student's full name (extracted from filename)
        photo_path: Path to the student's photo file

    Raises:
        ValueError: If photo_path doesn't exist or has invalid extension
    """

    name: str
    photo_path: Path

    # Class variable for allowed photo extensions
    ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".jpg", ".jpeg", ".png"}

    @field_validator("photo_path")
    @classmethod
    def validate_photo_path(cls, v: Path) -> Path:
        """Validate that photo path exists and has correct extension.

        Args:
            v: The photo path to validate

        Returns:
            The validated photo path

        Raises:
            ValueError: If path doesn't exist or has invalid extension
        """
        if not v.exists():
            raise ValueError(f"Photo file does not exist: {v}")

        if not v.is_file():
            raise ValueError(f"Photo path is not a file: {v}")

        if v.suffix.lower() not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid photo format: {v.suffix}. "
                f"Allowed formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        return v

    @classmethod
    def from_photo_path(cls, photo_path: Path) -> "Student":
        """Create a Student instance from a photo file path.

        The student's name is extracted from the filename (without extension).
        Underscores in the filename are converted to spaces.

        Args:
            photo_path: Path to the student's photo file

        Returns:
            A new Student instance

        Example:
            >>> student = Student.from_photo_path(Path("max_mustermann.jpg"))
            >>> student.name
            'max mustermann'
        """
        name = photo_path.stem.replace("_", " ")
        return cls(name=name, photo_path=photo_path)

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"Student(name='{self.name}', photo='{self.photo_path.name}')"

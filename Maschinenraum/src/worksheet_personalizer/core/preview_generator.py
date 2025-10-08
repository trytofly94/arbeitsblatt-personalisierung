"""Preview generator for worksheet personalization.

This module generates preview versions of personalized worksheets
using the first student in a list as an example.
"""

import logging
import tempfile
from pathlib import Path

from worksheet_personalizer.core.image_processor import ImageProcessor
from worksheet_personalizer.core.pdf_processor import PDFProcessor
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.settings_manager import SettingsManager

logger = logging.getLogger(__name__)


class PreviewGenerator:
    """Generates preview versions of personalized worksheets.

    Uses the first student from a list to create a preview that demonstrates
    what the final personalized worksheet will look like.

    Attributes:
        worksheet_path: Path to the template worksheet file
        students: List of Student objects
        settings_manager: SettingsManager instance for configuration
    """

    def __init__(
        self,
        worksheet_path: Path,
        students: list[Student],
        settings_manager: SettingsManager,
    ) -> None:
        """Initialize the preview generator.

        Args:
            worksheet_path: Path to the template worksheet file
            students: List of Student objects (must have at least one)
            settings_manager: SettingsManager instance for configuration

        Raises:
            ValueError: If students list is empty
        """
        if not students:
            raise ValueError("Cannot generate preview: student list is empty")

        self.worksheet_path = worksheet_path
        self.students = students
        self.settings_manager = settings_manager
        self._preview_path: Path | None = None

    def generate_preview(self) -> Path:
        """Generate a preview worksheet using the first student.

        Creates a temporary file with the personalized preview.
        The file format matches the input worksheet format.

        Returns:
            Path to the generated preview file

        Raises:
            RuntimeError: If preview generation fails
        """
        try:
            # Use the first student for preview
            first_student = self.students[0]
            logger.info(f"Generating preview for student: {first_student.name}")

            # Get the appropriate processor
            processor = self._get_processor()

            # Create temporary file with same extension as worksheet
            suffix = self.worksheet_path.suffix
            with tempfile.NamedTemporaryFile(
                mode="wb", suffix=suffix, delete=False
            ) as tmp_file:
                self._preview_path = Path(tmp_file.name)

            # Generate the personalized preview
            processor.personalize_for_student(
                student=first_student, output_path=self._preview_path
            )

            logger.info(f"Preview generated successfully: {self._preview_path}")
            return self._preview_path

        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            # Clean up temporary file if it was created
            if self._preview_path and self._preview_path.exists():
                self._preview_path.unlink()
            raise RuntimeError(f"Preview generation failed: {e}") from e

    def cleanup_preview(self, preview_path: Path | None = None) -> None:
        """Delete the temporary preview file.

        Args:
            preview_path: Path to the preview file to delete.
                         If None, uses the last generated preview.
        """
        path_to_delete = preview_path or self._preview_path

        if path_to_delete and path_to_delete.exists():
            try:
                path_to_delete.unlink()
                logger.debug(f"Cleaned up preview file: {path_to_delete}")
                if path_to_delete == self._preview_path:
                    self._preview_path = None
            except Exception as e:
                logger.warning(f"Failed to clean up preview file: {e}")

    def _get_processor(self) -> PDFProcessor | ImageProcessor:
        """Get the appropriate processor based on worksheet format.

        Returns:
            PDFProcessor for .pdf files, ImageProcessor for image files

        Raises:
            ValueError: If worksheet format is not supported
        """
        suffix = self.worksheet_path.suffix.lower()

        if suffix == ".pdf":
            return PDFProcessor(
                worksheet_path=self.worksheet_path,
                settings_manager=self.settings_manager,
            )
        elif suffix in {".png", ".jpg", ".jpeg"}:
            return ImageProcessor(
                worksheet_path=self.worksheet_path,
                settings_manager=self.settings_manager,
            )
        else:
            raise ValueError(
                f"Unsupported worksheet format: {suffix}. "
                "Supported formats: .pdf, .png, .jpg, .jpeg"
            )

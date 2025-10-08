"""Worksheet personalization orchestration.

This module provides the main WorksheetPersonalizer class that orchestrates
the entire personalization process, handling both PDF and image formats.
"""

import logging
from pathlib import Path
from typing import Union

from rich.console import Console
from rich.prompt import Confirm

from worksheet_personalizer.core.image_processor import ImageProcessor
from worksheet_personalizer.core.pdf_processor import PDFProcessor
from worksheet_personalizer.core.preview_generator import PreviewGenerator
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.settings_manager import SettingsManager
from worksheet_personalizer.utils.file_handler import (
    discover_student_photos,
    ensure_output_dir,
    generate_output_filename,
)
from worksheet_personalizer.utils.interaction_handler import InteractionHandler
from worksheet_personalizer.utils.settings_menu import SettingsMenu

logger = logging.getLogger(__name__)


class WorksheetPersonalizer:
    """Orchestrates the worksheet personalization process.

    This class handles the complete workflow of personalizing worksheets:
    - Detecting the input format (PDF or image)
    - Discovering student photos
    - Creating personalized worksheets for all students
    - Managing output directory

    Attributes:
        worksheet_path: Path to the worksheet file
        students_folder: Path to folder containing student photos
        output_folder: Path to output directory
        add_name: Whether to add student names to worksheets
    """

    def __init__(
        self,
        worksheet_path: Path,
        students_folder: Path,
        output_folder: Path,
        add_name: bool = False,
        preview_enabled: bool = True,
    ) -> None:
        """Initialize the worksheet personalizer.

        Args:
            worksheet_path: Path to the worksheet file (PDF or image)
            students_folder: Path to folder containing student photos
            output_folder: Path where personalized worksheets will be saved
            add_name: Whether to add student names to worksheets
            preview_enabled: Whether to show interactive preview before processing

        Raises:
            FileNotFoundError: If worksheet or students folder doesn't exist
            ValueError: If worksheet format is not supported
        """
        if not worksheet_path.exists():
            raise FileNotFoundError(f"Worksheet file not found: {worksheet_path}")

        if not students_folder.exists():
            raise FileNotFoundError(f"Students folder not found: {students_folder}")

        self.worksheet_path = worksheet_path
        self.students_folder = students_folder
        self.output_folder = output_folder
        self.add_name = add_name
        self.preview_enabled = preview_enabled

        # Settings manager for preview mode
        self.settings_manager = SettingsManager()

        # Rich console for output
        self.console = Console()

        # Detect format and create appropriate processor
        self.format = self._detect_format()
        self.processor = self._get_processor()

        logger.info(
            f"Initialized WorksheetPersonalizer: "
            f"format={self.format}, add_name={add_name}, preview={preview_enabled}"
        )

    def _detect_format(self) -> str:
        """Detect the worksheet format based on file extension.

        Returns:
            Format string: "pdf" or "image"

        Raises:
            ValueError: If format is not supported
        """
        extension = self.worksheet_path.suffix.lower()

        if extension == ".pdf":
            return "pdf"
        elif extension in {".png", ".jpg", ".jpeg"}:
            return "image"
        else:
            raise ValueError(
                f"Unsupported worksheet format: {extension}. "
                f"Supported formats: .pdf, .png, .jpg, .jpeg"
            )

    def _get_processor(self) -> Union[PDFProcessor, ImageProcessor]:
        """Get the appropriate processor based on detected format.

        Returns:
            PDFProcessor or ImageProcessor instance

        Raises:
            ValueError: If format is invalid
        """
        if self.format == "pdf":
            return PDFProcessor(self.worksheet_path, self.add_name)
        elif self.format == "image":
            return ImageProcessor(self.worksheet_path, self.add_name)
        else:
            raise ValueError(f"Invalid format: {self.format}")

    def process_all(self) -> list[Path]:
        """Process worksheets for all students in the folder.

        This method:
        1. Discovers all student photos in the students folder
        2. Shows preview if enabled (with interactive settings menu)
        3. Ensures the output directory exists
        4. Creates a personalized worksheet for each student
        5. Returns the list of created files

        Returns:
            List of paths to created personalized worksheets

        Raises:
            ValueError: If no students found or processing fails
            IOError: If files cannot be written
        """
        logger.info("Starting batch personalization process")

        # Discover students
        students = discover_student_photos(self.students_folder)
        logger.info(f"Found {len(students)} student(s) to process")

        # Show preview if enabled
        if self.preview_enabled:
            continue_processing = self._show_preview(students)
            if not continue_processing:
                self.console.print("[yellow]Processing cancelled by user.[/yellow]")
                return []

        # Ensure output directory exists
        ensure_output_dir(self.output_folder)

        # Process each student
        created_files: list[Path] = []
        errors: list[tuple[Student, Exception]] = []

        for i, student in enumerate(students, 1):
            try:
                logger.info(f"Processing {i}/{len(students)}: {student.name}")

                # Generate output filename
                output_path = generate_output_filename(
                    self.worksheet_path, student.name, self.output_folder
                )

                # Personalize worksheet
                self.processor.personalize_for_student(student, output_path)

                created_files.append(output_path)
                logger.info(f"✓ Successfully created: {output_path.name}")

            except Exception as e:
                logger.error(f"✗ Error processing {student.name}: {e}")
                errors.append((student, e))
                continue

        # Summary
        logger.info(
            f"\nPersonalization complete: {len(created_files)} successful, "
            f"{len(errors)} failed"
        )

        if errors:
            logger.warning("\nFailed students:")
            for student, error in errors:
                logger.warning(f"  - {student.name}: {error}")

        if not created_files:
            raise ValueError("No worksheets were successfully created")

        return created_files

    def _show_preview(self, students: list[Student]) -> bool:
        """Show interactive preview and handle user interaction.

        Args:
            students: List of students (first one used for preview)

        Returns:
            True to continue processing, False to cancel
        """
        self.console.print(
            f"\n[bold cyan]🔍 Generating preview for {self.worksheet_path.name}...[/bold cyan]"
        )

        # Create preview generator
        try:
            preview_gen = PreviewGenerator(
                worksheet_path=self.worksheet_path,
                students=students,
                settings_manager=self.settings_manager,
            )
        except ValueError as e:
            self.console.print(f"[red]❌ Error creating preview: {e}[/red]")
            return False

        # Create interaction handler
        interaction = InteractionHandler(self.console)

        # Create settings menu
        settings_menu = SettingsMenu(self.settings_manager, self.console)

        preview_path = None
        viewer_process = None

        try:
            # Main preview loop
            while True:
                # Generate preview (or regenerate after settings change)
                try:
                    preview_path = preview_gen.generate_preview()
                    self.console.print(
                        f"[green]✓ Preview created with student: {students[0].name}[/green]"
                    )
                except Exception as e:
                    self.console.print(f"[red]❌ Error generating preview: {e}[/red]")
                    logger.error(f"Preview generation failed: {e}", exc_info=True)

                    # Ask if user wants to continue anyway
                    if Confirm.ask("Continue processing anyway?", default=False):
                        return True
                    else:
                        return False

                # Open in viewer
                try:
                    viewer_process = interaction.open_in_viewer(preview_path)
                except Exception as e:
                    self.console.print(f"[yellow]⚠️  Error opening preview: {e}[/yellow]")
                    logger.warning(f"Failed to open preview: {e}")

                # Wait for user input
                action = interaction.wait_for_input()

                if action == "esc":
                    self.console.print("[yellow]Operation cancelled.[/yellow]")
                    return False

                elif action == "enter":
                    self.console.print("[green]✓ Continuing with all students...[/green]")
                    return True

                elif action == "menu":
                    # Close viewer while in menu
                    if viewer_process:
                        interaction.close_viewer(viewer_process)
                        viewer_process = None

                    # Show settings menu
                    changes_made = settings_menu.show()

                    # If changes were made, regenerate preview
                    if changes_made:
                        self.console.print(
                            "\n[cyan]Settings changed, generating new preview...[/cyan]"
                        )
                        # Clean up old preview
                        if preview_path:
                            preview_gen.cleanup_preview(preview_path)
                            preview_path = None
                        # Loop will regenerate preview

        finally:
            # Clean up
            if viewer_process:
                interaction.close_viewer(viewer_process)
            if preview_path:
                preview_gen.cleanup_preview(preview_path)

    def process_single(self, student: Student) -> Path:
        """Process worksheet for a single student.

        Args:
            student: Student object with name and photo path

        Returns:
            Path to the created personalized worksheet

        Raises:
            ValueError: If processing fails
        """
        logger.info(f"Processing single student: {student.name}")

        # Ensure output directory exists
        ensure_output_dir(self.output_folder)

        # Generate output filename
        output_path = generate_output_filename(
            self.worksheet_path, student.name, self.output_folder
        )

        # Personalize worksheet
        self.processor.personalize_for_student(student, output_path)

        logger.info(f"Created: {output_path}")
        return output_path

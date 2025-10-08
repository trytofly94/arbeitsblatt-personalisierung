"""Batch processor for worksheet personalization.

This module handles batch processing of worksheets from Input folders
and creates personalized versions in Output folders.
"""

import logging
import shutil
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from worksheet_personalizer.core.pdf_processor import PDFProcessor
from worksheet_personalizer.core.image_processor import ImageProcessor
from worksheet_personalizer.core.preview_generator import PreviewGenerator
from worksheet_personalizer.models.student import Student
from worksheet_personalizer.settings_manager import SettingsManager
from worksheet_personalizer.utils.interaction_handler import InteractionHandler
from worksheet_personalizer.utils.settings_menu import SettingsMenu

logger = logging.getLogger(__name__)
console = Console()


class BatchProcessor:
    """Processes worksheets in batch mode for multiple student groups.

    This class handles the entire workflow:
    1. Reads PDFs from Input folders (Input-A, Input-B, Input-C)
    2. Matches with student photos from Schüler folders
    3. Creates personalized worksheets
    4. Saves to Ausgabe folders with worksheet-named subfolders
    5. Moves processed PDFs from Input to Ausgabe
    """

    # Supported worksheet formats
    PDF_FORMATS = {".pdf"}
    IMAGE_FORMATS = {".png", ".jpg", ".jpeg"}
    SUPPORTED_FORMATS = PDF_FORMATS | IMAGE_FORMATS

    # Supported photo formats
    PHOTO_FORMATS = {".jpg", ".jpeg", ".png"}

    def __init__(self, base_path: Path, preview_enabled: bool = True) -> None:
        """Initialize batch processor.

        Args:
            base_path: Base directory containing Input-X, Schüler-X, Ausgabe-X folders
            preview_enabled: Whether to show interactive preview before processing
        """
        self.base_path = base_path
        self.settings_manager = SettingsManager()
        self.groups = ["A", "B", "C"]
        self.preview_enabled = preview_enabled

        logger.info(f"Initialized batch processor at: {base_path}")

    def _get_folder_paths(self, group: str) -> tuple[Path, Path, Path]:
        """Get folder paths for a specific group.

        Args:
            group: Group identifier (A, B, or C)

        Returns:
            Tuple of (input_folder, students_folder, output_folder)
        """
        input_folder = self.base_path / f"Input-{group}"
        students_folder = self.base_path / f"Schüler-{group}"
        output_folder = self.base_path / f"Ausgabe-{group}"

        return input_folder, students_folder, output_folder

    def _load_students(self, students_folder: Path) -> List[Student]:
        """Load student data from a folder.

        Args:
            students_folder: Path to folder containing student photos

        Returns:
            List of Student objects
        """
        students = []

        if not students_folder.exists():
            logger.warning(f"Students folder not found: {students_folder}")
            return students

        for photo_path in students_folder.iterdir():
            if photo_path.suffix.lower() in self.PHOTO_FORMATS and photo_path.is_file():
                # Extract student name from filename (without extension)
                student_name = photo_path.stem
                student = Student(name=student_name, photo_path=photo_path)
                students.append(student)
                logger.debug(f"Loaded student: {student_name}")

        logger.info(f"Loaded {len(students)} students from {students_folder}")
        return students

    def _create_output_folder(self, output_base: Path, worksheet_name: str) -> Path:
        """Create output folder for a worksheet, handling duplicates.

        Args:
            output_base: Base output folder (e.g., Ausgabe-A)
            worksheet_name: Name of the worksheet (without extension)

        Returns:
            Path to the created output folder
        """
        output_folder = output_base / worksheet_name

        # Handle duplicate folder names with numbering
        counter = 2
        while output_folder.exists():
            output_folder = output_base / f"{worksheet_name}_{counter}"
            counter += 1

        output_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created output folder: {output_folder}")

        return output_folder

    def _process_worksheet(
        self,
        worksheet_path: Path,
        students: List[Student],
        output_folder: Path,
        progress: Progress,
        task_id: int
    ) -> None:
        """Process a single worksheet for all students.

        Args:
            worksheet_path: Path to the worksheet file
            students: List of students to personalize for
            output_folder: Folder to save personalized worksheets
            progress: Rich progress instance
            task_id: Progress task ID
        """
        if not students:
            console.print(f"[yellow]⚠️  Keine Schüler gefunden für {worksheet_path.name}[/yellow]")
            return

        # Get settings
        add_name = self.settings_manager.get("add_name", True)

        # Determine processor based on file type
        if worksheet_path.suffix.lower() in self.PDF_FORMATS:
            processor = PDFProcessor(worksheet_path, add_name=add_name)
        elif worksheet_path.suffix.lower() in self.IMAGE_FORMATS:
            processor = ImageProcessor(worksheet_path, add_name=add_name)
        else:
            console.print(f"[red]❌ Nicht unterstütztes Format: {worksheet_path.suffix}[/red]")
            return

        # Process for each student
        for student in students:
            try:
                # Create output filename
                output_filename = f"{student.name}{worksheet_path.suffix}"
                output_path = output_folder / output_filename

                # Personalize worksheet
                processor.personalize_for_student(student, output_path)

                progress.update(task_id, advance=1)
                logger.info(f"Created personalized worksheet for {student.name}")

            except Exception as e:
                console.print(f"[red]❌ Fehler bei {student.name}: {e}[/red]")
                logger.error(f"Error processing worksheet for {student.name}: {e}", exc_info=True)

    def _move_processed_worksheet(self, worksheet_path: Path, output_folder: Path) -> None:
        """Move processed worksheet from Input to Output folder.

        Args:
            worksheet_path: Original worksheet path in Input folder
            output_folder: Folder where personalized worksheets were saved
        """
        try:
            target_path = output_folder / worksheet_path.name
            shutil.move(str(worksheet_path), str(target_path))
            logger.info(f"Moved {worksheet_path.name} to {output_folder}")
        except Exception as e:
            console.print(f"[yellow]⚠️  Konnte {worksheet_path.name} nicht verschieben: {e}[/yellow]")
            logger.error(f"Error moving worksheet: {e}", exc_info=True)

    def _show_preview_for_worksheet(
        self, worksheet_path: Path, students: List[Student]
    ) -> bool:
        """Show preview for a worksheet and handle user interaction.

        Generates a preview using the first student, opens it in the system
        viewer, and waits for user input (ESC/ENTER/MENU).

        Args:
            worksheet_path: Path to the worksheet to preview
            students: List of students (first one used for preview)

        Returns:
            True to continue processing, False to cancel
        """
        console.print(f"\n[bold cyan]🔍 Generiere Vorschau für {worksheet_path.name}...[/bold cyan]")

        # Create preview generator
        try:
            preview_gen = PreviewGenerator(
                worksheet_path=worksheet_path,
                students=students,
                settings_manager=self.settings_manager,
            )
        except ValueError as e:
            console.print(f"[red]❌ Fehler beim Erstellen der Vorschau: {e}[/red]")
            return False

        # Create interaction handler
        interaction = InteractionHandler(console)

        # Create settings menu
        settings_menu = SettingsMenu(self.settings_manager, console)

        preview_path = None
        viewer_process = None

        try:
            # Main preview loop
            while True:
                # Generate preview (or regenerate after settings change)
                try:
                    preview_path = preview_gen.generate_preview()
                    console.print(
                        f"[green]✓ Vorschau erstellt mit Schüler: {students[0].name}[/green]"
                    )
                except Exception as e:
                    console.print(f"[red]❌ Fehler bei Vorschau-Generierung: {e}[/red]")
                    logger.error(f"Preview generation failed: {e}", exc_info=True)

                    # Ask if user wants to continue anyway
                    from rich.prompt import Confirm

                    if Confirm.ask(
                        "Möchten Sie trotzdem fortfahren?", default=False
                    ):
                        return True
                    else:
                        return False

                # Open in viewer
                try:
                    viewer_process = interaction.open_in_viewer(preview_path)
                except Exception as e:
                    console.print(f"[yellow]⚠️  Fehler beim Öffnen der Vorschau: {e}[/yellow]")
                    logger.warning(f"Failed to open preview: {e}")

                # Wait for user input
                action = interaction.wait_for_input()

                if action == "esc":
                    console.print("[yellow]Vorgang abgebrochen.[/yellow]")
                    return False

                elif action == "enter":
                    console.print("[green]✓ Fortfahren mit allen Schülern...[/green]")
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
                        console.print(
                            "\n[cyan]Einstellungen geändert, generiere neue Vorschau...[/cyan]"
                        )
                        # Clean up old preview
                        if preview_path:
                            preview_gen.cleanup_preview(preview_path)
                            preview_path = None
                        # Loop will regenerate preview
                    else:
                        # No changes, just reopen the preview
                        pass

        finally:
            # Clean up
            if viewer_process:
                interaction.close_viewer(viewer_process)
            if preview_path:
                preview_gen.cleanup_preview(preview_path)

    def process_group(self, group: str) -> None:
        """Process all worksheets for a specific group.

        Args:
            group: Group identifier (A, B, or C)
        """
        input_folder, students_folder, output_folder = self._get_folder_paths(group)

        console.print(f"\n[bold cyan]📁 Verarbeite Gruppe {group}[/bold cyan]")

        # Check if folders exist
        if not input_folder.exists():
            console.print(f"[yellow]⚠️  Input-Ordner nicht gefunden: {input_folder}[/yellow]")
            return

        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)

        # Load students
        students = self._load_students(students_folder)

        if not students:
            console.print(f"[yellow]⚠️  Keine Schülerfotos gefunden in {students_folder}[/yellow]")
            return

        # Find all worksheets in Input folder
        worksheets = [
            f for f in input_folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS
        ]

        if not worksheets:
            console.print(f"[yellow]⚠️  Keine Arbeitsblätter gefunden in {input_folder}[/yellow]")
            return

        console.print(f"[green]✓ {len(students)} Schüler gefunden[/green]")
        console.print(f"[green]✓ {len(worksheets)} Arbeitsblatt/Arbeitsblätter gefunden[/green]")

        # Process each worksheet
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:

            for worksheet_path in worksheets:
                # Show preview if enabled
                if self.preview_enabled:
                    continue_processing = self._show_preview_for_worksheet(
                        worksheet_path, students
                    )
                    if not continue_processing:
                        console.print(
                            f"[yellow]⚠️  Überspringe {worksheet_path.name}[/yellow]"
                        )
                        continue

                worksheet_name = worksheet_path.stem
                output_subfolder = self._create_output_folder(output_folder, worksheet_name)

                task_id = progress.add_task(
                    f"[cyan]Verarbeite {worksheet_path.name}...",
                    total=len(students)
                )

                self._process_worksheet(
                    worksheet_path,
                    students,
                    output_subfolder,
                    progress,
                    task_id
                )

                # Keep original worksheet in Input folder (don't move)
                # self._move_processed_worksheet(worksheet_path, output_subfolder)

                console.print(f"[green]✓ {worksheet_path.name} fertig![/green]")

    def process_all_groups(self) -> None:
        """Process all groups (A, B, C)."""
        console.print("\n[bold green]🚀 Starte Batch-Verarbeitung[/bold green]\n")

        for group in self.groups:
            try:
                self.process_group(group)
            except Exception as e:
                console.print(f"[red]❌ Fehler bei Gruppe {group}: {e}[/red]")
                logger.error(f"Error processing group {group}: {e}", exc_info=True)

        console.print("\n[bold green]✅ Batch-Verarbeitung abgeschlossen![/bold green]\n")


def main() -> None:
    """Main entry point for batch processing."""
    # Get base path (parent of Maschinenraum)
    base_path = Path(__file__).parent.parent.parent.parent

    try:
        processor = BatchProcessor(base_path)
        processor.process_all_groups()

    except Exception as e:
        console.print(f"\n[bold red]❌ Kritischer Fehler:[/bold red] {e}\n")
        logger.error(f"Critical error in batch processing: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

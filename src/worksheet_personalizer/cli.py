"""Command-line interface for worksheet personalization.

This module provides a Click-based CLI for personalizing worksheets with
student photos and names.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from worksheet_personalizer.config import setup_logging
from worksheet_personalizer.core.personalizer import WorksheetPersonalizer

console = Console()


@click.command()
@click.option(
    "--worksheet",
    "-w",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the worksheet file (PDF or image)",
)
@click.option(
    "--students-folder",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Path to folder containing student photos",
)
@click.option(
    "--output-folder",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Path to output folder for personalized worksheets",
)
@click.option(
    "--add-name",
    "-n",
    is_flag=True,
    default=False,
    help="Add student name next to photo",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose logging (DEBUG level)",
)
def personalize(
    worksheet: Path,
    students_folder: Path,
    output_folder: Path,
    add_name: bool,
    verbose: bool,
) -> None:
    """Personalize worksheets with student photos.

    This tool takes a worksheet (PDF or image) and a folder of student photos,
    then creates personalized versions of the worksheet for each student with
    their photo in the top-right corner.

    Example:

        worksheet-personalizer -w math_test.pdf -s ./students -o ./output

    With names:

        worksheet-personalizer -w worksheet.png -s ./students -o ./output --add-name
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    # Print header
    console.print("\n[bold cyan]Worksheet Personalizer[/bold cyan]")
    console.print("=" * 50)
    console.print(f"[bold]Worksheet:[/bold] {worksheet}")
    console.print(f"[bold]Students:[/bold] {students_folder}")
    console.print(f"[bold]Output:[/bold] {output_folder}")
    console.print(f"[bold]Add Names:[/bold] {add_name}")
    console.print("=" * 50 + "\n")

    try:
        # Initialize personalizer
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Initializing personalizer...", total=None
            )

            personalizer = WorksheetPersonalizer(
                worksheet_path=worksheet,
                students_folder=students_folder,
                output_folder=output_folder,
                add_name=add_name,
            )

            progress.update(task, completed=True)

        # Process all students
        console.print("[bold green]Processing students...[/bold green]\n")

        created_files = personalizer.process_all()

        # Success message
        console.print(f"\n[bold green]✓ Success![/bold green]")
        console.print(
            f"Created {len(created_files)} personalized worksheet(s) in {output_folder}"
        )

        # List created files
        if created_files:
            console.print("\n[bold]Created files:[/bold]")
            for file_path in created_files:
                console.print(f"  • {file_path.name}")

    except FileNotFoundError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        console.print(
            "\n[yellow]Tip:[/yellow] Make sure all input paths exist and are correct."
        )
        sys.exit(1)

    except ValueError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        console.print(
            "\n[yellow]Tip:[/yellow] Check that your worksheet and photos are in "
            "supported formats (PDF, PNG, JPG)."
        )
        sys.exit(1)

    except Exception as e:
        console.print(f"\n[bold red]✗ Unexpected error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        else:
            console.print(
                "\n[yellow]Tip:[/yellow] Run with --verbose flag for more details."
            )
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    personalize()


if __name__ == "__main__":
    main()

"""Interactive settings menu for preview mode.

This module provides an interactive menu for adjusting worksheet
personalization settings during preview mode.
"""

import logging

from rich.console import Console
from rich.prompt import Confirm, FloatPrompt
from rich.table import Table

from worksheet_personalizer.config import PHOTO_POSITIONS
from worksheet_personalizer.settings_manager import SettingsManager

logger = logging.getLogger(__name__)

# Try to import readchar for single-key input
try:
    import readchar
    READCHAR_AVAILABLE = True
except ImportError:
    READCHAR_AVAILABLE = False
    logger.warning("readchar not available, using Enter-based input")


class SettingsMenu:
    """Interactive settings menu for worksheet personalization.

    Provides a user-friendly interface for modifying settings during
    preview mode, including name toggle, position presets, and photo size.

    Attributes:
        settings_manager: SettingsManager instance for persistence
        console: Rich Console instance for formatted output
    """

    def __init__(self, settings_manager: SettingsManager, console: Console) -> None:
        """Initialize the settings menu.

        Args:
            settings_manager: SettingsManager instance for configuration
            console: Rich Console instance for formatted output
        """
        self.settings_manager = settings_manager
        self.console = console

    def show(self) -> bool:
        """Display the interactive settings menu.

        Shows current settings and allows the user to modify them.
        Changes are saved immediately to settings.json.

        Returns:
            True if any changes were made (indicating preview should be regenerated),
            False if no changes were made
        """
        changes_made = False

        while True:
            # Clear console for clean display
            self.console.clear()

            # Display current settings
            self._display_current_settings()

            # Show menu options
            self.console.print("\n[bold cyan]Settings Menu:[/bold cyan]")
            self.console.print("  1) Toggle name on worksheet")
            self.console.print("  2) Change photo position")
            self.console.print("  3) Adjust photo size")
            self.console.print("  4) Change text position")
            self.console.print("  5) Back to preview")
            self.console.print()

            # Get user choice with single-key input
            if READCHAR_AVAILABLE:
                self.console.print("[dim]Press a number key (1-5)...[/dim]", end="")
                choice = self._wait_for_number_key(["1", "2", "3", "4", "5"])
                self.console.print(f" {choice}")
            else:
                # Fallback to Enter-based input
                from rich.prompt import Prompt
                choice = Prompt.ask(
                    "Select an option",
                    choices=["1", "2", "3", "4", "5"],
                    default="5",
                )

            if choice == "1":
                if self._toggle_add_name():
                    changes_made = True
            elif choice == "2":
                if self._select_position():
                    changes_made = True
            elif choice == "3":
                if self._adjust_photo_size():
                    changes_made = True
            elif choice == "4":
                if self._select_text_position():
                    changes_made = True
            elif choice == "5":
                # Exit menu
                break

        return changes_made

    def _wait_for_number_key(self, valid_keys: list[str]) -> str:
        """Wait for user to press a number key.

        Args:
            valid_keys: List of valid key choices (e.g., ["1", "2", "3"])

        Returns:
            The pressed key as a string
        """
        while True:
            key = readchar.readkey()
            if key in valid_keys:
                return key
            # Ignore invalid keys and wait for a valid one

    def _display_current_settings(self) -> None:
        """Display current settings in a formatted table."""
        self.console.print("\n[bold]Current Settings:[/bold]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Setting", style="dim", width=20)
        table.add_column("Value", style="green")

        # Get current settings
        add_name = self.settings_manager.get("add_name", True)
        photo_size = self.settings_manager.get("photo_size_cm", 2.5)
        photo_position = self.settings_manager.get_photo_position()
        text_position = self.settings_manager.get("name_position", "beside_photo")

        # Add rows
        table.add_row("Add Name", "Yes" if add_name else "No")
        table.add_row("Photo Position", photo_position)
        table.add_row("Photo Size", f"{photo_size} cm")
        table.add_row("Text Position", text_position.replace("_", " ").title())

        self.console.print(table)

    def _toggle_add_name(self) -> bool:
        """Toggle the 'add name' setting.

        Returns:
            True if setting was changed, False otherwise
        """
        current_value = self.settings_manager.get("add_name", True)

        self.console.print(
            f"\nCurrent setting: [green]{'Yes' if current_value else 'No'}[/green]"
        )

        new_value = Confirm.ask(
            "Add student names to worksheets?",
            default=current_value,
        )

        if new_value != current_value:
            self.settings_manager.set("add_name", new_value)
            self.console.print(
                f"[green]✓ Name setting updated to: {'Yes' if new_value else 'No'}[/green]"
            )
            logger.info(f"Name setting changed to: {new_value}")
            input("\nPress Enter to continue...")
            return True
        else:
            self.console.print("[yellow]No change made[/yellow]")
            input("\nPress Enter to continue...")
            return False

    def _select_position(self) -> bool:
        """Allow user to select a photo position preset.

        Returns:
            True if position was changed, False otherwise
        """
        current_position = self.settings_manager.get_photo_position()

        self.console.print(f"\nCurrent position: [green]{current_position}[/green]\n")

        # Display available positions
        self.console.print("[bold]Available positions:[/bold]")
        position_list = list(PHOTO_POSITIONS.keys())
        for i, position in enumerate(position_list, 1):
            marker = "→" if position == current_position else " "
            self.console.print(f"  {marker} {i}) {position}")

        self.console.print()

        # Get user choice with single-key input
        valid_choices = [str(i) for i in range(1, len(position_list) + 1)]
        if READCHAR_AVAILABLE:
            self.console.print(f"[dim]Press a number key (1-{len(position_list)})...[/dim]", end="")
            choice = self._wait_for_number_key(valid_choices)
            self.console.print(f" {choice}")
        else:
            # Fallback
            from rich.prompt import Prompt
            choice = Prompt.ask(
                "Select a position",
                choices=valid_choices,
                default=str(position_list.index(current_position) + 1),
            )

        # Convert choice to position
        selected_position = position_list[int(choice) - 1]

        if selected_position != current_position:
            try:
                self.settings_manager.set_photo_position(selected_position)
                self.console.print(
                    f"[green]✓ Photo position updated to: {selected_position}[/green]"
                )
                logger.info(f"Photo position changed to: {selected_position}")
                input("\nPress Enter to continue...")
                return True
            except ValueError as e:
                self.console.print(f"[red]Error: {e}[/red]")
                input("\nPress Enter to continue...")
                return False
        else:
            self.console.print("[yellow]No change made[/yellow]")
            input("\nPress Enter to continue...")
            return False

    def _adjust_photo_size(self) -> bool:
        """Allow user to adjust photo size.

        Returns:
            True if size was changed, False otherwise
        """
        current_size = self.settings_manager.get("photo_size_cm", 2.5)

        self.console.print(f"\nCurrent size: [green]{current_size} cm[/green]\n")

        # Get new size with validation
        try:
            new_size = FloatPrompt.ask(
                "Enter new photo size in cm (1.0 - 10.0)",
                default=current_size,
            )

            # Validate range
            if new_size < 1.0 or new_size > 10.0:
                self.console.print(
                    "[red]Error: Size must be between 1.0 and 10.0 cm[/red]"
                )
                input("\nPress Enter to continue...")
                return False

            if new_size != current_size:
                self.settings_manager.set("photo_size_cm", new_size)
                self.console.print(
                    f"[green]✓ Photo size updated to: {new_size} cm[/green]"
                )
                logger.info(f"Photo size changed to: {new_size} cm")
                input("\nPress Enter to continue...")
                return True
            else:
                self.console.print("[yellow]No change made[/yellow]")
                input("\nPress Enter to continue...")
                return False

        except (ValueError, EOFError) as e:
            self.console.print(f"[red]Invalid input: {e}[/red]")
            input("\nPress Enter to continue...")
            return False

    def _select_text_position(self) -> bool:
        """Allow user to select text/name position.

        Returns:
            True if position was changed, False otherwise
        """
        current_position = self.settings_manager.get("name_position", "beside_photo")

        self.console.print(f"\nCurrent text position: [green]{current_position.replace('_', ' ').title()}[/green]\n")

        # Available text positions
        text_positions = {
            "1": ("beside_photo", "Beside Photo (left of photo)"),
            "2": ("center", "Center (middle of page)"),
            "3": ("left", "Left Side"),
            "4": ("right", "Right Side"),
        }

        # Display available positions
        self.console.print("[bold]Available text positions:[/bold]")
        for key, (pos_value, description) in text_positions.items():
            marker = "→" if pos_value == current_position else " "
            self.console.print(f"  {marker} {key}) {description}")

        self.console.print()

        # Get user choice with single-key input
        if READCHAR_AVAILABLE:
            self.console.print("[dim]Press a number key (1-4)...[/dim]", end="")
            choice = self._wait_for_number_key(["1", "2", "3", "4"])
            self.console.print(f" {choice}")
        else:
            # Fallback
            from rich.prompt import Prompt
            choice = Prompt.ask(
                "Select a position",
                choices=["1", "2", "3", "4"],
                default="1",
            )

        # Get selected position
        selected_position, description = text_positions[choice]

        if selected_position != current_position:
            self.settings_manager.set("name_position", selected_position)
            self.console.print(
                f"[green]✓ Text position updated to: {description}[/green]"
            )
            logger.info(f"Text position changed to: {selected_position}")
            input("\nPress Enter to continue...")
            return True
        else:
            self.console.print("[yellow]No change made[/yellow]")
            input("\nPress Enter to continue...")
            return False

"""Interactive settings menu for preview mode.

This module provides an interactive menu for adjusting worksheet
personalization settings during preview mode.
"""

import logging

from rich.console import Console
from rich.prompt import FloatPrompt
from rich.table import Table

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
    preview mode, mirroring all options from Einstellungen.command.

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
            self.console.print("  2) Adjust photo size")
            self.console.print("  3) Name distance from top")
            self.console.print("  4) Photo distance from top")
            self.console.print("  5) Photo distance from right")
            self.console.print("  [green]ENTER[/green] - Back to preview")
            self.console.print()

            # Get user choice with single-key input
            if READCHAR_AVAILABLE:
                self.console.print("[dim]Press a number key (1-5) or ENTER...[/dim]", end="")
                choice = self._wait_for_menu_key(["1", "2", "3", "4", "5"])
                self.console.print(f" {choice}")
            else:
                # Fallback to Enter-based input
                from rich.prompt import Prompt
                choice = Prompt.ask(
                    "Select an option",
                    choices=["1", "2", "3", "4", "5", ""],
                    default="",
                )

            if choice == "enter" or choice == "":
                # Exit menu
                break
            elif choice == "1":
                if self._toggle_add_name():
                    changes_made = True
            elif choice == "2":
                if self._adjust_photo_size():
                    changes_made = True
            elif choice == "3":
                if self._adjust_name_top_margin():
                    changes_made = True
            elif choice == "4":
                if self._adjust_photo_top_margin():
                    changes_made = True
            elif choice == "5":
                if self._adjust_photo_right_margin():
                    changes_made = True

        return changes_made

    def _wait_for_menu_key(self, valid_keys: list[str]) -> str:
        """Wait for user to press a number key or ENTER.

        Args:
            valid_keys: List of valid number key choices (e.g., ["1", "2", "3"])

        Returns:
            The pressed key as a string, or "enter" if ENTER was pressed
        """
        while True:
            key = readchar.readkey()
            if key == readchar.key.ENTER or key in ("\r", "\n"):
                return "enter"
            elif key in valid_keys:
                return key
            # Ignore invalid keys and wait for a valid one

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
        table.add_column("Setting", style="dim", width=25)
        table.add_column("Value", style="green")

        # Get current settings
        add_name = self.settings_manager.get("add_name", True)
        photo_size = self.settings_manager.get("photo_size_cm", 2.5)
        name_top = self.settings_manager.get("name_top_margin_percent", 2.5)
        photo_top = self.settings_manager.get("photo_top_margin_percent", 2.5)
        photo_right = self.settings_manager.get("photo_right_margin_percent", 3.5)

        # Add rows
        table.add_row("Add Name", "Yes" if add_name else "No")
        table.add_row("Photo Size", f"{photo_size} cm")
        table.add_row("Name Distance from Top", f"{self._get_margin_description(name_top)}")
        table.add_row("Photo Distance from Top", f"{self._get_margin_description(photo_top)}")
        table.add_row("Photo Distance from Right", f"{self._get_margin_description(photo_right)}")

        self.console.print(table)

    def _get_margin_description(self, value: float) -> str:
        """Get human-readable description for margin percentage.

        Args:
            value: Margin percentage value

        Returns:
            Descriptive string for the margin
        """
        margin_map = {
            0.0: "Kein Abstand",
            0.5: "Minimal",
            1.0: "Sehr schmal",
            1.5: "Schmal",
            2.5: "Normal",
            3.5: "Mittel",
            5.0: "Breit",
            7.0: "Sehr breit",
            10.0: "Maximal",
        }
        return margin_map.get(value, f"{value}%")

    def _toggle_add_name(self) -> bool:
        """Toggle the 'add name' setting.

        Returns:
            True if setting was changed, False otherwise
        """
        current_value = self.settings_manager.get("add_name", True)

        self.console.print(
            f"\nCurrent setting: [green]{'Yes' if current_value else 'No'}[/green]\n"
        )

        self.console.print("[bold]Add student names to worksheets?[/bold]")
        self.console.print("  1) Yes")
        self.console.print("  2) No")
        self.console.print()

        # Get user choice with single-key input
        if READCHAR_AVAILABLE:
            self.console.print("[dim]Press 1 or 2...[/dim]", end="")
            choice = self._wait_for_number_key(["1", "2"])
            self.console.print(f" {choice}")
        else:
            # Fallback
            from rich.prompt import Prompt
            choice = Prompt.ask(
                "Select an option",
                choices=["1", "2"],
                default="1" if current_value else "2",
            )

        new_value = choice == "1"

        if new_value != current_value:
            self.settings_manager.set("add_name", new_value)
            self.console.print(
                f"[green]✓ Name setting updated to: {'Yes' if new_value else 'No'}[/green]"
            )
            logger.info(f"Name setting changed to: {new_value}")
            return True
        else:
            self.console.print("[yellow]No change made[/yellow]")
            return False

    def _adjust_photo_size(self) -> bool:
        """Allow user to adjust photo size with 6 presets + custom.

        Returns:
            True if size was changed, False otherwise
        """
        current_size = self.settings_manager.get("photo_size_cm", 2.5)

        self.console.print(f"\nCurrent size: [green]{current_size} cm[/green]\n")

        # Display size presets (matching Einstellungen.command)
        self.console.print("[bold]Available photo sizes:[/bold]")
        size_presets = {
            "1": (1.5, "Klein"),
            "2": (2.0, "Mittel-Klein"),
            "3": (2.5, "Standard"),
            "4": (3.0, "Mittel-Groß"),
            "5": (3.5, "Groß"),
            "6": (4.0, "Sehr Groß"),
            "7": (None, "Benutzerdefiniert"),
        }

        for key, (size, description) in size_presets.items():
            marker = "→" if size == current_size else " "
            size_str = f"{size} cm" if size else "Custom"
            self.console.print(f"  {marker} {key}) {size_str} ({description})")

        self.console.print()

        # Get user choice with single-key input
        if READCHAR_AVAILABLE:
            self.console.print("[dim]Press a number key (1-7)...[/dim]", end="")
            choice = self._wait_for_number_key(["1", "2", "3", "4", "5", "6", "7"])
            self.console.print(f" {choice}")
        else:
            from rich.prompt import Prompt
            choice = Prompt.ask(
                "Select a size",
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="3",
            )

        # Handle custom input
        if choice == "7":
            try:
                new_size = FloatPrompt.ask(
                    "Enter photo size in cm (0.5 - 10.0)",
                    default=current_size,
                )
                if new_size < 0.5 or new_size > 10.0:
                    self.console.print(
                        "[red]Error: Size must be between 0.5 and 10.0 cm[/red]"
                    )
                    return False
            except (ValueError, EOFError):
                self.console.print("[red]Invalid input[/red]")
                return False
        else:
            new_size = size_presets[choice][0]

        if new_size != current_size:
            self.settings_manager.set("photo_size_cm", new_size)
            self.console.print(
                f"[green]✓ Photo size updated to: {new_size} cm[/green]"
            )
            logger.info(f"Photo size changed to: {new_size} cm")
            return True
        else:
            self.console.print("[yellow]No change made[/yellow]")
            return False

    def _adjust_name_top_margin(self) -> bool:
        """Allow user to adjust name distance from top (9 presets).

        Returns:
            True if margin was changed, False otherwise
        """
        return self._adjust_margin(
            setting_key="name_top_margin_percent",
            current_value=self.settings_manager.get("name_top_margin_percent", 2.5),
            title="Name-Abstand von oben ändern",
            description="vom oberen Blattrand"
        )

    def _adjust_photo_top_margin(self) -> bool:
        """Allow user to adjust photo distance from top (9 presets).

        Returns:
            True if margin was changed, False otherwise
        """
        return self._adjust_margin(
            setting_key="photo_top_margin_percent",
            current_value=self.settings_manager.get("photo_top_margin_percent", 2.5),
            title="Foto-Abstand von oben ändern",
            description="vom oberen Blattrand"
        )

    def _adjust_photo_right_margin(self) -> bool:
        """Allow user to adjust photo distance from right (9 presets).

        Returns:
            True if margin was changed, False otherwise
        """
        return self._adjust_margin(
            setting_key="photo_right_margin_percent",
            current_value=self.settings_manager.get("photo_right_margin_percent", 3.5),
            title="Foto-Abstand von rechts ändern",
            description="vom rechten Blattrand"
        )

    def _adjust_margin(self, setting_key: str, current_value: float, title: str, description: str) -> bool:
        """Generic method to adjust any margin setting.

        Args:
            setting_key: Settings key to modify
            current_value: Current margin value
            title: Display title for the menu
            description: Description text

        Returns:
            True if margin was changed, False otherwise
        """
        self.console.print(f"\nCurrent: [green]{self._get_margin_description(current_value)}[/green]\n")

        # Display margin presets (matching Einstellungen.command)
        self.console.print(f"[bold]Wählen Sie einen Abstand {description}:[/bold]")
        margin_presets = {
            "1": 0.0,
            "2": 0.5,
            "3": 1.0,
            "4": 1.5,
            "5": 2.5,
            "6": 3.5,
            "7": 5.0,
            "8": 7.0,
            "9": 10.0,
        }

        for key, value in margin_presets.items():
            marker = "→" if value == current_value else " "
            desc = self._get_margin_description(value)
            self.console.print(f"  {marker} {key}) {desc} ({value}%)")

        self.console.print()

        # Get user choice with single-key input
        if READCHAR_AVAILABLE:
            self.console.print("[dim]Press a number key (1-9)...[/dim]", end="")
            choice = self._wait_for_number_key(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
            self.console.print(f" {choice}")
        else:
            from rich.prompt import Prompt
            choice = Prompt.ask(
                "Select a margin",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                default="5",
            )

        new_value = margin_presets[choice]

        if new_value != current_value:
            self.settings_manager.set(setting_key, new_value)
            self.console.print(
                f"[green]✓ {title.split()[0]} updated to: {self._get_margin_description(new_value)}[/green]"
            )
            logger.info(f"{setting_key} changed to: {new_value}")
            return True
        else:
            self.console.print("[yellow]No change made[/yellow]")
            return False

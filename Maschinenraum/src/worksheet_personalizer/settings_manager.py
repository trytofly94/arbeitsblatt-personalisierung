"""Settings manager for user-friendly configuration.

This module provides a simple interface for managing user settings
stored in a JSON file.
"""

import json
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# Settings file location
SETTINGS_FILE = Path(__file__).parent.parent.parent / "settings.json"

# Name position options
NamePosition = Literal["beside_photo", "center", "left", "right"]


class SettingsManager:
    """Manages user settings for worksheet personalization.

    Attributes:
        photo_size_cm: Photo size (long side) in centimeters
        add_name: Whether to add student names
        name_position: Where to place the name on the worksheet
        font_size: Font size for student names
        photo_margin_cm: Margin from edge in centimeters
    """

    def __init__(self) -> None:
        """Initialize settings manager and load settings."""
        self.settings_file = SETTINGS_FILE
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load settings from JSON file.

        Returns:
            Dictionary with settings
        """
        if not self.settings_file.exists():
            logger.info("Settings file not found, creating default settings")
            return self._create_default_settings()

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
            logger.debug(f"Loaded settings from {self.settings_file}")
            return settings
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self._create_default_settings()

    def _create_default_settings(self) -> dict:
        """Create and save default settings.

        Returns:
            Dictionary with default settings
        """
        default_settings = {
            "photo_size_cm": 2.5,
            "add_name": True,
            "name_position": "beside_photo",
            "font_size": 12,
            "photo_margin_cm": 0.5
        }

        self._save_settings(default_settings)
        return default_settings

    def _save_settings(self, settings: dict) -> None:
        """Save settings to JSON file.

        Args:
            settings: Dictionary with settings to save
        """
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings saved to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get(self, key: str, default=None):
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value) -> None:
        """Set a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self._save_settings(self.settings)

    def get_all(self) -> dict:
        """Get all settings.

        Returns:
            Dictionary with all settings
        """
        return self.settings.copy()

    def update(self, new_settings: dict) -> None:
        """Update multiple settings at once.

        Args:
            new_settings: Dictionary with settings to update
        """
        self.settings.update(new_settings)
        self._save_settings(self.settings)


def interactive_settings_update() -> None:
    """Interactive CLI for updating settings."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm

    console = Console()
    manager = SettingsManager()

    console.print("\n[bold cyan]⚙️  Einstellungen für Arbeitsblatt-Personalisierung[/bold cyan]\n")

    current_settings = manager.get_all()

    # Display current settings
    console.print("[bold]Aktuelle Einstellungen:[/bold]")
    console.print(f"  📏 Fotogröße: [green]{current_settings['photo_size_cm']} cm[/green]")
    console.print(f"  ✏️  Name hinzufügen: [green]{'Ja' if current_settings['add_name'] else 'Nein'}[/green]")
    console.print(f"  📍 Name-Position: [green]{current_settings['name_position']}[/green]")
    console.print(f"  🔤 Schriftgröße: [green]{current_settings['font_size']}[/green]")
    console.print(f"  📐 Foto-Abstand: [green]{current_settings['photo_margin_cm']} cm[/green]\n")

    # Ask if user wants to change settings
    if not Confirm.ask("Möchten Sie die Einstellungen ändern?"):
        console.print("\n[yellow]Keine Änderungen vorgenommen.[/yellow]")
        return

    # Photo size
    photo_size = Prompt.ask(
        "Fotogröße (lange Seite in cm)",
        default=str(current_settings['photo_size_cm'])
    )
    try:
        photo_size = float(photo_size)
        if photo_size <= 0 or photo_size > 10:
            console.print("[red]Ungültige Größe! Verwende Standardwert.[/red]")
            photo_size = current_settings['photo_size_cm']
    except ValueError:
        console.print("[red]Ungültige Eingabe! Verwende Standardwert.[/red]")
        photo_size = current_settings['photo_size_cm']

    # Add name
    add_name = Confirm.ask(
        "Namen auf Arbeitsblatt hinzufügen?",
        default=current_settings['add_name']
    )

    # Name position (only if add_name is True)
    name_position = current_settings['name_position']
    if add_name:
        console.print("\n[bold]Name-Position:[/bold]")
        console.print("  1) neben dem Foto (rechts)")
        console.print("  2) mittig auf dem Arbeitsblatt")
        console.print("  3) links auf dem Arbeitsblatt")
        console.print("  4) rechts auf dem Arbeitsblatt")

        position_choice = Prompt.ask(
            "Wählen Sie eine Position",
            choices=["1", "2", "3", "4"],
            default="1"
        )

        position_map = {
            "1": "beside_photo",
            "2": "center",
            "3": "left",
            "4": "right"
        }
        name_position = position_map[position_choice]

    # Font size
    font_size = Prompt.ask(
        "Schriftgröße für Namen",
        default=str(current_settings['font_size'])
    )
    try:
        font_size = int(font_size)
        if font_size < 6 or font_size > 48:
            console.print("[red]Ungültige Größe! Verwende Standardwert.[/red]")
            font_size = current_settings['font_size']
    except ValueError:
        console.print("[red]Ungültige Eingabe! Verwende Standardwert.[/red]")
        font_size = current_settings['font_size']

    # Photo margin
    photo_margin = Prompt.ask(
        "Abstand des Fotos vom Rand (in cm)",
        default=str(current_settings['photo_margin_cm'])
    )
    try:
        photo_margin = float(photo_margin)
        if photo_margin < 0 or photo_margin > 5:
            console.print("[red]Ungültiger Abstand! Verwende Standardwert.[/red]")
            photo_margin = current_settings['photo_margin_cm']
    except ValueError:
        console.print("[red]Ungültige Eingabe! Verwende Standardwert.[/red]")
        photo_margin = current_settings['photo_margin_cm']

    # Update settings
    new_settings = {
        "photo_size_cm": photo_size,
        "add_name": add_name,
        "name_position": name_position,
        "font_size": font_size,
        "photo_margin_cm": photo_margin
    }

    manager.update(new_settings)

    console.print("\n[bold green]✓ Einstellungen erfolgreich gespeichert![/bold green]\n")
    console.print("[dim]Drücken Sie Enter zum Beenden...[/dim]")
    input()

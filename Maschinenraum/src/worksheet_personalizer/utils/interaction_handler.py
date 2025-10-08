"""Interaction handler for preview mode user interactions.

This module manages user input and system viewer integration for the
interactive preview feature.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console

from worksheet_personalizer.config import VIEWER_COMMANDS

logger = logging.getLogger(__name__)

# Try to import readchar, fall back to basic input if not available
try:
    import readchar

    READCHAR_AVAILABLE = True
except ImportError:
    READCHAR_AVAILABLE = False
    logger.warning(
        "readchar library not available, using fallback input method. "
        "Install readchar for better user experience: pip install readchar"
    )


class InteractionHandler:
    """Handles user interaction during preview mode.

    Manages opening files in system viewers and capturing keyboard input
    for preview navigation (ESC, ENTER, M for menu).

    Attributes:
        console: Rich Console instance for output formatting
    """

    def __init__(self, console: Console) -> None:
        """Initialize the interaction handler.

        Args:
            console: Rich Console instance for formatted output
        """
        self.console = console
        self._viewer_process: subprocess.Popen[bytes] | None = None

    def open_in_viewer(self, file_path: Path) -> subprocess.Popen[bytes] | None:
        """Open a file in the system's default viewer.

        Detects the operating system and uses the appropriate command
        to open the file in a non-blocking manner.

        Args:
            file_path: Path to the file to open

        Returns:
            Popen object for the viewer process, or None if opening failed

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get viewer command for current platform
        platform = sys.platform
        viewer_cmd = VIEWER_COMMANDS.get(platform)

        if not viewer_cmd:
            self.console.print(
                f"[yellow]Warning: No viewer command configured for platform '{platform}'[/yellow]"
            )
            self.console.print(f"[yellow]Preview file location: {file_path}[/yellow]")
            return None

        try:
            # Open file in system viewer (non-blocking)
            if platform == "win32":
                # Windows needs special handling
                process = subprocess.Popen(
                    ["cmd", "/c", "start", "", str(file_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # macOS and Linux
                process = subprocess.Popen(
                    [viewer_cmd, str(file_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            self._viewer_process = process
            logger.info(f"Opened preview in viewer: {file_path}")

            # Give the viewer a moment to start
            time.sleep(0.5)

            return process

        except Exception as e:
            logger.error(f"Failed to open file in viewer: {e}")
            self.console.print(
                f"[red]Error opening viewer: {e}[/red]"
            )
            self.console.print(
                f"[yellow]Please open manually: {file_path}[/yellow]"
            )
            return None

    def wait_for_input(self) -> str:
        """Wait for user keyboard input and return the action.

        Shows a prompt and waits for the user to press ESC, ENTER, or M.

        Returns:
            Action string: 'esc', 'enter', or 'menu'
        """
        self.console.print()
        self.console.print(
            "[bold cyan]Preview Actions:[/bold cyan]",
            style="bold",
        )
        self.console.print("  [green]ENTER[/green] - Continue with all students")
        self.console.print("  [yellow]M[/yellow] - Open settings menu")
        self.console.print("  [red]ESC[/red] - Cancel operation")
        self.console.print()

        if READCHAR_AVAILABLE:
            return self._wait_with_readchar()
        else:
            return self._wait_with_fallback()

    def _wait_with_readchar(self) -> str:
        """Wait for input using readchar library.

        Returns:
            Action string: 'esc', 'enter', or 'menu'
        """
        self.console.print("[dim]Press a key...[/dim]", end="")

        while True:
            try:
                key = readchar.readkey()

                # Handle different key representations
                if key == readchar.key.ESC or key == "\x1b":
                    self.console.print(" ESC")
                    return "esc"
                elif key == readchar.key.ENTER or key in ("\r", "\n"):
                    self.console.print(" ENTER")
                    return "enter"
                elif key.lower() == "m":
                    self.console.print(" M")
                    return "menu"
                else:
                    # Invalid key, continue waiting
                    continue

            except Exception as e:
                logger.error(f"Error reading key: {e}")
                # Fall back to basic input on error
                return self._wait_with_fallback()

    def _wait_with_fallback(self) -> str:
        """Wait for input using basic input() as fallback.

        Returns:
            Action string: 'esc', 'enter', or 'menu'
        """
        while True:
            response = input("Enter action (enter/m/esc): ").strip().lower()

            if response in ("", "enter"):
                return "enter"
            elif response == "m":
                return "menu"
            elif response == "esc":
                return "esc"
            else:
                self.console.print(
                    "[yellow]Invalid input. Please enter: enter, m, or esc[/yellow]"
                )

    def close_viewer(
        self, process: subprocess.Popen[bytes] | None = None, timeout: int = 5
    ) -> None:
        """Close the viewer process gracefully.

        Attempts to terminate the process, then kills it if it doesn't
        respond within the timeout.

        Args:
            process: Popen object to close. If None, uses the last opened viewer.
            timeout: Seconds to wait before force-killing the process
        """
        target_process = process or self._viewer_process

        if not target_process:
            return

        try:
            # Try graceful termination first
            target_process.terminate()

            # Wait for process to terminate
            try:
                target_process.wait(timeout=timeout)
                logger.debug("Viewer process terminated successfully")
            except subprocess.TimeoutExpired:
                # Force kill if it didn't terminate
                logger.warning(
                    f"Viewer process didn't terminate within {timeout}s, forcing kill"
                )
                target_process.kill()
                target_process.wait()

            if target_process == self._viewer_process:
                self._viewer_process = None

        except Exception as e:
            logger.warning(f"Error closing viewer process: {e}")

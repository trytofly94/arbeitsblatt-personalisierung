"""Arbeitsblatt-Personalisierung.

A CLI tool for automatically personalizing worksheets by adding student
photos and names.
"""

from worksheet_personalizer.core.personalizer import WorksheetPersonalizer
from worksheet_personalizer.models.student import Student

__version__ = "0.1.0"
__author__ = "Ihr Name"
__license__ = "MIT"

__all__ = ["WorksheetPersonalizer", "Student"]

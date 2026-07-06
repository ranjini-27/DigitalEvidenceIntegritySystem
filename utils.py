"""
utils.py
--------
Shared utility/helper functions used across the Digital Evidence Integrity
and Chain of Custody System.

Includes:
    - Screen clearing
    - Formatted table printing
    - Unique ID generation
    - Input validation helpers
    - File metadata extraction
"""

import os
import uuid
from datetime import datetime
from pathlib import Path


def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str):
    """Print a formatted section header to the CLI."""
    width = 70
    print("=" * width)
    print(title.center(width))
    print("=" * width)


def print_divider(char: str = "-", width: int = 70):
    """Print a simple divider line."""
    print(char * width)


def generate_evidence_id() -> str:
    """
    Generate a unique Evidence ID.
    Format: EVD-<8 hex chars from uuid4>
    """
    return f"EVD-{uuid.uuid4().hex[:8].upper()}"


def generate_audit_id() -> str:
    """
    Generate a unique Audit ID.
    Format: AUD-<8 hex chars from uuid4>
    """
    return f"AUD-{uuid.uuid4().hex[:8].upper()}"


def current_timestamp() -> str:
    """Return the current date and time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_non_empty(value: str, field_name: str) -> str:
    """
    Validate that a given input string is not empty.
    Repeats the prompt until valid input is provided.
    """
    while not value or not value.strip():
        print(f"[!] {field_name} cannot be empty. Please try again.")
        value = input(f"Enter {field_name}: ")
    return value.strip()


def validate_file_path(path_str: str) -> bool:
    """
    Validate that the provided path exists and is a file (not a directory).
    Returns True if valid, False otherwise.
    """
    path = Path(path_str.strip().strip('"'))
    if not path.exists():
        print(f"[!] Error: The path '{path}' does not exist.")
        return False
    if not path.is_file():
        print(f"[!] Error: The path '{path}' is not a file.")
        return False
    return True


def get_file_metadata(path_str: str) -> dict:
    """
    Extract metadata from a given file path.

    Returns a dictionary with:
        file_name, file_path, file_size (bytes), collected_date
    """
    path = Path(path_str.strip().strip('"')).resolve()
    stat_info = path.stat()

    metadata = {
        "file_name": path.name,
        "file_path": str(path),
        "file_size": stat_info.st_size,
        "collected_date": current_timestamp(),
    }
    return metadata


def format_file_size(size_bytes: int) -> str:
    """Convert a byte count into a human-readable string (KB, MB, GB)."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def print_table(headers: list, rows: list, col_widths: list = None):
    """
    Print a simple formatted table to the CLI.

    Args:
        headers: list of column header strings
        rows: list of tuples/lists containing row data
        col_widths: optional list of column widths; auto-calculated if None
    """
    if not col_widths:
        col_widths = []
        for i, header in enumerate(headers):
            max_data_width = max(
                [len(str(row[i])) for row in rows], default=0
            )
            col_widths.append(max(len(header), max_data_width, 10) + 2)

    header_line = "".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print_divider("-", sum(col_widths))

    if not rows:
        print("No records found.".center(sum(col_widths)))
        return

    for row in rows:
        line = "".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        print(line)


def pause():
    """Pause execution until the user presses Enter."""
    input("\nPress Enter to return to the main menu...")

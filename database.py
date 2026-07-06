"""
database.py
-----------
Handles all SQLite database operations for the Digital Evidence
Integrity and Chain of Custody System.

Responsible for:
    - Creating the database and required tables if they do not exist.
    - Providing a reusable connection object to other modules.
"""

import sqlite3
from pathlib import Path

# Database is stored inside the "database" folder, keeping the project
# structure clean and organized.
DB_DIR = Path(__file__).parent / "database"
DB_PATH = DB_DIR / "evidence.db"


def get_connection() -> sqlite3.Connection:
    """
    Create (if needed) and return a connection to the SQLite database.
    Ensures the 'database' directory exists before connecting.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """
    Create the 'evidence' and 'audit_log' tables if they do not already
    exist. This function is safe to call every time the program starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Evidence table: stores core evidence metadata and hash
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id     TEXT PRIMARY KEY,
            case_id         TEXT NOT NULL,
            investigator    TEXT NOT NULL,
            file_name       TEXT NOT NULL,
            file_path       TEXT NOT NULL,
            file_size       INTEGER NOT NULL,
            sha256_hash     TEXT NOT NULL,
            collected_date  TEXT NOT NULL
        )
        """
    )

    # Audit log table: stores the chain of custody trail for each
    # evidence item. Linked to 'evidence' via foreign key.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            audit_id        TEXT PRIMARY KEY,
            evidence_id     TEXT NOT NULL,
            investigator    TEXT NOT NULL,
            action          TEXT NOT NULL,
            result          TEXT NOT NULL,
            remarks         TEXT,
            timestamp       TEXT NOT NULL,
            FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
        )
        """
    )

    conn.commit()
    conn.close()

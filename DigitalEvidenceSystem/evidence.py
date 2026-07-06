"""
evidence.py
-----------
Handles registration and retrieval of digital evidence records.

Responsibilities:
    - Register new evidence (read metadata, compute hash, store in DB).
    - View all registered evidence in a summary table.
    - View full details for a single evidence item.

This module never modifies or writes to the original evidence file;
it only reads metadata and computes a hash, preserving forensic integrity.
"""

from database import get_connection
from hashing import calculate_sha256
from audit import log_action
from utils import (
    generate_evidence_id,
    validate_non_empty,
    validate_file_path,
    get_file_metadata,
    format_file_size,
    print_table,
    print_header,
)


def register_evidence():
    """
    CLI workflow to register a new piece of digital evidence.

    Steps:
        1. Prompt for file path, investigator name, and case ID.
        2. Validate the file exists and is readable.
        3. Extract file metadata.
        4. Calculate SHA-256 hash.
        5. Store the record in the database.
        6. Log the registration event in the chain of custody.
    """
    print_header("REGISTER NEW EVIDENCE")

    # --- Gather and validate input ---
    file_path = input("Enter full path of the evidence file: ").strip()
    if not validate_file_path(file_path):
        return

    investigator = validate_non_empty(
        input("Enter Investigator Name: "), "Investigator Name"
    )
    case_id = validate_non_empty(input("Enter Case ID: "), "Case ID")

    try:
        # --- Extract metadata (read-only) ---
        metadata = get_file_metadata(file_path)

        print("\nCalculating SHA-256 hash... please wait.")
        sha256_hash = calculate_sha256(metadata["file_path"])

        evidence_id = generate_evidence_id()

        # --- Store in database ---
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO evidence
                (evidence_id, case_id, investigator, file_name, file_path,
                 file_size, sha256_hash, collected_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                case_id,
                investigator,
                metadata["file_name"],
                metadata["file_path"],
                metadata["file_size"],
                sha256_hash,
                metadata["collected_date"],
            ),
        )
        conn.commit()
        conn.close()

        # --- Log chain of custody entry ---
        log_action(
            evidence_id=evidence_id,
            investigator=investigator,
            action="Registered Evidence",
            result="Success",
            remarks="Evidence registered and SHA-256 hash calculated.",
        )

        # --- Confirmation output ---
        print("\n[OK] Evidence registered successfully!")
        print_header("EVIDENCE SUMMARY")
        print(f"Evidence ID     : {evidence_id}")
        print(f"Case ID         : {case_id}")
        print(f"Investigator    : {investigator}")
        print(f"File Name       : {metadata['file_name']}")
        print(f"File Path       : {metadata['file_path']}")
        print(f"File Size       : {format_file_size(metadata['file_size'])}")
        print(f"SHA-256 Hash    : {sha256_hash}")
        print(f"Collected Date  : {metadata['collected_date']}")

    except FileNotFoundError as e:
        print(f"[!] Error: {e}")
    except IOError as e:
        print(f"[!] Error reading file: {e}")
    except Exception as e:
        print(f"[!] Unexpected error during registration: {e}")


def get_all_evidence():
    """Return all evidence records from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence ORDER BY collected_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_evidence_by_id(evidence_id: str):
    """Return a single evidence record by its Evidence ID, or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def view_all_evidence():
    """
    CLI workflow: display all registered evidence in a summary table,
    then optionally show full details for a selected Evidence ID.
    """
    print_header("REGISTERED EVIDENCE")
    records = get_all_evidence()

    if not records:
        print("No evidence has been registered yet.")
        return

    headers = ["Evidence ID", "Case ID", "File Name", "Investigator", "Collected Date"]
    rows = [
        (r["evidence_id"], r["case_id"], r["file_name"],
         r["investigator"], r["collected_date"])
        for r in records
    ]
    print_table(headers, rows)

    choice = input(
        "\nEnter an Evidence ID to view full details (or press Enter to skip): "
    ).strip()

    if choice:
        view_evidence_details(choice)


def view_evidence_details(evidence_id: str):
    """Display complete details for a single evidence record."""
    record = get_evidence_by_id(evidence_id)

    if not record:
        print(f"[!] No evidence found with ID '{evidence_id}'.")
        return

    print_header(f"EVIDENCE DETAILS - {evidence_id}")
    print(f"Evidence ID     : {record['evidence_id']}")
    print(f"Case ID         : {record['case_id']}")
    print(f"Investigator    : {record['investigator']}")
    print(f"File Name       : {record['file_name']}")
    print(f"File Path       : {record['file_path']}")
    print(f"File Size       : {format_file_size(record['file_size'])}")
    print(f"SHA-256 Hash    : {record['sha256_hash']}")
    print(f"Collected Date  : {record['collected_date']}")

"""
audit.py
--------
Manages the Chain of Custody audit trail.

Every meaningful action performed on a piece of evidence (registration,
verification, viewing, report generation, etc.) is logged here so that
a complete, tamper-evident history can be reconstructed at any time.
"""

from database import get_connection
from utils import generate_audit_id, current_timestamp, print_table, print_header


def log_action(evidence_id: str, investigator: str, action: str,
                result: str, remarks: str = ""):
    """
    Insert a new entry into the audit_log table.

    Args:
        evidence_id: The evidence item this action relates to.
        investigator: Name of the investigator performing the action.
        action: Short description of the action (e.g. "Registered Evidence").
        result: Outcome of the action (e.g. "Success", "Integrity Verified").
        remarks: Optional free-text notes.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_log
            (audit_id, evidence_id, investigator, action, result, remarks, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            generate_audit_id(),
            evidence_id,
            investigator,
            action,
            result,
            remarks,
            current_timestamp(),
        ),
    )

    conn.commit()
    conn.close()


def get_custody_log(evidence_id: str):
    """
    Retrieve the complete chain of custody history for a given
    Evidence ID, ordered chronologically.

    Returns:
        A list of sqlite3.Row objects representing each audit entry.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT audit_id, evidence_id, investigator, action, result, remarks, timestamp
        FROM audit_log
        WHERE evidence_id = ?
        ORDER BY timestamp ASC
        """,
        (evidence_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def view_chain_of_custody():
    """
    CLI workflow: prompt for an Evidence ID and display its complete
    chain of custody history in a formatted table.
    """
    print_header("VIEW CHAIN OF CUSTODY")
    evidence_id = input("Enter Evidence ID: ").strip()

    if not evidence_id:
        print("[!] Evidence ID cannot be empty.")
        return

    logs = get_custody_log(evidence_id)

    if not logs:
        print(f"\nNo chain of custody records found for Evidence ID '{evidence_id}'.")
        print("Please verify the Evidence ID is correct.")
        return

    print(f"\nChain of Custody for Evidence ID: {evidence_id}\n")
    headers = ["Audit ID", "Date/Time", "Investigator", "Action", "Result", "Remarks"]
    rows = [
        (log["audit_id"], log["timestamp"], log["investigator"],
         log["action"], log["result"], log["remarks"] or "-")
        for log in logs
    ]
    print_table(headers, rows)

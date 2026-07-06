"""
report.py
---------
Generates a professional PDF forensic report for a given piece of
evidence using the ReportLab library.

The report includes:
    - Evidence information (ID, case, investigator, file metadata)
    - SHA-256 hash
    - Latest verification status
    - Complete chain of custody history
"""

from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from evidence import get_evidence_by_id
from audit import get_custody_log
from utils import format_file_size, current_timestamp

REPORTS_DIR = Path(__file__).parent / "reports"


def _get_latest_verification_status(logs):
    """
    Scan the chain of custody logs in reverse to find the most recent
    verification result. Returns 'Not Yet Verified' if none exists.
    """
    for entry in reversed(logs):
        if entry["action"] == "Verified Integrity":
            return f"{entry['result']} (as of {entry['timestamp']})"
    return "Not Yet Verified"


def generate_report():
    """
    CLI workflow to generate a PDF forensic report for a given
    Evidence ID.
    """
    print("\n" + "=" * 70)
    print("GENERATE FORENSIC REPORT".center(70))
    print("=" * 70)

    evidence_id = input("Enter Evidence ID to generate report for: ").strip()

    if not evidence_id:
        print("[!] Evidence ID cannot be empty.")
        return

    record = get_evidence_by_id(evidence_id)
    if not record:
        print(f"[!] No evidence found with ID '{evidence_id}'.")
        return

    logs = get_custody_log(evidence_id)

    # Ensure the reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = REPORTS_DIR / f"Forensic_Report_{evidence_id}_{timestamp_tag}.pdf"

    try:
        _build_pdf(record, logs, output_path)
        print(f"\n[OK] Forensic report generated successfully!")
        print(f"Saved at: {output_path.resolve()}")
    except Exception as e:
        print(f"[!] Failed to generate report: {e}")


def _build_pdf(record, logs, output_path: Path):
    """
    Construct and save the PDF document using ReportLab's platypus
    layout engine.

    Args:
        record: sqlite3.Row for the evidence item.
        logs: list of sqlite3.Row chain-of-custody entries.
        output_path: Path where the PDF should be saved.
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=8,
        textColor=colors.HexColor("#1a1a2e"),
    )
    normal_style = styles["Normal"]
    mono_style = ParagraphStyle(
        "MonoStyle",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9,
        wordWrap="CJK",
    )

    elements = []

    # --- Title ---
    elements.append(Paragraph("Digital Forensic Evidence Report", title_style))
    elements.append(
        Paragraph(
            f"Generated on {current_timestamp()} | "
            "Digital Evidence Integrity and Chain of Custody System",
            subtitle_style,
        )
    )

    # --- Evidence Information Table ---
    elements.append(Paragraph("1. Evidence Information", heading_style))

    info_data = [
        ["Evidence ID", record["evidence_id"]],
        ["Case ID", record["case_id"]],
        ["Investigator", record["investigator"]],
        ["File Name", record["file_name"]],
        ["File Path", record["file_path"]],
        ["File Size", format_file_size(record["file_size"])],
        ["Date/Time Collected", record["collected_date"]],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 11 * cm])
    info_table.setStyle(_default_table_style())
    elements.append(info_table)

    # --- SHA-256 Hash ---
    elements.append(Paragraph("2. SHA-256 Hash", heading_style))
    elements.append(Paragraph(record["sha256_hash"], mono_style))

    # --- Verification Status ---
    elements.append(Paragraph("3. Verification Status", heading_style))
    status = _get_latest_verification_status(logs)
    elements.append(Paragraph(status, normal_style))

    # --- Chain of Custody ---
    elements.append(Paragraph("4. Chain of Custody History", heading_style))

    if logs:
        custody_data = [["Date/Time", "Investigator", "Action", "Result", "Remarks"]]
        for entry in logs:
            custody_data.append(
                [
                    entry["timestamp"],
                    entry["investigator"],
                    entry["action"],
                    entry["result"],
                    Paragraph(entry["remarks"] or "-", normal_style),
                ]
            )
        custody_table = Table(
            custody_data, colWidths=[3.2 * cm, 3 * cm, 3.3 * cm, 3 * cm, 3.5 * cm]
        )
        custody_table.setStyle(_custody_table_style())
        elements.append(custody_table)
    else:
        elements.append(Paragraph("No chain of custody records found.", normal_style))

    doc.build(elements)


def _default_table_style() -> TableStyle:
    """Return the reusable table style for the evidence info table."""
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef1f7")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
    )


def _custody_table_style() -> TableStyle:
    """Return the reusable table style for the chain-of-custody table."""
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f8fb")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )

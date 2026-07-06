"""
main.py
-------
Entry point for the Digital Evidence Integrity and Chain of Custody
System.

This is a Command Line Interface (CLI) only application built for
MSc Digital Forensics coursework. It simulates a simplified real-world
digital forensic evidence management workflow:

    1. Register Evidence
    2. View Evidence
    3. Verify Evidence Integrity
    4. View Chain of Custody
    5. Generate Forensic Report
    6. Exit

Run with:
    python main.py
"""

import sys

from database import initialize_database
from evidence import register_evidence, view_all_evidence
from verify import verify_evidence_integrity
from audit import view_chain_of_custody
from report import generate_report
from utils import clear_screen, print_header, pause


MENU_TEXT = """
  [1] Register Evidence
  [2] View Evidence
  [3] Verify Evidence Integrity
  [4] View Chain of Custody
  [5] Generate Forensic Report
  [6] Exit
"""


def display_main_menu():
    """Print the main menu banner and options."""
    clear_screen()
    print_header("DIGITAL EVIDENCE INTEGRITY & CHAIN OF CUSTODY SYSTEM")
    print("  MSc Digital Forensics - Evidence Management Simulation")
    print(MENU_TEXT)


def main():
    """Main application loop."""
    # Ensure database and tables exist before anything else runs
    try:
        initialize_database()
    except Exception as e:
        print(f"[FATAL] Could not initialize database: {e}")
        sys.exit(1)

    while True:
        display_main_menu()
        choice = input("Select an option (1-6): ").strip()

        try:
            if choice == "1":
                clear_screen()
                register_evidence()
                pause()

            elif choice == "2":
                clear_screen()
                view_all_evidence()
                pause()

            elif choice == "3":
                clear_screen()
                verify_evidence_integrity()
                pause()

            elif choice == "4":
                clear_screen()
                view_chain_of_custody()
                pause()

            elif choice == "5":
                clear_screen()
                generate_report()
                pause()

            elif choice == "6":
                clear_screen()
                print("Exiting Digital Evidence Integrity System. Goodbye.")
                sys.exit(0)

            else:
                print("[!] Invalid option. Please choose a number between 1 and 6.")
                pause()

        except KeyboardInterrupt:
            print("\n\n[!] Operation cancelled by user.")
            pause()
        except Exception as e:
            # Catch-all so unexpected errors never crash the whole program
            print(f"[!] An unexpected error occurred: {e}")
            pause()


if __name__ == "__main__":
    main()

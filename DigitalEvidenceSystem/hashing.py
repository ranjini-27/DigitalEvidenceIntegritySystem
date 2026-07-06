"""
hashing.py
----------
Handles cryptographic hashing operations for evidence files.

The system uses SHA-256 exclusively, as it is the industry-standard
algorithm recommended in digital forensics for verifying evidence
integrity (NIST SP 800-101, ISO/IEC 27037).

IMPORTANT: This module only READS files to compute hashes. It never
modifies, writes to, or deletes the original evidence file, preserving
forensic soundness.
"""

import hashlib
from pathlib import Path


CHUNK_SIZE = 65536  # 64 KB chunks - efficient for large evidence files


def calculate_sha256(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a file without modifying it.

    Args:
        file_path: Path to the evidence file.

    Returns:
        The SHA-256 hash as a lowercase hexadecimal string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Evidence file not found: {file_path}")

    sha256_hash = hashlib.sha256()

    # Open the file strictly in read-only binary mode ("rb") to guarantee
    # the original evidence is never altered during hashing.
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sha256_hash.update(chunk)
    except IOError as e:
        raise IOError(f"Unable to read evidence file: {e}")

    return sha256_hash.hexdigest()


def compare_hashes(hash_a: str, hash_b: str) -> bool:
    """
    Securely compare two SHA-256 hash strings.

    Uses hmac.compare_digest via hashlib-safe comparison to avoid
    timing attacks, though this is primarily a forensic integrity
    check rather than a security-critical authentication step.

    Args:
        hash_a: First hash string.
        hash_b: Second hash string.

    Returns:
        True if hashes match exactly, False otherwise.
    """
    import hmac
    return hmac.compare_digest(hash_a.lower().strip(), hash_b.lower().strip())

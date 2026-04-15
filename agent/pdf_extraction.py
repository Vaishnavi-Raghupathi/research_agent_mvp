import os
import fitz  # PyMuPDF
import re
from collections import defaultdict


def extract_pdf(path):
    """
    Extract text from PDF. Returns dict with 'text' and 'equations' keys.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Cannot read '{path}'. Check permissions.")

    try:
        doc = fitz.open(path)
    except Exception:
        raise ValueError(f"Could not open PDF: {path}")

    plain_text = ""
    for page in doc:
        plain_text += page.get_text() + "\n"
    doc.close()

    equations = extract_equations_from_text(plain_text)

    return {
        "text": plain_text,
        "equations": equations
    }


def extract_pdf_text_only(path):
    """Legacy helper — returns just the text string."""
    return extract_pdf(path)["text"]


def extract_equations_from_text(text):
    """
    Extract equations from plain text using regex patterns.
    This is a placeholder implementation.
    """
    equations = []
    # Example: Extract lines containing '=' as potential equations
    for line in text.splitlines():
        if '=' in line:
            equations.append(line.strip())
    return equations
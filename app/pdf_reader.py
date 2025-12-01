"""
PDF Reader Module with Circular Classification

Extracts text from uploaded PDF files using pdfplumber
and includes a heuristic classifier to detect whether
the document is a Government Circular or a general PDF.
"""

import pdfplumber
from typing import Union, Tuple, Dict
import io


# -------------------------------------------------------------------
# 🔍 1. Government Circular Detector (Heuristic Rule-based)
# -------------------------------------------------------------------

def detect_government_circular(text: str) -> Dict:
    """
    Detect whether the given text looks like a Government Circular.

    Returns dict with:
        - is_circular: bool
        - confidence: float (0–1)
        - reason: explanation
    """

    if not text or len(text.strip()) == 0:
        return {
            "is_circular": False,
            "confidence": 0.0,
            "reason": "The document contains no readable text."
        }

    # Convert to lowercase for easy matching
    t = text.lower()

    # Common circular keywords
    gov_keywords = [
        "government of", "govt. of", "g.o.", "department of",
        "ministry of", "secretariat", "circular", "proceedings",
        "office order", "official memorandum", "directorate",
        "education department", "school education", "revenue department",
        "public notice", "administrative"
    ]

    # Points system
    score = 0
    max_score = len(gov_keywords)

    for word in gov_keywords:
        if word in t:
            score += 1

    confidence = round(score / max_score, 2)

    # Classification threshold
    is_circular = confidence >= 0.20  # at least 20% matching

    reason = (
        f"Matched {score} keywords out of {max_score}. "
        f"Confidence: {confidence}"
    )

    return {
        "is_circular": is_circular,
        "confidence": confidence,
        "reason": reason
    }


# -------------------------------------------------------------------
# 📄 2. Extract Text (Normal)
# -------------------------------------------------------------------

def extract_text(pdf_file_path: Union[str, io.BytesIO]) -> str:
    """
    Extract plain text from PDF using pdfplumber.
    """
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            extracted_text = []

            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()

                if page_text:
                    extracted_text.append(page_text.strip())
                else:
                    print(f"Warning: Page {page_num} is empty or unreadable.")

            return "\n\n".join(extracted_text).strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


# -------------------------------------------------------------------
# 📄 3. Extract Text with Layout
# -------------------------------------------------------------------

def extract_text_with_layout(pdf_file_path: Union[str, io.BytesIO]) -> str:
    """
    Extracts text while attempting to preserve layout.
    """
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            extracted_text = []

            for page in pdf.pages:
                page_text = page.extract_text(
                    layout=True,
                    x_tolerance=3,
                    y_tolerance=3
                )
                if page_text:
                    extracted_text.append(page_text.strip())

            return "\n\n".join(extracted_text).strip()

    except Exception as e:
        raise Exception(f"Error extracting text with layout: {str(e)}")


# -------------------------------------------------------------------
# 📄 4. PDF Info
# -------------------------------------------------------------------

def get_pdf_info(pdf_file_path: Union[str, io.BytesIO]) -> dict:
    """
    Returns metadata and page count of the PDF.
    """
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            info = {
                'page_count': len(pdf.pages),
                'metadata': pdf.metadata if pdf.metadata else {},
            }
            return info

    except Exception as e:
        raise Exception(f"Error getting PDF info: {str(e)}")


# -------------------------------------------------------------------
# 🧪 5. Test (Command Line)
# -------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        print(f"Testing PDF: {test_pdf}")
        print("=" * 50)

        info = get_pdf_info(test_pdf)
        print(f"Pages: {info['page_count']}")
        print(f"Metadata: {info['metadata']}")
        print("=" * 50)

        text = extract_text(test_pdf)
        print(f"Extracted {len(text)} characters\n")

        print("Detecting Circular...")
        print(detect_government_circular(text))

    else:
        print("Usage: python pdf_reader.py <file.pdf>")

"""Text Cleaner Module

Responsible for preprocessing text extracted from PDFs.
Handles English + ALL Indian languages, removes headers/footers, and normalizes whitespace.
"""

import re
from typing import List, Optional


def clean_text(text: str, remove_page_numbers: bool = True) -> str:
    if not text or not text.strip():
        return ""
    
    # Step 1: Remove common headers/footers patterns
    text = remove_headers_footers(text)
    
    # Step 2: Remove page numbers if requested
    if remove_page_numbers:
        text = remove_page_numbers_pattern(text)
    
    # Step 3: Normalize whitespace
    text = normalize_whitespace(text)
    
    # Step 4: Remove special characters (updated to ALL Indian languages)
    text = remove_special_characters(text)
    
    # Step 5: Fix common PDF extraction issues
    text = fix_pdf_artifacts(text)
    
    # Step 6: Final cleanup
    return text.strip()


def remove_headers_footers(text: str) -> str:
    lines = text.split('\n')
    cleaned_lines = []

    header_footer_patterns = [
        r'^Page\s+\d+',
        r'^\d+\s*$',
        r'^Page\s+\d+\s+of\s+\d+',
        r'^\[?Page\s*\d+\]?',
        r'^Government of.*',
        r'^Ministry of.*',
        r'^Department of.*',
        r'^Annexure.*',
        r'^Appendix.*',
        r'^\s*[-_=]{3,}\s*$',
        r'^\s*[•·\*]{3,}\s*$',
    ]
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        
        if not any(re.match(p, stripped, re.IGNORECASE) for p in header_footer_patterns):
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def remove_page_numbers_pattern(text: str) -> str:
    patterns = [
        r'^\s*\d+\s*$',
        r'\n\s*\d+\s*\n',
        r'^\d+\s*\|',
        r'\|\s*\d+\s*$',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '\n', text, flags=re.MULTILINE)
    
    return text


def normalize_whitespace(text: str) -> str:
    text = text.replace('\t', ' ')
    text = re.sub(r' +', ' ', text)

    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines]

    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +\n', '\n', text)

    return text


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Now supports ALL Indian languages + English.
    """
    indian_unicode = (
        r"\u0900-\u097F"  # Hindi - Devanagari
        r"\u0B80-\u0BFF"  # Tamil
        r"\u0C00-\u0C7F"  # Telugu
        r"\u0C80-\u0CFF"  # Kannada
        r"\u0D00-\u0D7F"  # Malayalam
        r"\u0980-\u09FF"  # Bengali
        r"\u0A00-\u0A7F"  # Punjabi
        r"\u0A80-\u0AFF"  # Gujarati
        r"\u0B00-\u0B7F"  # Odia
    )

    if keep_punctuation:
        pattern = rf"[^{indian_unicode}a-zA-Z0-9\s\n.,!?;:'\"()\-–—/]"
    else:
        pattern = rf"[^{indian_unicode}a-zA-Z0-9\s\n]"

    text = re.sub(pattern, " ", text)
    return re.sub(r" +", " ", text)


def fix_pdf_artifacts(text: str) -> str:
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    text = re.sub(r'\.{4,}', '...', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])([a-zA-Z])', r'\1 \2', text)
    return text


def remove_common_noise(text: str, noise_phrases: Optional[List[str]] = None) -> str:
    default_noise = [
        "Confidential",
        "Internal Use Only",
        "Not for Publication",
        "Draft Copy",
        "For Official Use",
    ]
    
    phrases = noise_phrases if noise_phrases else default_noise
    for phrase in phrases:
        text = re.sub(re.escape(phrase), "", text, flags=re.IGNORECASE)
    return text


def get_text_statistics(text: str) -> dict:
    stats = {
        "character_count": len(text),
        "character_count_no_spaces": len(text.replace(' ', '').replace('\n', '')),
        "word_count": len(text.split()),
        "line_count": len(text.split('\n')),
        "paragraph_count": len([p for p in text.split("\n\n") if p.strip()]),
    }

    indian_pattern = (
        r"[\u0900-\u097F"  # Hindi
        r"\u0B80-\u0BFF"  # Tamil
        r"\u0C00-\u0C7F"  # Telugu
        r"\u0C80-\u0CFF"  # Kannada
        r"\u0D00-\u0D7F"  # Malayalam
        r"\u0980-\u09FF"  # Bengali
        r"\u0A00-\u0A7F"  # Punjabi
        r"\u0A80-\u0AFF"  # Gujarati
        r"\u0B00-\u0B7F"  # Odia
        r"]"
    )

    stats["has_indian_language"] = bool(re.search(indian_pattern, text))
    stats["has_english"] = bool(re.search(r"[a-zA-Z]", text))

    return stats

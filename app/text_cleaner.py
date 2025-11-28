"""Text Cleaner Module

Responsible for preprocessing text extracted from PDFs.
Handles English and Tamil text, removes headers/footers, and normalizes whitespace.
"""

import re
from typing import List, Optional


def clean_text(text: str, remove_page_numbers: bool = True) -> str:
    """
    Clean and preprocess text from PDF documents.
    Removes headers/footers, normalizes whitespace, supports English and Tamil.
    
    Args:
        text: Raw text extracted from PDF
        remove_page_numbers: Whether to remove page numbers (default: True)
        
    Returns:
        str: Cleaned and normalized text
        
    Example:
        >>> raw_text = "Page 1\n\nGovernment Circular\n\nContent here...\n\nPage 2"
        >>> clean = clean_text(raw_text)
        >>> print(clean)
    """
    if not text or not text.strip():
        return ""
    
    # Step 1: Remove common headers/footers patterns
    text = remove_headers_footers(text)
    
    # Step 2: Remove page numbers if requested
    if remove_page_numbers:
        text = remove_page_numbers_pattern(text)
    
    # Step 3: Normalize whitespace
    text = normalize_whitespace(text)
    
    # Step 4: Remove special characters (keep Tamil and English)
    text = remove_special_characters(text)
    
    # Step 5: Fix common PDF extraction issues
    text = fix_pdf_artifacts(text)
    
    # Step 6: Final cleanup
    text = text.strip()
    
    return text


def remove_headers_footers(text: str) -> str:
    """
    Remove common header and footer patterns from government documents.
    
    Args:
        text: Input text
        
    Returns:
        str: Text with headers/footers removed
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    # Common header/footer patterns in government circulars
    header_footer_patterns = [
        r'^Page\s+\d+',  # Page X
        r'^\d+\s*$',  # Standalone numbers
        r'^Page\s+\d+\s+of\s+\d+',  # Page X of Y
        r'^\[?Page\s*\d+\]?',  # [Page X]
        r'^Government of.*',  # Government header (if at top repeatedly)
        r'^Ministry of.*',  # Ministry header
        r'^Department of.*',  # Department header
        r'^Annexure.*',  # Annexure headers
        r'^Appendix.*',  # Appendix headers
        r'^\s*[-_=]{3,}\s*$',  # Horizontal lines
        r'^\s*[•·\*]{3,}\s*$',  # Bullet separators
    ]
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines temporarily
        if not stripped:
            cleaned_lines.append(line)
            continue
        
        # Check if line matches any header/footer pattern
        is_header_footer = False
        for pattern in header_footer_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                is_header_footer = True
                break
        
        # Keep line if it's not a header/footer
        if not is_header_footer:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def remove_page_numbers_pattern(text: str) -> str:
    """
    Remove page numbers from text.
    
    Args:
        text: Input text
        
    Returns:
        str: Text with page numbers removed
    """
    # Pattern for standalone page numbers (on their own line or at start/end)
    patterns = [
        r'^\s*\d+\s*$',  # Standalone number on line
        r'\n\s*\d+\s*\n',  # Number between newlines
        r'^\d+\s*\|',  # Number with pipe
        r'\|\s*\d+\s*$',  # Pipe with number at end
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '\n', text, flags=re.MULTILINE)
    
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    - Replace multiple spaces with single space
    - Replace multiple newlines with maximum 2 newlines
    - Remove trailing/leading whitespace from lines
    
    Args:
        text: Input text
        
    Returns:
        str: Text with normalized whitespace
    """
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Clean up each line
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    
    # Join lines back
    text = '\n'.join(cleaned_lines)
    
    # Replace more than 2 consecutive newlines with exactly 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove spaces before newlines
    text = re.sub(r' +\n', '\n', text)
    
    return text


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Remove special characters while keeping English, Tamil, and basic punctuation.
    
    Args:
        text: Input text
        keep_punctuation: Whether to keep basic punctuation marks
        
    Returns:
        str: Text with special characters removed
    """
    if keep_punctuation:
        # Keep:
        # - English letters (a-z, A-Z)
        # - Tamil Unicode range (\u0B80-\u0BFF)
        # - Numbers (0-9)
        # - Basic punctuation (.,!?;:()"'-)
        # - Whitespace (\s)
        # - Newlines (\n)
        pattern = r'[^a-zA-Z0-9\u0B80-\u0BFF\s\n.,!?;:\'"()\-–—/]'
    else:
        # Keep only letters, numbers, and whitespace
        pattern = r'[^a-zA-Z0-9\u0B80-\u0BFF\s\n]'
    
    text = re.sub(pattern, ' ', text)
    
    # Clean up any double spaces created
    text = re.sub(r' +', ' ', text)
    
    return text


def fix_pdf_artifacts(text: str) -> str:
    """
    Fix common PDF extraction artifacts.
    
    Args:
        text: Input text
        
    Returns:
        str: Text with artifacts fixed
    """
    # Fix broken words with hyphens at line breaks
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Remove zero-width spaces and other invisible characters
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    
    # Fix multiple periods
    text = re.sub(r'\.{4,}', '...', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])([a-zA-Z])', r'\1 \2', text)
    
    return text


def remove_common_noise(text: str, noise_phrases: Optional[List[str]] = None) -> str:
    """
    Remove common noise phrases from government documents.
    
    Args:
        text: Input text
        noise_phrases: Optional list of custom phrases to remove
        
    Returns:
        str: Text with noise removed
    """
    # Default noise phrases in government circulars
    default_noise = [
        "Confidential",
        "Internal Use Only",
        "Not for Publication",
        "Draft Copy",
        "For Official Use",
    ]
    
    phrases = noise_phrases if noise_phrases else default_noise
    
    for phrase in phrases:
        # Case-insensitive removal
        text = re.sub(re.escape(phrase), '', text, flags=re.IGNORECASE)
    
    return text


def get_text_statistics(text: str) -> dict:
    """
    Get statistics about the cleaned text.
    
    Args:
        text: Input text
        
    Returns:
        dict: Statistics including character count, word count, etc.
    """
    stats = {
        'character_count': len(text),
        'character_count_no_spaces': len(text.replace(' ', '').replace('\n', '')),
        'word_count': len(text.split()),
        'line_count': len(text.split('\n')),
        'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
    }
    
    # Detect language presence
    has_tamil = bool(re.search(r'[\u0B80-\u0BFF]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))
    
    stats['has_tamil'] = has_tamil
    stats['has_english'] = has_english
    stats['is_bilingual'] = has_tamil and has_english
    
    return stats


if __name__ == "__main__":
    # Test the module
    test_text = """
    Page 1
    
    Government of India
    Ministry of Example
    
    CIRCULAR NO. 123/2024
    
    Subject: Important Government Circular
    
    This is the main    content   of the circular.
    It contains multiple    spaces and needs cleaning.
    
    Tamil text: அரசாங்க சுற்றறிக்கை முக்கியமானது.
    
    Page 2
    
    More content here with special characters: @#$%^&
    And some broken-
    words across lines.
    
    ...............
    
    Confidential - Not for Publication
    """
    
    print("Original Text:")
    print("=" * 60)
    print(test_text)
    print("\n" + "=" * 60)
    
    # Clean the text
    cleaned = clean_text(test_text)
    
    print("\nCleaned Text:")
    print("=" * 60)
    print(cleaned)
    print("\n" + "=" * 60)
    
    # Get statistics
    stats = get_text_statistics(cleaned)
    print("\nText Statistics:")
    print("=" * 60)
    for key, value in stats.items():
        print(f"{key}: {value}")

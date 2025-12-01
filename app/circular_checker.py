"""
circular_checker.py
Utility module to detect whether the given text appears to be
a government circular / official communication.

Returns:
    bool → True if circular, False if general document
"""

import re

# -----------------------------------------------------
# LIST OF KEYWORDS AND PATTERNS THAT INDICATE OFFICIAL USE
# -----------------------------------------------------

GOV_KEYWORDS = [
    # English
    "government", "govt", "department", "ministry", "secretary",
    "circular", "notification", "order", "proceedings",
    "office memorandum", "office order", "official", "g.o", "g.o.",

    # Tamil
    "அரசு", "சுற்றறிக்கை", "அறிவிப்பு", "துறை", "உத்தரவு", "அரசாணை",
    "கல்வித்துறை", "நிதித்துறை",

    # Hindi
    "सरकार", "विभाग", "मंत्रालय", "अधिसूचना", "आदेश", "परिपत्र",
    "राज्य सरकार", "केंद्र सरकार",

    # Telugu
    "ప్రభుత్వం", "విభాగం", "సర్క్యులర్", "ప్రకటన",

    # Kannada
    "ಸರ್ಕಾರ್", "ವಿಭಾಗ", "ಅಧಿಸೂಚನೆ", "ಆದೇಶ",

    # Malayalam
    "സർക്കാർ", "വകുപ്പ്", "അறിവിപ്പ്", "സർകുലർ",
]

# Header patterns commonly found in circulars
HEADER_PATTERNS = [
    r"government of [a-zA-Z ]+",
    r"govt\.? of [a-zA-Z ]+",
    r"department of [a-zA-Z ]+",
    r"ministry of [a-zA-Z ]+",
    r"அரசு அறிவிப்பு",
    r"தமிழ்நாடு அரசு",
    r"सरकार",
    r"भारत सरकार",
]


# -----------------------------------------------------
# MAIN FUNCTION
# -----------------------------------------------------
def is_government_circular(text: str) -> bool:
    """
    Determines whether a text appears to be a government circular.
    Returns:
        bool → True if circular-like, False otherwise.
    """

    if not text or len(text.strip()) < 10:
        return False

    text_lower = text.lower()

    # ---------------------------
    # 1. Keyword match
    # ---------------------------
    for kw in GOV_KEYWORDS:
        if kw.lower() in text_lower:
            return True

    # ---------------------------
    # 2. Header format match
    # ---------------------------
    for pattern in HEADER_PATTERNS:
        if re.search(pattern, text_lower):
            return True

    # ---------------------------
    # 3. If no match → Not circular
    # ---------------------------
    return False

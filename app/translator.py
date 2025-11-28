# app/translator.py

import os
import json
from typing import List
from pathlib import Path
from transformers import NllbTokenizerFast

from transformers import AutoModelForSeq2SeqLM

# -------------------------------
# MODEL PATH CONFIG
# -------------------------------
MODEL_LOCAL_DIR = os.path.join(
    os.path.dirname(__file__), "..", "models", "nllb_model"
)

LOCAL_ONLY = True  # Offline mode

# -------------------------------
# GLOBALS
# -------------------------------
_tokenizer = None
_model = None
_lang_map = None  # <-- PATCH: external lang_code_to_id support

LANG_CODE_FILE = Path(MODEL_LOCAL_DIR) / "lang_codes.json"


# ============================================================
# LOAD MODEL + TOKENIZER
# ============================================================
def _load_model_and_tokenizer():
    global _tokenizer, _model, _lang_map

    if _tokenizer is not None and _model is not None:
        return

    model_path = Path(MODEL_LOCAL_DIR)

    if not model_path.exists():
        raise FileNotFoundError(
            f"❌ Model folder NOT FOUND:\n{model_path}\n\n"
            "Fix:\n  • Run: python app/download_nllb.py\n"
            "  • Or manually place files into models/nllb-200-distilled-600M/"
        )

    # Load tokenizer
    _tokenizer = NllbTokenizerFast.from_pretrained(
    str(model_path),
    local_files_only=LOCAL_ONLY
)

    # Load model
    _model = AutoModelForSeq2SeqLM.from_pretrained(
        str(model_path),
        local_files_only=LOCAL_ONLY
    )
    _model.eval()

    # ==============================================================
    # PATCH: Load lang_code_to_id (from tokenizer OR fallback file)
    # ==============================================================
    raw_map = getattr(_tokenizer, "lang_code_to_id", None)

    if raw_map and len(raw_map) > 0:
        _lang_map = raw_map
    else:
        if not LANG_CODE_FILE.exists():
            raise RuntimeError(
                "❌ tokenizer.json does NOT contain lang_code_to_id\n"
                f"AND lang_codes.json NOT FOUND at:\n{LANG_CODE_FILE}\n\n"
                "Fix:\n  • Create lang_codes.json from the patch I gave.\n"
            )
        with open(LANG_CODE_FILE, "r", encoding="utf8") as f:
            _lang_map = json.load(f)


# ============================================================
# GET SUPPORTED LANGUAGES
# ============================================================
def get_supported_lang_codes() -> List[str]:
    _load_model_and_tokenizer()
    return sorted(list(_lang_map.keys()))


# ============================================================
# TRANSLATION FUNCTION
# ============================================================
def translate(text: str, source_lang: str, target_lang: str, max_length: int = 512) -> str:
    if not text or not text.strip():
        return ""

    _load_model_and_tokenizer()

    # VALIDATION
    if source_lang not in _lang_map:
        raise ValueError(f"❌ Unsupported source language: {source_lang}")

    if target_lang not in _lang_map:
        raise ValueError(f"❌ Unsupported target language: {target_lang}")

    # Set source language for tokenizer
    _tokenizer.src_lang = source_lang

    # Encode
    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    # Generate
    outputs = _model.generate(
        **inputs,
        forced_bos_token_id=_lang_map[target_lang],
        max_length=max_length,
        num_beams=4,
        early_stopping=True
    )

    result = _tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    return result.strip()


# ============================================================
# Convenience shortcuts
# ============================================================
def translate_to_tamil(text: str) -> str:
    return translate(text, "eng_Latn", "tam_Taml")


def translate_to_english(text: str) -> str:
    return translate(text, "tam_Taml", "eng_Latn")

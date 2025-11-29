"""
NLLB Translation Module
Supports translation to all Indian languages using lang_code_to_id.
"""

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Manually define language codes for Indian languages
INDIAN_LANG_CODES = {
    "tam_Taml": 256170,   # Tamil
    "tel_Telu": 256172,   # Telugu
    "hin_Deva": 256068,   # Hindi
    "kan_Knda": 256083,   # Kannada
    "mal_Mlym": 256115,   # Malayalam
    "ben_Beng": 256026,   # Bengali
    "mar_Deva": 256116,   # Marathi
    "pan_Guru": 256138,   # Punjabi
    "guj_Gujr": 256064,   # Gujarati
    "asm_Beng": 256015,   # Assamese
    "ori_Orya": 256136,   # Odia
    "urd_Arab": 256190,   # Urdu
}

class NLLBTranslator:
    def __init__(self, model_path):

        model_path = os.path.abspath(model_path)
        print(f"Loading NLLB model from: {model_path}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )

        # Load model (avoid meta tensors)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_path,
            local_files_only=True
        ).to("cpu")

        # Load language codes
        if hasattr(self.tokenizer, "lang_code_to_id"):
            self.lang_map = self.tokenizer.lang_code_to_id
        else:
            self.lang_map = self._extract_lang_codes(model_path)

        # Add missing Indian languages
        self.lang_map.update(INDIAN_LANG_CODES)

        print("NLLB Loaded Successfully on CPU.")

    def _extract_lang_codes(self, model_path):
        json_path = os.path.join(model_path, "tokenizer.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("lang_code_to_id", {})

    def translate(self, text, target_lang="tam_Taml"):

        if target_lang not in self.lang_map:
            raise ValueError(f"Language code '{target_lang}' not found.")

        inputs = self.tokenizer(text, return_tensors="pt", padding=True).to("cpu")

        output_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=self.lang_map[target_lang],
            max_length=512
        )

        return self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)

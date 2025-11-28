# download_model.py
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "ai4bharat/indictrans2-en-indic-1B"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "hf_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Download model and tokenizer to cache
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

print("Model downloaded to cache:", CACHE_DIR)

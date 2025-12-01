# ui/streamlit_app.py
import streamlit as st
import sys
import os
import tempfile
import time
import re
import base64

# ensure parent package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# local modules
from app.pdf_reader import extract_text
from app.text_cleaner import clean_text, get_text_statistics

from typing import List, Tuple
from collections import Counter
import math

# translator (NLLB)
try:
    from app.translator import NLLBTranslator
    HAVE_TRANSLATOR = True
except:
    HAVE_TRANSLATOR = False

# TTS
try:
    from gtts import gTTS
    from langdetect import detect
    HAVE_TTS = True
except:
    HAVE_TTS = False

# Scraper
try:
    import requests
    from bs4 import BeautifulSoup
    HAVE_SCRAPER = True
except:
    HAVE_SCRAPER = False

st.set_page_config(page_title="Mozhi Amudhu", page_icon="📄", layout="wide")

# ============================================================
# 🔥 1. Background Image Loader (bd.jpg)
# ============================================================
def add_bg_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    st.markdown(
    f"""
    <style>
    /* Background image */
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Clean Inputs */
    textarea, input, select {{
        background-color: #ffffffee !important;
        border: 1px solid #aaa !important;
        color: #111 !important;
        border-radius: 8px !important;
        padding: 8px !important;
    }}

    .stTextInput>div>div>input {{
        background-color: #ffffffaa !important;
        color: #111 !important;
        border: 1px solid #aaa !important;
    }}

    /* Main Title */
    .main-header {{
        font-size: 2.2rem; 
        font-weight: 700; 
        color:#1a1a1a; 
        text-align:center;
        padding:1rem 0;
        background: #f2f4f8cc;
        border-radius: 10px;
        border: 1px solid #d0d0d0;
    }}

    /* Summary Boxes */
    .summary-box {{
        background: #f7f9fcdd;
        padding: 1rem; 
        border-radius: 10px; 
        border: 1px solid #ccd3e0;
        color:#111;
    }}

    /* Muted Text */
    .muted {{
        color:#333;
        font-size:0.95rem;
    }}

    /* Tab Colors (remove orange) */
    .stTabs [data-baseweb="tab"] {{
        background: #e8ecf1 !important;
        color: #000 !important;
        border-radius: 8px 8px 0 0 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: #ffffff !important;
        border-bottom: 2px solid #4a90e2 !important;
        color: #004080 !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# Load BD.jpg background
bg_path = os.path.join(os.path.dirname(__file__), "assets", "bg2.jpg")
if os.path.exists(bg_path):
    add_bg_image(bg_path)


# ============================================================
# (REST OF YOUR FULL CODE – UNCHANGED)
# ============================================================

MODEL_PATH = os.path.abspath(r"D:\Mozhi_Amudhu\models\nllb-200-distilled-600M")

INDIAN_LANGS = {
    "Tamil": "tam_Taml",
    "Hindi": "hin_Deva",
    "Telugu": "tel_Telu",
    "Malayalam": "mal_Mlym",
    "Kannada": "kan_Knda",
    "Bengali": "ben_Beng",
    "Gujarati": "guj_Gujr",
    "Punjabi": "pan_Guru",
    "Marathi": "mar_Deva",
    "Odia": "ori_Orya",
    "Urdu": "urd_Arab",
    "English": "eng_Latn",
}

# -----------------------
# Sentence utils
# -----------------------
SENT_END_RE = re.compile(r'(?<=[.!?।])\s+')

def split_sentences(text: str) -> List[str]:
    raw = SENT_END_RE.split(text.strip())
    return [s.strip() for s in raw if s.strip()]

def score_sentences_by_wordfreq(text: str):
    words = re.findall(r"[\w\u0900-\u0fff\u0b80-\u0bff']+", text.lower())
    words = [w for w in words if len(w) > 1]
    freq = Counter(words)
    maxf = max(freq.values()) if freq else 1
    for k in list(freq.keys()):
        freq[k] = freq[k] / maxf

    sentences = split_sentences(text)
    scored = []
    for s in sentences:
        w = re.findall(r"[\w\u0900-\u0fff\u0b80-\u0bff']+", s.lower())
        if not w:
            score = 0
        else:
            score = sum(freq.get(x, 0) for x in w) / (math.sqrt(len(w)))
        scored.append((s, score))
    return scored

def generate_official_summary_extractive(text, max_sentences=3):
    scored = score_sentences_by_wordfreq(text)
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]
    order = split_sentences(text)
    chosen = [s for s, _ in sorted(top, key=lambda t: order.index(t[0]))]
    if not chosen:
        chosen = order[:max_sentences]
    summary = " ".join(chosen)
    if summary and summary[-1] not in ".!?।":
        summary += "."
    return summary

def generate_simplified_summary_extractive(text, max_sentences=5):
    scored = score_sentences_by_wordfreq(text)
    if not scored:
        return ""
    scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    mid = len(scored_sorted) // 2
    picks = []
    for i in range(max_sentences):
        idx = i//2 if i % 2 == 0 else mid + (i//2)
        if idx < len(scored_sorted):
            picks.append(scored_sorted[idx])
    if not picks:
        picks = scored_sorted[:max_sentences]
    sents = split_sentences(text)
    chosen = [s for s in sents if s in [p[0] for p in picks]][:max_sentences]
    if not chosen:
        chosen = sents[:max_sentences]
    summary = " ".join(chosen)
    if summary and summary[-1] not in ".!?।":
        summary += "."
    return summary

GOV_KEYWORDS = [
    "government","govt","department","ministry","secretary",
    "circular","notification","order","g.o","proceedings",
    "அரசு","சுற்றறிக்கை","துறை","அறிவிப்பு",
    "सरकार","विभाग","अधिसूचना","आदेश",
]

def looks_like_circular(text: str) -> bool:
    tl = text.lower()
    return any(k in tl for k in GOV_KEYWORDS)

def scrape_url_text(url: str):
    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    article = soup.find("article")
    if article: return "\n".join(article.stripped_strings)
    main = soup.find("main")
    if main: return "\n".join(main.stripped_strings)
    ps = soup.find_all("p")
    if ps: return "\n".join(p.get_text(" ", strip=True) for p in ps)
    body = soup.find("body")
    return " ".join(body.stripped_strings) if body else ""

@st.cache_resource
def load_translator(path):
    if not HAVE_TRANSLATOR: return None
    try:
        return NLLBTranslator(model_path=path)
    except:
        return None

translator_obj = load_translator(MODEL_PATH)

def generate_audio(text: str):
    lang = detect(text) if HAVE_TTS else "en"
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "temp_audio")
    os.makedirs(out_dir, exist_ok=True)
    ts = int(time.time())
    out_path = os.path.join(out_dir, f"mozhi_{ts}.mp3")
    tts = gTTS(text=text, lang=lang)
    tts.save(out_path)
    return out_path, lang

def initialize_session_state():
    defaults = {
        "extracted_text": "",
        "cleaned_text": "",
        "official_summary": "",
        "simplified_summary": "",
        "translated_text": "",
        "audio_path": None,
        "permission_required": False,
        "permission_decision": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_downstream(keep_extracted=False):
    if not keep_extracted:
        st.session_state.extracted_text = ""
    st.session_state.cleaned_text = ""
    st.session_state.official_summary = ""
    st.session_state.simplified_summary = ""
    st.session_state.translated_text = ""
    st.session_state.audio_path = None
    st.session_state.permission_required = False
    st.session_state.permission_decision = None

# ============================================================
# MAIN UI
# ============================================================
def main():
    initialize_session_state()

    st.markdown('<div class="main-header"> Mozhi Amudhu — Multilingual Summariser & Translator</div>', unsafe_allow_html=True)

    # ------------ INPUT -------------
    st.header("Step 1: Input Document")
    tab_pdf, tab_paste, tab_url = st.tabs(["Upload PDF", " Paste Text", " Fetch URL"])

    # PDF TAB
    with tab_pdf:
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded and st.button("Extract & Inspect"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.getvalue())
                    pdf_path = tmp.name
                text = extract_text(pdf_path)
                st.session_state.extracted_text = text or ""
                reset_downstream(keep_extracted=True)
                if not text:
                    st.error("No text extracted.")
                else:
                    if looks_like_circular(text):
                        st.session_state.permission_required = False
                        st.session_state.permission_decision = True
                        st.success("Government circular detected.")
                    else:
                        st.session_state.permission_required = True
                        st.warning("Not a circular. Confirm to proceed.")
            finally:
                try: os.unlink(pdf_path)
                except: pass

    # PASTE TAB
    with tab_paste:
        pasted = st.text_area("Paste text here", height=220)
        if st.button("Use pasted text"):
            if not pasted.strip():
                st.error("Paste some text first.")
            else:
                st.session_state.extracted_text = pasted
                reset_downstream(keep_extracted=True)
                if looks_like_circular(pasted):
                    st.session_state.permission_required = False
                    st.session_state.permission_decision = True
                    st.success("Looks like a circular.")
                else:
                    st.session_state.permission_required = True
                    st.warning("Not a circular. Confirm to continue.")

    # URL TAB
    with tab_url:
        url = st.text_input("Enter URL")
        if st.button("Fetch URL"):
            if not url:
                st.error("Enter a valid URL.")
            else:
                try:
                    txt = scrape_url_text(url)
                    st.session_state.extracted_text = txt
                    reset_downstream(keep_extracted=True)
                    if looks_like_circular(txt):
                        st.session_state.permission_required = False
                        st.session_state.permission_decision = True
                        st.success("Circular content detected.")
                    else:
                        st.session_state.permission_required = True
                        st.warning("Not a circular. Confirm to continue.")
                except Exception as e:
                    st.error(f"URL fetch failed: {e}")

    # PERMISSION CHECK
    if st.session_state.permission_required and st.session_state.extracted_text:
        choice = st.selectbox("Continue?", ["— Select —","Yes","No"])
        if choice == "Yes":
            st.session_state.permission_decision = True
            st.session_state.permission_required = False
        elif choice == "No":
            reset_downstream()
            st.info("Stopped.")
            return

    # ------------ CLEANING -------------
    if st.session_state.permission_decision:
        st.header("🧹 Step 2: Clean & Inspect")
        if st.button("Clean Text") and st.session_state.extracted_text:
            cleaned = clean_text(st.session_state.extracted_text)
            st.session_state.cleaned_text = cleaned
            stats = get_text_statistics(cleaned)
            st.success(f"Cleaned: {stats['word_count']} words")

        if st.session_state.cleaned_text:
            with st.expander("View cleaned text"):
                st.text_area("Cleaned text", st.session_state.cleaned_text, height=240)

    # ------------ SUMMARY -------------
    if st.session_state.cleaned_text:
        st.header("Step 3: Summarise")
        c1, c2 = st.columns(2)
        if c1.button("Official Summary"):
            st.session_state.official_summary = generate_official_summary_extractive(
                st.session_state.cleaned_text, 3
            )
        if c2.button("Simplified Summary"):
            st.session_state.simplified_summary = generate_simplified_summary_extractive(
                st.session_state.cleaned_text, 5
            )

        col1, col2 = st.columns(2)
        if st.session_state.official_summary:
            col1.subheader("Official Summary")
            col1.markdown(f"<div class='summary-box'>{st.session_state.official_summary}</div>", unsafe_allow_html=True)

        if st.session_state.simplified_summary:
            col2.subheader("Simplified Summary")
            col2.markdown(f"<div class='summary-box'>{st.session_state.simplified_summary}</div>", unsafe_allow_html=True)

    # ------------ TRANSLATION -------------
    if st.session_state.official_summary or st.session_state.simplified_summary:
        st.header("Step 4: Translate")
        if translator_obj is None:
            st.info("Translation unavailable — model not loaded.")
        else:
            which = st.radio("Which summary?", ("Simplified", "Official"))
            text_to_translate = (
                st.session_state.simplified_summary if which=="Simplified" else st.session_state.official_summary
            )
            target = st.selectbox("Translate to", list(INDIAN_LANGS.keys()))
            if st.button("Translate"):
                code = INDIAN_LANGS[target]
                translated = translator_obj.translate(text_to_translate, target_lang=code)
                st.session_state.translated_text = translated

        if st.session_state.translated_text:
            st.subheader("Translated Output")
            st.markdown(f"<div class='summary-box'>{st.session_state.translated_text}</div>", unsafe_allow_html=True)

    # ------------ AUDIO -------------
    if st.session_state.translated_text or st.session_state.simplified_summary or st.session_state.official_summary:
        st.header("Step 5: Audio")
        choices = []
        if st.session_state.translated_text: choices.append("Translated")
        if st.session_state.simplified_summary: choices.append("Simplified")
        if st.session_state.official_summary: choices.append("Official")

        choice = st.selectbox("Pick text", choices)
        text = (
            st.session_state.translated_text if choice=="Translated"
            else st.session_state.simplified_summary if choice=="Simplified"
            else st.session_state.official_summary
        )

        if st.button("Generate Audio"):
            path, lang = generate_audio(text)
            st.session_state.audio_path = path
            st.success(f"Audio generated")

        if st.session_state.audio_path:
            st.audio(st.session_state.audio_path)
            with open(st.session_state.audio_path, "rb") as fh:
                st.download_button("Download MP3", fh.read(), "summary.mp3")

    st.markdown("<div style='text-align:center;color:#222;'>Mozhi Amudhu</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

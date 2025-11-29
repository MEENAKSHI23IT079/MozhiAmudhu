import streamlit as st
import sys
import os
import tempfile
import time

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Local modules
from app.pdf_reader import extract_text
from app.text_cleaner import clean_text, get_text_statistics
from app.summarizer import generate_official_summary, generate_simplified_summary
from app.translator import NLLBTranslator

# TTS
from gtts import gTTS
from langdetect import detect

st.set_page_config(page_title="Mozhi Amudhu", page_icon="📄", layout="wide")


# -----------------------------------------------------
# Cache Translator (fixes meta-tensor issue)
# -----------------------------------------------------
@st.cache_resource
def load_translator():
    return NLLBTranslator(
        model_path=r"D:\Mozhi_Amudhu\models\nllb-200-distilled-600M"
    )

translator = load_translator()


# Supported languages
indian_langs = {
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
    "Urdu": "urd_Arab"
}


# -----------------------------------------------------
# Session Initialization
# -----------------------------------------------------
def initialize_session_state():
    defaults = {
        "extracted_text": "",
        "cleaned_text": "",
        "official_summary": "",
        "simplified_summary": "",
        "translated_text": "",
        "audio_path": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -----------------------------------------------------
# PDF Processing
# -----------------------------------------------------
def process_pdf(uploaded_file):
    with st.spinner("Extracting text from PDF…"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                pdf_path = tmp.name

            text = extract_text(pdf_path)
            os.unlink(pdf_path)

            if text:
                st.session_state.extracted_text = text
                st.success(f"✓ Extracted {len(text)} characters")
            else:
                st.error("No text extracted.")
        except Exception as e:
            st.error(f"PDF error: {e}")


# -----------------------------------------------------
# Cleaning
# -----------------------------------------------------
def clean_extracted_text():
    if not st.session_state.extracted_text:
        st.error("No extracted text")
        return

    with st.spinner("Cleaning text..."):
        cleaned = clean_text(st.session_state.extracted_text)
        st.session_state.cleaned_text = cleaned
        stats = get_text_statistics(cleaned)
        st.success(f"✓ Cleaned: {stats['word_count']} words, {stats['paragraph_count']} paragraphs")


# -----------------------------------------------------
# Summaries
# -----------------------------------------------------
def run_summariser(summary_type):
    text = st.session_state.cleaned_text
    if not text:
        st.error("Clean the text first")
        return

    with st.spinner("Generating summary…"):
        if summary_type == "official":
            st.session_state.official_summary = generate_official_summary(text)
        else:
            st.session_state.simplified_summary = generate_simplified_summary(text)

    st.success("✓ Summary ready")


# -----------------------------------------------------
# Translation
# -----------------------------------------------------
def run_translation(text, target_code):
    with st.spinner("Translating summary…"):
        try:
            translated = translator.translate(text, target_code)
            st.session_state.translated_text = translated
            st.success("✓ Translation completed")
        except Exception as e:
            st.error(f"Translation error: {e}")


# -----------------------------------------------------
# TTS
# -----------------------------------------------------
def generate_audio(text):
    try:
        lang = detect(text)
    except:
        lang = "en"

    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "temp_audio")
    os.makedirs(out_dir, exist_ok=True)

    ts = int(time.time())
    audio_path = os.path.join(out_dir, f"tts_{ts}.mp3")

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_path)
        st.session_state.audio_path = audio_path
        return lang
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None


# -----------------------------------------------------
# MAIN UI
# -----------------------------------------------------
def main():

    initialize_session_state()

    st.markdown('<div style="font-size:2.3rem;font-weight:700;text-align:center;color:#1f77b4;">📄 Mozhi Amudhu</div>', unsafe_allow_html=True)

    # ---------------- Step 1: Input ----------------
    st.header("📥 Step 1: Input Document")
    tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])

    with tab1:
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            if st.button("Extract Text"):
                process_pdf(uploaded)
            if st.button("Clean Text", disabled=not st.session_state.extracted_text):
                clean_extracted_text()

    with tab2:
        text = st.text_area("Paste text here", height=200)
        if st.button("Use pasted text"):
            if text.strip():
                st.session_state.extracted_text = text
                clean_extracted_text()
            else:
                st.error("Paste some text first")

    # Show cleaned text
    if st.session_state.cleaned_text:
        st.divider()
        with st.expander("📖 View Cleaned Text"):
            stats = get_text_statistics(st.session_state.cleaned_text)
            st.info(f"{stats['word_count']} words | {stats['paragraph_count']} paragraphs")
            st.text_area("Cleaned text", st.session_state.cleaned_text, height=220)

    # ---------------- Step 2: Summaries ----------------
    if st.session_state.cleaned_text:
        st.divider()
        st.header("📝 Step 2: Summaries")

        c1, c2 = st.columns(2)
        if c1.button("🎯 Official Summary"):
            run_summariser("official")
        if c2.button("✨ Simplified Summary"):
            run_summariser("simplified")

        col1, col2 = st.columns(2)
        if st.session_state.official_summary:
            with col1:
                st.subheader("🎯 Official Summary")
                st.markdown(f'<div style="background:#f0f2f6;padding:1rem;border-radius:8px;">{st.session_state.official_summary}</div>', unsafe_allow_html=True)

        if st.session_state.simplified_summary:
            with col2:
                st.subheader("✨ Simplified Summary")
                st.markdown(f'<div style="background:#f0f2f6;padding:1rem;border-radius:8px;">{st.session_state.simplified_summary}</div>', unsafe_allow_html=True)

    # ---------------- Step 3: Translation ----------------
    if st.session_state.official_summary or st.session_state.simplified_summary:
        st.divider()
        st.header("🌐 Step 3: Translate Summary")

        choice = st.radio("Choose summary to translate:", ("Simplified", "Official"))
        text_to_translate = (
            st.session_state.simplified_summary if choice == "Simplified"
            else st.session_state.official_summary
        )

        lang = st.selectbox("Translate to:", list(indian_langs.keys()))

        if st.button("🌐 Translate"):
            lang_code = indian_langs[lang]
            run_translation(text_to_translate, lang_code)

        if st.session_state.translated_text:
            st.subheader("Translated Output")
            st.markdown(f'<div style="background:#f0f2f6;padding:1rem;border-radius:8px;">{st.session_state.translated_text}</div>', unsafe_allow_html=True)

    # ---------------- Step 4: Audio ----------------
    if st.session_state.translated_text:
        st.divider()
        st.header("🔊 Step 4: Listen to Text")

        text = st.session_state.translated_text

        if st.button("🎙️ Generate Audio"):
            lang = generate_audio(text)
            if lang:
                st.success(f"Audio generated (Detected: **{lang}**)")

        if st.session_state.audio_path:
            st.audio(st.session_state.audio_path)
            with open(st.session_state.audio_path, "rb") as audio:
                st.download_button("📥 Download MP3", audio.read(),
                                   file_name="summary.mp3", mime="audio/mp3")

    st.divider()
    st.markdown("<div style='text-align:center;color:#777;padding:0.8rem;'>Mozhi Amudhu v2.0 — Summariser + Translator</div>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()

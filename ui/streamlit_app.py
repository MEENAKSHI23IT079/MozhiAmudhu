# ui/streamlit_app.py
import streamlit as st
import sys
import os
import tempfile
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.pdf_reader import extract_text
from app.text_cleaner import clean_text, get_text_statistics
from app import translator
from app.tts_generator import generate_tts_tamil, check_tts_available

st.set_page_config(page_title="Mozhi Amudhu", page_icon="📄", layout="wide")

st.markdown("""
<style>
.main-header { font-size: 2.4rem; font-weight:700; color:#1f77b4; text-align:center; padding:1rem 0;}
.summary-box { background:#f0f2f6; padding:1rem; border-radius:8px; }
.lang-select { width: 100%; }
</style>
""", unsafe_allow_html=True)


# session state
def initialize_session_state():
    defaults = {
        "extracted_text": "",
        "cleaned_text": "",
        "official_summary": "",
        "simplified_summary": "",
        "translated_text": "",
        "audio_path": None,
        "src_code": "eng_Latn",     # >>> default language for dropdowns
        "tgt_code": "tam_Taml"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# PDF processing
def process_pdf(uploaded_file):
    with st.spinner("Extracting text from PDF..."):
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


# cleaning
def clean_extracted_text():
    if not st.session_state.extracted_text:
        st.error("No extracted text")
        return
    with st.spinner("Cleaning text..."):
        cleaned = clean_text(st.session_state.extracted_text)
        st.session_state.cleaned_text = cleaned
        stats = get_text_statistics(cleaned)
        st.success(f"✓ Cleaned: {stats['word_count']} words, {stats['paragraph_count']} paragraphs")


# summary
def generate_summary(which: str):
    text = st.session_state.cleaned_text
    if not text:
        st.error("Clean text first")
        return
    with st.spinner("Generating summary..."):
        sents = text.replace("\n", " ").split(". ")
        if which == "official":
            s = ". ".join(sents[:3]).strip()
            st.session_state.official_summary = (s + ".") if s else ""
        else:
            s = ". ".join(sents[:5]).strip()
            st.session_state.simplified_summary = (s + ".") if s else ""
        st.success("✓ Summary ready")


# wrapper for translator
def do_translate(text, src_code, tgt_code):
    try:
        translated = translator.translate(text, source_lang=src_code, target_lang=tgt_code)
        return translated
    except FileNotFoundError as e:
        st.error(str(e))
        st.info("Run app/download_nllb.py while online to download the model files.")
        return ""
    except Exception as e:
        st.error(f"Translation error: {e}")
        return ""


# TTS wrapper
def generate_audio_from_text(text):
    tts_status = check_tts_available()
    if not tts_status["any_available"]:
        st.error("No TTS backend available. Install gTTS or Coqui TTS.")
        return
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "temp_audio")
    os.makedirs(output_dir, exist_ok=True)
    ts = int(time.time())
    out = os.path.join(output_dir, f"summary_{ts}.mp3")
    backend = "gtts" if tts_status["gtts"] else "coqui"
    try:
        audio_path = generate_tts_tamil(text, out, backend=backend)
        st.session_state.audio_path = audio_path
        st.success("✓ Audio generated")
    except Exception as e:
        st.error(f"TTS error: {e}")


# main
def main():
    initialize_session_state()

    st.markdown('<div class="main-header">📄 Mozhi Amudhu — Multilingual</div>', unsafe_allow_html=True)

    # sidebar
    with st.sidebar:
        st.header("⚙️ Settings & Languages")

        # >>> UPDATED FOR MULTILINGUAL DROPDOWNS <<<
        try:
            codes = translator.get_supported_lang_codes()
            st.success("Translation model: available (local)")
        except Exception:
            codes = []
            st.warning("Translation model not found.")

        st.markdown("### 🌐 Select Languages")

        if codes:
            st.session_state.src_code = st.selectbox(
                "Input Language",
                options=codes,
                index=codes.index(st.session_state.src_code)
                if st.session_state.src_code in codes else 0,
                key="src_dropdown"
            )
            st.session_state.tgt_code = st.selectbox(
                "Output Language",
                options=codes,
                index=codes.index(st.session_state.tgt_code)
                if st.session_state.tgt_code in codes else 0,
                key="tgt_dropdown"
            )
        else:
            st.session_state.src_code = st.text_input("Source language", value="eng_Latn")
            st.session_state.tgt_code = st.text_input("Target language", value="tam_Taml")

        st.divider()
        st.write("TTS status:")
        tts = check_tts_available()
        st.write(f"gTTS: {'✓' if tts['gtts'] else '✗'}  —  Coqui: {'✓' if tts['coqui'] else '✗'}")


    # Input Area
    st.header("📥 Step 1: Input Document")
    tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])

    with tab1:
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            c1, c2 = st.columns(2)
            if c1.button("Extract Text"):
                process_pdf(uploaded)
            if c2.button("Clean Text", disabled=not st.session_state.extracted_text):
                clean_extracted_text()

    with tab2:
        pasted = st.text_area("Paste text here", height=200)
        if st.button("Use pasted text"):
            if pasted.strip():
                st.session_state.extracted_text = pasted
                clean_extracted_text()
            else:
                st.error("Paste some text first")

    if st.session_state.cleaned_text:
        st.divider()
        with st.expander("📖 View Cleaned Text"):
            stats = get_text_statistics(st.session_state.cleaned_text)
            st.info(f"{stats['word_count']} words | {stats['paragraph_count']} paragraphs")
            st.text_area("Cleaned text", st.session_state.cleaned_text, height=220)


    # Summaries
    if st.session_state.cleaned_text:
        st.divider()
        st.header("📝 Step 2: Summaries")
        c1, c2 = st.columns(2)
        if c1.button("🎯 Official summary"):
            generate_summary("official")
        if c2.button("✨ Simplified summary"):
            generate_summary("simplified")

        if st.session_state.official_summary or st.session_state.simplified_summary:
            c1, c2 = st.columns(2)
            with c1:
                if st.session_state.official_summary:
                    st.subheader("🎯 Official Summary")
                    st.markdown(f'<div class="summary-box">{st.session_state.official_summary}</div>',
                                unsafe_allow_html=True)
            with c2:
                if st.session_state.simplified_summary:
                    st.subheader("✨ Simplified Summary")
                    st.markdown(f'<div class="summary-box">{st.session_state.simplified_summary}</div>',
                                unsafe_allow_html=True)


    # Translation
    if st.session_state.official_summary or st.session_state.simplified_summary:
        st.divider()
        st.header("🌐 Step 3: Translate")

        sel = st.radio("Choose summary to translate", ("Simplified", "Official"))
        base_text = st.session_state.simplified_summary if sel == "Simplified" else st.session_state.official_summary

        if st.button("🔄 Translate"):
            output = do_translate(base_text,
                                  st.session_state.src_code,
                                  st.session_state.tgt_code)
            st.session_state.translated_text = output

        if st.session_state.translated_text:
            st.subheader("✅ Translated Output")
            st.markdown(f'<div class="summary-box">{st.session_state.translated_text}</div>',
                        unsafe_allow_html=True)


    # Audio
    if st.session_state.translated_text:
        st.divider()
        st.header("🔊 Step 4: Text to Speech")
        if st.button("🎙️ Generate Audio"):
            generate_audio_from_text(st.session_state.translated_text)
        if st.session_state.audio_path:
            st.audio(st.session_state.audio_path)
            with open(st.session_state.audio_path, "rb") as fh:
                st.download_button("📥 Download MP3", fh.read(),
                                   file_name="summary.mp3", mime="audio/mp3")

    st.divider()
    st.markdown("<div style='text-align:center;color:#666;padding:0.8rem;'>Mozhi Amudhu v1.0 — NLLB Offline</div>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()

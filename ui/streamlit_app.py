# ui/streamlit_app.py
import streamlit as st
import sys
import os
import tempfile
import time

# Path setup (so "app" package imports work)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Local modules
from app.pdf_reader import extract_text
from app.text_cleaner import clean_text, get_text_statistics
from app.summarizer import generate_official_summary, generate_simplified_summary

# Translator (optional)
try:
    from app.translator import NLLBTranslator
    HAVE_TRANSLATOR = True
except Exception:
    HAVE_TRANSLATOR = False

# TTS (optional)
try:
    from gtts import gTTS
    from langdetect import detect
    HAVE_TTS = True
except Exception:
    HAVE_TTS = False

st.set_page_config(page_title="Mozhi Amudhu", page_icon="📄", layout="wide")

# -----------------------
# Configuration
# -----------------------
MODEL_PATH = r"D:\Mozhi_Amudhu\models\nllb-200-distilled-600M"  # update if different

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
# Cached translator loader
# -----------------------
@st.cache_resource
def load_translator_safe(path: str):
    if not HAVE_TRANSLATOR:
        return None
    try:
        return NLLBTranslator(model_path=path)
    except Exception as e:
        # return None if loading failed (UI will show message)
        return None

translator_obj = load_translator_safe(MODEL_PATH) if HAVE_TRANSLATOR else None

# -----------------------
# Session defaults
# -----------------------
def initialize_session_state():
    defaults = {
        "extracted_text": "",
        "cleaned_text": "",
        "official_summary": "",
        "simplified_summary": "",
        "translated_text": "",
        "audio_path": None,
        # permission flow:
        "permission_required": False,   # True if doc not clearly circular and user must decide
        "permission_widget_value": None, # stored by the widget key "permission_widget" (do not clash)
        "permission_decision": None,    # None => not decided, True => proceed, False => stop
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -----------------------
# Circular detection
# -----------------------
GOV_KEYWORDS = [
    "government", "govt", "department", "ministry", "secretary",
    "circular", "notification", "order", "g.o", "proceedings",
    # Tamil / Hindi etc (extendable)
    "அரசு", "சுற்றறிக்கை", "துறை", "அறிவிப்பு",
    "सरकार", "विभाग", "अधिसूचना", "आदेश",
]

def looks_like_circular(text: str) -> bool:
    if not text or not text.strip():
        return False
    tl = text.lower()
    return any(k in tl for k in GOV_KEYWORDS)

# -----------------------
# PDF / paste processing
# -----------------------
def reset_processing_state(keep_extracted=False):
    """Clear downstream state. If keep_extracted=False, also clears extracted_text."""
    if not keep_extracted:
        st.session_state.extracted_text = ""
    st.session_state.cleaned_text = ""
    st.session_state.official_summary = ""
    st.session_state.simplified_summary = ""
    st.session_state.translated_text = ""
    st.session_state.audio_path = None
    st.session_state.permission_required = False
    st.session_state.permission_widget_value = None
    st.session_state.permission_decision = None

def process_pdf(uploaded_file):
    """Extract text and prepare permission flow when required."""
    with st.spinner("Extracting text from PDF…"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                pdf_path = tmp.name

            text = extract_text(pdf_path)
        except Exception as e:
            st.error(f"PDF extraction error: {e}")
            return
        finally:
            try:
                if 'pdf_path' in locals() and os.path.exists(pdf_path):
                    os.unlink(pdf_path)
            except Exception:
                pass

        if not text:
            st.error("No text extracted from PDF.")
            return

        # Save extracted text and reset downstream state
        st.session_state.extracted_text = text
        st.session_state.cleaned_text = ""
        st.session_state.official_summary = ""
        st.session_state.simplified_summary = ""
        st.session_state.translated_text = ""
        st.session_state.audio_path = None
        st.session_state.permission_widget_value = None
        st.session_state.permission_decision = None

        # Decide if permission is required
        if looks_like_circular(text):
            st.session_state.permission_required = False
            st.session_state.permission_decision = True
            st.success("✓ Text extracted (detected as Government Circular).")
        else:
            st.session_state.permission_required = True
            st.session_state.permission_decision = None
            st.warning("⚠️ This document does NOT look like a Government Circular. Please choose whether to continue.")

def use_pasted_text(user_text: str):
    """Same flow for pasted text."""
    if not user_text or not user_text.strip():
        st.error("Paste some text first.")
        return

    st.session_state.extracted_text = user_text
    st.session_state.cleaned_text = ""
    st.session_state.official_summary = ""
    st.session_state.simplified_summary = ""
    st.session_state.translated_text = ""
    st.session_state.audio_path = None
    st.session_state.permission_widget_value = None
    st.session_state.permission_decision = None

    if looks_like_circular(user_text):
        st.session_state.permission_required = False
        st.session_state.permission_decision = True
        st.success("✓ Text accepted (detected as Government Circular).")
    else:
        st.session_state.permission_required = True
        st.session_state.permission_decision = None
        st.warning("⚠️ This document does NOT look like a Government Circular. Please choose whether to continue.")

# -----------------------
# Cleaning / summaries / translation / TTS
# -----------------------
def clean_extracted_text():
    text = st.session_state.extracted_text
    if not text:
        st.error("No extracted text to clean.")
        return
    with st.spinner("Cleaning text..."):
        cleaned = clean_text(text)
        st.session_state.cleaned_text = cleaned
        stats = get_text_statistics(cleaned)
        st.success(f"✓ Cleaned: {stats['word_count']} words, {stats['paragraph_count']} paragraphs")

def run_summariser(which: str):
    text = st.session_state.cleaned_text
    if not text:
        st.error("Clean the text first.")
        return
    with st.spinner("Generating summary..."):
        if which == "official":
            st.session_state.official_summary = generate_official_summary(text)
        else:
            st.session_state.simplified_summary = generate_simplified_summary(text)
    st.success("✓ Summary ready")

def run_translation(text: str, target_code: str):
    if translator_obj is None:
        st.error("Translation model not available locally (or failed to load).")
        return
    with st.spinner("Translating..."):
        try:
            translated = translator_obj.translate(text, target_code)
            st.session_state.translated_text = translated
            st.success("✓ Translation completed")
        except Exception as e:
            st.error(f"Translation error: {e}")

def generate_audio_for_text(text: str):
    if not HAVE_TTS:
        st.error("TTS backend (gTTS/langdetect) not available.")
        return
    try:
        lang = detect(text)
    except Exception:
        lang = "en"
    out_dir = os.path.join(os.path.dirname(__file__), "assets", "temp_audio")
    os.makedirs(out_dir, exist_ok=True)
    ts = int(time.time())
    audio_path = os.path.join(out_dir, f"tts_{ts}.mp3")
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_path)
        st.session_state.audio_path = audio_path
        st.success("✓ Audio generated")
    except Exception as e:
        st.error(f"TTS error: {e}")

# -----------------------
# Permission widget helper
# -----------------------
def render_permission_widget():
    """
    Render a permission selectbox with no default action.
    Key used: "permission_widget" (unique)
    Returns:
        - True  => user chose 'Yes, continue'
        - False => user chose 'No, stop'
        - None  => user has not chosen (placeholder)
    """
    # options with placeholder to force explicit user choice
    options = ["— Select —", "Yes, continue", "No, stop"]
    # render selectbox (value will be stored in st.session_state["permission_widget"])
    choice = st.selectbox(
        "This doesn't look like a Government Circular. Do you want to continue processing?",
        options,
        index=0,
        key="permission_widget",
    )
    # Interpret result (do NOT write to session_state key that conflicts with widget key)
    if choice == "Yes, continue":
        # mark decision and clear permission_required
        st.session_state.permission_decision = True
        st.session_state.permission_required = False
        return True
    elif choice == "No, stop":
        st.session_state.permission_decision = False
        st.session_state.permission_required = False
        # clear extracted to hide further steps
        reset_processing_state(keep_extracted=False)
        return False
    else:
        # placeholder selected
        st.session_state.permission_decision = None
        return None

# -----------------------
# UI layout
# -----------------------
def main():
    initialize_session_state()

    st.markdown('<div style="font-size:2.3rem;font-weight:700;text-align:center;color:#1f77b4;">📄 Mozhi Amudhu</div>', unsafe_allow_html=True)

    # ---------- Step 1: Input ----------
    st.header("📥 Step 1: Input Document")
    tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])

    # Upload PDF
    with tab1:
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            if st.button("Extract Text"):
                process_pdf(uploaded)

            # Show permission widget if required (extracted_text present and decision not made)
            if st.session_state.permission_required and st.session_state.extracted_text:
                perm_result = render_permission_widget()
                if perm_result is False:
                    st.info("Process stopped by user. No further steps will be shown.")
            # Show Clean button only if permission decision is True (allowed)
            if st.session_state.permission_decision is True:
                if st.button("Clean Text", disabled=not st.session_state.extracted_text):
                    clean_extracted_text()

    # Paste Text
    with tab2:
        pasted = st.text_area("Paste text here", height=220, key="paste_area")
        if st.button("Use pasted text"):
            use_pasted_text(pasted)

        # If pasted text requires permission, show widget
        if st.session_state.permission_required and st.session_state.extracted_text:
            perm_result = render_permission_widget()
            if perm_result is False:
                st.info("Process stopped by user. No further steps will be shown.")

        # Clean button for pasted flow (only after permission granted)
        if st.session_state.permission_decision is True and st.session_state.extracted_text:
            if st.button("Clean Text (pasted)", key="clean_paste_btn"):
                clean_extracted_text()

    # ---------- Show cleaned text (only when cleaned and allowed) ----------
    if st.session_state.permission_decision is True and st.session_state.cleaned_text:
        st.divider()
        with st.expander("📖 View Cleaned Text"):
            stats = get_text_statistics(st.session_state.cleaned_text)
            st.info(f"{stats['word_count']} words | {stats['paragraph_count']} paragraphs")
            st.text_area("Cleaned text", st.session_state.cleaned_text, height=220)

    # ---------- Step 2: Summaries (only when allowed and cleaned) ----------
    if st.session_state.permission_decision is True and st.session_state.cleaned_text:
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
                st.markdown(
                    f'<div style="background:#f0f2f6;padding:1rem;border-radius:8px;">{st.session_state.official_summary}</div>',
                    unsafe_allow_html=True,
                )
        if st.session_state.simplified_summary:
            with col2:
                st.subheader("✨ Simplified Summary")
                st.markdown(
                    f'<div style="background:#f0f2f6;padding:1rem;border-radius:8px;">{st.session_state.simplified_summary}</div>',
                    unsafe_allow_html=True,
                )

    # ---------- Step 3: Translation (only when allowed and have a summary) ----------
    if st.session_state.permission_decision is True and (st.session_state.official_summary or st.session_state.simplified_summary):
        st.divider()
        st.header("🌐 Step 3: Translate Summary")

        # choose which summary to translate
        which_choice = st.radio("Choose summary to translate:", ("Simplified", "Official"), key="which_summary_radio")
        text_to_translate = st.session_state.simplified_summary if which_choice == "Simplified" else st.session_state.official_summary

        if translator_obj is None:
            st.info("Translation model not available locally. Skipping translation step.")
        else:
            lang_choice = st.selectbox("Translate to:", list(INDIAN_LANGS.keys()), key="translate_lang_box")
            if st.button("🌐 Translate"):
                run_translation(text_to_translate, INDIAN_LANGS[lang_choice])

        if st.session_state.translated_text:
            st.subheader("Translated Output")
            st.markdown(
                f'<div style="background:#f0f2f6;padding:1rem;border-radius:8px;">{st.session_state.translated_text}</div>',
                unsafe_allow_html=True,
            )

    # ---------- Step 4: Audio (only when allowed and some text available) ----------
    if st.session_state.permission_decision is True:
        audio_text_available = st.session_state.translated_text or st.session_state.simplified_summary or st.session_state.official_summary
        if audio_text_available:
            st.divider()
            st.header("🔊 Step 4: Listen to Text")
            audio_choice = st.selectbox(
                "Select text to generate audio from:",
                ["Translated", "Simplified summary", "Official summary"],
                key="audio_choice_box"
            )
            chosen_text = ""
            if audio_choice == "Translated":
                chosen_text = st.session_state.translated_text or st.session_state.simplified_summary or st.session_state.official_summary
            elif audio_choice == "Simplified summary":
                chosen_text = st.session_state.simplified_summary
            else:
                chosen_text = st.session_state.official_summary

            if chosen_text:
                if st.button("🎙️ Generate Audio"):
                    generate_audio_for_text(chosen_text)

                if st.session_state.audio_path:
                    st.audio(st.session_state.audio_path)
                    with open(st.session_state.audio_path, "rb") as fh:
                        st.download_button("📥 Download MP3", fh.read(), file_name="summary.mp3", mime="audio/mp3")

    st.divider()
    st.markdown("<div style='text-align:center;color:#777;padding:0.8rem;'>Mozhi Amudhu — Summariser + Translator</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

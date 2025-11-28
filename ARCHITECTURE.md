# Technical Architecture: Mozhi Amudhu

## System Overview
Multilingual Government Circular Summarization System built with Streamlit, designed to process government circulars and generate bilingual summaries with text-to-speech capabilities.

---

## 1. Architecture Diagram (Text-Based)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                    (Streamlit Frontend)                          │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │ PDF Upload   │         │ Text Input   │                      │
│  └──────┬───────┘         └──────┬───────┘                      │
└─────────┼────────────────────────┼──────────────────────────────┘
          │                        │
          ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT PROCESSING LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              pdf_reader.py (PyPDF2/pdfplumber)           │   │
│  │              Extract text from PDF documents              │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          text_cleaner.py (IndicNLP Library)              │   │
│  │          Preprocess & normalize Indic text               │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI PROCESSING LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            summarizer.py (Ollama + LLaMA-3)              │   │
│  │  ┌──────────────────┐      ┌───────────────────────┐    │   │
│  │  │ Official Summary │      │ Simplified Summary    │    │   │
│  │  │ (Technical/Formal)      │ (Citizen-Friendly)    │    │   │
│  │  └────────┬─────────┘      └──────────┬────────────┘    │   │
│  └───────────┼───────────────────────────┼──────────────────┘   │
│              │                           │                       │
│              ▼                           ▼                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         translator.py (IndicTrans2/AI4Bharat)            │   │
│  │         Translate English → Tamil (both summaries)       │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         tts_generator.py (AI4Bharat Indic-TTS)           │   │
│  │         Convert Tamil text to speech audio (WAV/MP3)     │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT PRESENTATION LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  English     │  │    Tamil     │  │  Audio Download      │  │
│  │  Summaries   │  │  Summaries   │  │  (Tamil TTS)         │  │
│  │  (Display)   │  │  (Display)   │  │  (.wav/.mp3)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Folder Structure

```
mozhi_amudhu/
├── app/
│   ├── __init__.py                  # Package initialization
│   ├── pdf_reader.py                # PDF text extraction
│   ├── text_cleaner.py              # Text preprocessing (IndicNLP)
│   ├── summarizer.py                # Summarization (Ollama LLaMA-3)
│   ├── translator.py                # Translation (IndicTrans2)
│   └── tts_generator.py             # Text-to-Speech (Indic-TTS)
│
├── ui/
│   ├── __init__.py                  # Package initialization
│   └── streamlit_app.py             # Main Streamlit application
│
├── assets/
│   ├── temp_audio/                  # Generated audio files
│   └── uploads/                     # Temporary PDF uploads
│
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── ARCHITECTURE.md                  # This file
├── .gitignore                       # Git ignore rules
└── venv/                            # Virtual environment (not tracked)
```

---

## 3. Python Modules and Responsibilities

### **3.1. app/pdf_reader.py**
**Responsibility:** Extract text from uploaded PDF documents
- **Functions:**
  - `extract_text_from_pdf(file) → str`
  - Handle multi-page PDFs
  - Handle scanned PDFs (OCR if needed)
- **Libraries:** PyPDF2, pdfplumber, or PyMuPDF

### **3.2. app/text_cleaner.py**
**Responsibility:** Preprocess and normalize text using IndicNLP
- **Functions:**
  - `preprocess_text(text, language='en') → str`
  - Remove special characters, normalize whitespace
  - Handle Indic language-specific preprocessing
  - Tokenization and sentence segmentation
- **Libraries:** indic-nlp-library, regex, unicodedata

### **3.3. app/summarizer.py**
**Responsibility:** Generate summaries using Ollama (LLaMA-3)
- **Functions:**
  - `generate_official_summary(text) → str`
  - `generate_simplified_summary(text) → str`
  - Prompt engineering for two summary types
- **Libraries:** ollama, langchain (optional), requests

### **3.4. app/translator.py**
**Responsibility:** Translate summaries to Tamil
- **Functions:**
  - `translate_to_tamil(text, source_lang='en') → str`
  - Batch translation support
  - Handle IndicTrans2 model loading
- **Libraries:** indictrans2, transformers, torch, sentencepiece

### **3.5. app/tts_generator.py**
**Responsibility:** Convert Tamil text to speech
- **Functions:**
  - `generate_speech(text, language='ta', output_path) → str`
  - Handle audio file generation (WAV format)
  - Support for different voice models
- **Libraries:** ai4bharat/indic-tts, TTS, soundfile, scipy

### **3.6. ui/streamlit_app.py**
**Responsibility:** Main user interface and orchestration
- **Functions:**
  - Setup Streamlit UI components
  - Handle file uploads and text input
  - Coordinate module execution pipeline
  - Display results and download buttons
- **Libraries:** streamlit, base64 (for downloads)

---

## 4. Libraries Required

### **Core Dependencies**
```
# Web Framework
streamlit>=1.28.0

# PDF Processing
PyPDF2>=3.0.0
pdfplumber>=0.10.0

# Indic NLP
indic-nlp-library>=0.91

# LLM Integration (Ollama)
ollama>=0.1.0
requests>=2.31.0

# Translation (IndicTrans2)
indictrans>=2.0.0
transformers>=4.35.0
torch>=2.0.0
sentencepiece>=0.1.99

# Text-to-Speech (AI4Bharat)
TTS>=0.22.0
soundfile>=0.12.0
scipy>=1.11.0

# Utilities
numpy>=1.24.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

### **System Requirements**
- Python 3.9+
- Ollama installed locally with LLaMA-3 model
- GPU recommended for translation and TTS (CUDA 11.8+)
- Minimum 8GB RAM, 16GB recommended

---

## 5. Flowchart Description

### **User Flow**
```
START
  ↓
[User Interface Loaded]
  ↓
┌─────────────────────────┐
│ Input Selection         │
│ ○ Upload PDF            │
│ ○ Paste Text            │
└────────┬────────────────┘
         ↓
    ┌────────┐
    │ Upload │
    │  PDF?  │
    └───┬────┘
        │
    Yes │           No
        ↓            ↓
 [Extract Text]  [Use Pasted Text]
    (pdf_reader)     │
        │            │
        └────┬───────┘
             ↓
    [Preprocess Text]
    (text_cleaner - IndicNLP)
             ↓
    [Generate Summaries]
    (summarizer - Ollama LLaMA-3)
         ┌───┴───┐
         ↓       ↓
    [Official] [Simplified]
    [Summary]  [Summary]
         │       │
         └───┬───┘
             ↓
    [Translate to Tamil]
    (translator - IndicTrans2)
         ┌───┴───┐
         ↓       ↓
    [Tamil     [Tamil
     Official]  Simplified]
         │       │
         └───┬───┘
             ↓
    [Display English & Tamil Summaries]
             ↓
    [Generate Tamil Audio]
    (tts_generator - Indic-TTS)
             ↓
    [Provide Audio Download Button]
             ↓
         [END]
```

### **Error Handling Flow**
```
[Each Module]
     ↓
  ┌──────┐
  │Error?│
  └──┬───┘
     │
  Yes│          No
     ↓           ↓
[Log Error]  [Continue]
     ↓
[Display User-Friendly Message]
     ↓
[Allow Retry/New Input]
```

---

## 6. Data Flow

### **Pipeline Stages**
1. **Input Stage:** PDF/Text → Raw String
2. **Preprocessing Stage:** Raw String → Cleaned String
3. **Summarization Stage:** Cleaned String → 2 Summaries (Official + Simplified)
4. **Translation Stage:** English Summaries → Tamil Summaries
5. **TTS Stage:** Tamil Text → Audio File (.wav)
6. **Output Stage:** Display All + Download Audio

### **Data Formats**
- **Input:** PDF (binary), Plain Text (string)
- **Intermediate:** UTF-8 encoded strings
- **Output:** 
  - Text: Markdown-formatted strings
  - Audio: WAV file (16kHz, mono)

---

## 7. Key Design Decisions

### **7.1. Why Ollama + LLaMA-3?**
- Local deployment for data privacy
- Government circulars may contain sensitive information
- No dependency on external APIs
- Cost-effective for high-volume usage

### **7.2. Why IndicTrans2?**
- State-of-the-art for Indian language translation
- Better than generic models for Tamil
- Open-source and locally deployable

### **7.3. Why AI4Bharat Indic-TTS?**
- Specifically designed for Indian languages
- Natural-sounding Tamil speech
- Better pronunciation of government terminology

### **7.4. Why Streamlit?**
- Rapid prototyping
- Built-in file upload and download widgets
- Easy deployment
- No frontend expertise required

---

## 8. Deployment Considerations

### **Local Development**
```bash
# Install Ollama
# Download LLaMA-3 model: ollama pull llama3

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run application
streamlit run ui/streamlit_app.py
```

### **Production Deployment**
- **Option 1:** Streamlit Cloud (limited by resource constraints)
- **Option 2:** Docker container on cloud VM (AWS/GCP/Azure)
- **Option 3:** On-premises server (recommended for government use)

### **Performance Optimization**
- Cache models in memory (avoid reloading)
- Use GPU acceleration for translation and TTS
- Implement async processing for long documents
- Add progress bars for user feedback

---

## 9. Security and Privacy

### **Data Handling**
- No data stored permanently (process in memory)
- Temporary files deleted after session
- Local model inference (no external API calls)
- Suitable for confidential government documents

### **Access Control**
- Add authentication layer if needed
- Audit logging for document processing
- Role-based access for different summary types

---

## 10. Future Enhancements

1. **Multi-language Support:** Extend beyond Tamil (Hindi, Telugu, etc.)
2. **Batch Processing:** Handle multiple PDFs simultaneously
3. **Custom Prompts:** Allow users to customize summary styles
4. **History:** Save and retrieve past summaries
5. **Comparison View:** Side-by-side comparison of original vs summaries
6. **API Mode:** Expose functionality as REST API
7. **OCR Integration:** Better support for scanned documents

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-25  
**Author:** Mozhi Amudhu Development Team

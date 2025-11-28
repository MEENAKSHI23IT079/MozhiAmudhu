# Mozhi Amudhu - Project Structure

## ✅ Complete Folder Structure Created

```
D:\Mozhi_Amudhu\
│
├── app/                           # Core application modules
│   ├── __init__.py               # Package initialization
│   ├── pdf_reader.py             # PDF text extraction module
│   ├── text_cleaner.py           # Text preprocessing (IndicNLP)
│   ├── summarizer.py             # Summarization (Ollama LLaMA-3)
│   ├── translator.py             # Translation (IndicTrans2)
│   └── tts_generator.py          # Text-to-Speech (Indic-TTS)
│
├── ui/                            # User interface
│   ├── __init__.py               # Package initialization
│   └── streamlit_app.py          # Main Streamlit application
│
├── assets/                        # Static files and temporary storage
│   ├── temp_audio/               # Generated audio files (WAV)
│   └── uploads/                  # Temporary PDF uploads
│
├── venv/                          # Virtual environment (existing)
│
├── .gitignore                     # Git ignore configuration
├── ARCHITECTURE.md                # Complete technical architecture
├── PROJECT_STRUCTURE.md           # This file
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

---

## 📋 Module Overview

### **1. app/pdf_reader.py**
- Extract text from PDF files
- Support multi-page documents
- Handle OCR for scanned PDFs (optional)

### **2. app/text_cleaner.py**
- Preprocess text using IndicNLP library
- Normalize whitespace and special characters
- Handle Indic language-specific text cleaning

### **3. app/summarizer.py**
- Generate two types of summaries:
  - **Official Summary:** Technical/formal language
  - **Simplified Summary:** Citizen-friendly language
- Use Ollama with LLaMA-3 model

### **4. app/translator.py**
- Translate English summaries to Tamil
- Use IndicTrans2 (AI4Bharat)
- Support batch translation

### **5. app/tts_generator.py**
- Convert Tamil text to speech
- Generate WAV audio files
- Use AI4Bharat Indic-TTS

### **6. ui/streamlit_app.py**
- Main user interface
- File upload and text input
- Display results and audio download
- Orchestrate all modules

---

## 🚀 Next Steps

1. **Install dependencies:**
   ```powershell
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install Ollama and download LLaMA-3:**
   ```bash
   # Download from: https://ollama.com/
   ollama pull llama3
   ```

3. **Implement module code** (ready for development)

4. **Run the application:**
   ```powershell
   streamlit run ui\streamlit_app.py
   ```

---

## 📚 Documentation Files

- **ARCHITECTURE.md** - Complete technical architecture with:
  - Architecture diagrams
  - Data flow descriptions
  - Module responsibilities
  - Library requirements
  - Deployment strategies
  
- **README.md** - Project overview
- **requirements.txt** - Python dependencies (to be populated)
- **.gitignore** - Version control exclusions

---

## 🔧 Development Status

- [x] Folder structure created
- [x] Module files initialized with placeholders
- [x] Architecture documentation complete
- [ ] Implement PDF reader
- [ ] Implement text cleaner
- [ ] Implement summarizer
- [ ] Implement translator
- [ ] Implement TTS generator
- [ ] Implement Streamlit UI
- [ ] Testing and validation
- [ ] Deployment

---

**Created:** 2025-11-25  
**Status:** Structure Complete - Ready for Implementation

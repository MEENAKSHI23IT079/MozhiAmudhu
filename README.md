# Mozhi Amudhu: Multilingual Government Circular Summarization System

**மொழி அமுது** - A Streamlit-based AI application for processing, summarizing, and translating government circulars into multiple languages.

## 🌟 Features

- **📄 PDF Text Extraction** - Extract text from government circular PDFs
- **🧹 Text Preprocessing** - Clean and normalize text (supports English & Tamil)
- **📝 Dual Summarization** - Generate both official and simplified summaries
- **🌐 Translation** - Translate summaries to Tamil using IndicTrans2
- **🔊 Text-to-Speech** - Convert Tamil summaries to audio
- **📥 Audio Download** - Download generated audio files

## 🏗️ Architecture

The system follows a modular pipeline architecture:

```
PDF Upload → Text Extraction → Text Cleaning → Summarization → Translation → TTS → Audio Download
```

For detailed architecture, see [ARCHITECTURE.md](ARCHITECTURE.md)

## 📋 Prerequisites

- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended for translation)
- Internet connection (first run only, for downloading models)

## 🚀 Quick Start

### 1. Clone or Download
```bash
cd D:\Mozhi_Amudhu
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
streamlit run ui\streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📦 Module Overview

### Core Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `app/pdf_reader.py` | Extract text from PDFs | ✅ Complete |
| `app/text_cleaner.py` | Preprocess and clean text | ✅ Complete |
| `app/summarizer.py` | Generate summaries (Ollama) | ⚠️ Placeholder |
| `app/translator.py` | Translate to Tamil (IndicTrans2) | ✅ Complete |
| `app/tts_generator.py` | Generate Tamil speech audio | ✅ Complete |
| `ui/streamlit_app.py` | Main Streamlit UI | ✅ Complete |

## 📖 Usage Guide

### Step 1: Upload Document
- **Option A**: Upload a PDF file
- **Option B**: Paste text directly

### Step 2: Extract & Clean
- Click "Extract Text from PDF" or "Use Pasted Text"
- System automatically cleans and preprocesses the text

### Step 3: Generate Summaries
- Click "Generate Official Summary" for formal summary
- Click "Generate Simplified Summary" for citizen-friendly version

### Step 4: Translate
- Click "Translate Summaries to Tamil"
- Wait for IndicTrans2 model to process (may take a few minutes on first run)

### Step 5: Generate Audio
- Click "Generate Tamil Audio"
- Listen to the audio preview
- Download the audio file

## 🔧 Configuration

### Using GPU (Optional)

For faster translation and TTS, use GPU:

1. Install PyTorch with CUDA:
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

2. Modify the device parameter in code from `"cpu"` to `"cuda"`

### Ollama Integration (TODO)

To enable full summarization with LLaMA-3:

1. Install Ollama: https://ollama.com/
2. Download LLaMA-3:
```bash
ollama pull llama3
```
3. Install Python client:
```powershell
pip install ollama
```
4. Update `app/summarizer.py` to use Ollama API

## 🧪 Testing Modules

Test individual modules:

```powershell
# Test PDF Reader
python app\pdf_reader.py path\to\file.pdf

# Test Text Cleaner
python app\text_cleaner.py

# Test Translator
python app\translator.py

# Test TTS Generator
python app\tts_generator.py

# Test Summarizer
python app\summarizer.py
```

## 📂 Project Structure

```
D:\Mozhi_Amudhu\
├── app/                      # Core modules
│   ├── pdf_reader.py
│   ├── text_cleaner.py
│   ├── summarizer.py
│   ├── translator.py
│   └── tts_generator.py
├── ui/
│   └── streamlit_app.py     # Main application
├── assets/
│   ├── temp_audio/          # Generated audio files
│   └── uploads/             # Temporary PDF uploads
├── models/                   # Downloaded AI models (auto-created)
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

## 🌐 Supported Languages

- **Input**: English, Tamil (bilingual support)
- **Output**: English → Tamil translation
- **TTS**: Tamil audio generation

## 🛠️ Technologies Used

- **Framework**: Streamlit
- **PDF Processing**: pdfplumber
- **Translation**: AI4Bharat IndicTrans2
- **TTS**: gTTS (primary), Coqui TTS (optional)
- **Summarization**: Ollama + LLaMA-3 (planned)

## ⚠️ Known Limitations

1. **Summarization**: Currently uses placeholder. Full Ollama integration pending.
2. **Translation**: First run downloads ~1GB models (one-time)
3. **TTS**: gTTS requires internet connection
4. **Performance**: Translation may be slow on CPU

## 🔜 Roadmap

- [ ] Complete Ollama integration for summarization
- [ ] Add support for more Indian languages (Hindi, Telugu, etc.)
- [ ] Implement batch processing for multiple PDFs
- [ ] Add authentication and user management
- [ ] Export summaries to PDF/Word
- [ ] API mode for programmatic access

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is intended for government and public use.

## 👥 Authors

Mozhi Amudhu Development Team

## 📞 Support

For issues or questions, please check:
- [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- [GitHub Issues](https://github.com/yourrepo/mozhi_amudhu/issues)

---

**மொழி அமுது** - Bridging language barriers in government communication

*Built with ❤️ for accessible governance*

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

PDF Upload → Text Extraction → Text Cleaning → Summarization → Translation → TTS → Audio Download


For detailed architecture, see **ARCHITECTURE.md**

## 📋 Prerequisites

- Python 3.9 or higher  
- 8GB RAM minimum (16GB recommended for translation)  
- Internet connection (first run only, for downloading models)

## 🚀 Quick Start

### 1. Navigate to project
cd D:\Mozhi_Amudhu


### 2. Create Virtual Environment


python -m venv venv
.\venv\Scripts\activate


### 3. Install Dependencies


pip install -r requirements.txt


### 4. Run the Application


streamlit run ui\streamlit_app.py


The app will open in your browser at **http://localhost:8501**

## 📦 Module Overview

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
- Upload a PDF or paste text manually

### Step 2: Extract & Clean  
- System automatically extracts and cleans text

### Step 3: Generate Summaries  
- **Official Summary**  
- **Simplified Summary**

### Step 4: Translate  
- Translate to Tamil using IndicTrans2

### Step 5: Generate Audio  
- Produce Tamil audio  
- Download file

## 🔧 Configuration

### Optional: Enable GPU
Install PyTorch with CUDA:



pip install torch --index-url https://download.pytorch.org/whl/cu118


Then update device in code to `"cuda"`.

### Ollama Summarization (TODO)

1. Install Ollama  
2. Download LLaMA-3  
3. Integrate in `summarizer.py`

## 🧪 Testing Individual Modules



python app\pdf_reader.py
python app\text_cleaner.py
python app\translator.py
python app\tts_generator.py
python app\summarizer.py


## 📂 Project Structure



D:\Mozhi_Amudhu
├── app/
│ ├── pdf_reader.py
│ ├── text_cleaner.py
│ ├── summarizer.py
│ ├── translator.py
│ └── tts_generator.py
├── ui/
│ └── streamlit_app.py
├── assets/
│ ├── temp_audio/
│ └── uploads/
├── models/
├── requirements.txt
├── README.md
└── ARCHITECTURE.md


## 🌐 Supported Languages

- **Input:** English, Tamil  
- **Output:** Tamil  
- **TTS:** Tamil audio  

## 🛠 Technologies Used

- Streamlit  
- pdfplumber  
- IndicTrans2  
- gTTS / Coqui TTS  
- Ollama (planned)

## ⚠️ Known Limitations

- Summarizer pending Ollama integration  
- Model download size 1GB  
- Slow translation on CPU  
- gTTS requires internet  

## 🔜 Roadmap

- Full Ollama summarization  
- Multiple language support  
- Batch PDF processing  
- Authentication  
- Export to PDF/Word  
- API mode  

## 🤝 Contributing

Contributions are welcome.

## 📄 License

For government and public use.

## 👥 Authors

Mozhi Amudhu Development Team

## 📞 Support

Refer to **ARCHITECTURE.md** or GitHub Issues.

---

**மொழி அமுது** — Bridging language barriers in government communication.  
*Built with ❤️ for accessible governance*
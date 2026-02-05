# AI Veterinary Assistance (AVA)

An intelligent veterinary diagnostic assistant powered by AI, featuring natural language processing, image analysis, and **voice input** capabilities.

## ✨ Key Features

- 🔍 **Intelligent Diagnosis** - AI-powered disease detection from symptoms
- 🎤 **Voice Input** - Record patient descriptions in English or Malayalam
- 📸 **Skin Disease Detection** - Computer vision for skin condition analysis
- 🤖 **AI Follow-up Questions** - Smart questioning to narrow down diagnoses
- 📊 **Disease Database** - Comprehensive MongoDB-backed disease repository
- 👥 **User Management** - Secure authentication and role-based access
- 📈 **Consultation History** - Track and review past diagnoses
- ⚙️ **Admin Panel** - Manage users and seed database

## 🎤 Voice Input (NEW!)

AVA now supports voice input for patient descriptions:
- **English** - Full support for English speech-to-text
- **Malayalam** - Malayalam speech with optional English translation
- **Offline Processing** - All processing happens locally (no cloud APIs)
- **Medical Terminology** - Good accuracy with veterinary terms

[📖 Voice Input Setup Guide](VOICE_INPUT_SETUP.md)

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Install Python packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# For voice input (optional)
pip install openai-whisper audio-recorder-streamlit
```

### 2. Install FFmpeg (Required for Voice Input)

**Windows:**
- Download from https://www.gyan.dev/ffmpeg/builds/
- Extract and add to PATH

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 3. Configure Database

Create a `.env` file:

```env
MONGO_URL=mongodb://localhost:27017/
MONGO_DB_NAME=veterinary_ai_db
```

### 4. Run the Application

```powershell
streamlit run app_streamlit.py
```

## 📦 Voice Input Installation

For a streamlined voice input setup, run:

```powershell
# Windows PowerShell
.\install_voice_input.ps1

# Or manually
pip install openai-whisper audio-recorder-streamlit
python test_voice_input.py
```

See [VOICE_INPUT_SETUP.md](VOICE_INPUT_SETUP.md) for detailed instructions.

## 📚 Documentation

- [Voice Input Setup Guide](VOICE_INPUT_SETUP.md) - Complete voice input setup
- [Quick Start Guide](QUICK_START.md) - Get started quickly
- [Installation Guide](INSTALL.md) - Detailed installation steps
- [System Documentation](SYSTEM_DOCUMENTATION.md) - Architecture and design
- [Demo Script](DEMO_SCRIPT.md) - Demonstration guide

## 🎯 Usage

1. **Login/Register** - Create an account or use admin credentials
2. **Navigate to Diagnosis** - Click "🔍 Diagnosis" in sidebar
3. **Enter Patient Info** - Type or use voice input to describe symptoms
4. **Analyze** - Click "Analyze Patient" to get AI diagnosis
5. **Answer Follow-ups** - Respond to AI-generated questions for better accuracy
6. **View Results** - See top disease matches with confidence scores

### Voice Input Usage

1. Click "🎤 Voice Input" expander
2. Select language (English/Malayalam)
3. Click microphone to record
4. Click again to stop
5. Add or replace text with transcription

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.8+
- **Database:** MongoDB
- **NLP:** spaCy, NLTK
- **ML/DL:** PyTorch
- **Voice:** OpenAI Whisper
- **Image Analysis:** Custom CNN models

## 🧪 Testing

```powershell
# Test all systems
python test_all_systems.py

# Test voice input specifically
python test_voice_input.py

# Run test suite
python test_suite.py
```

## 📊 Project Structure

```
AI-veterinary-assistance/
├── app_streamlit.py          # Main Streamlit application
├── voice_input.py             # Voice input module (NEW!)
├── main.py                    # Core AI assistant
├── requirements.txt           # Python dependencies
├── VOICE_INPUT_SETUP.md       # Voice setup guide (NEW!)
├── install_voice_input.ps1    # Voice install script (NEW!)
├── test_voice_input.py        # Voice test script (NEW!)
├── ava/                       # Core modules
│   ├── api/                   # API endpoints
│   ├── imaging/               # Image analysis
│   └── skin_disease/          # Skin disease detection
└── ml_training/               # ML model training
    ├── skin_disease/          # Skin disease model
    └── vet_followup_qa/       # Follow-up QA model
```

## 🔐 Security

- Secure password hashing
- Role-based access control
- Session management
- Local voice processing (no data sent to cloud)

## 🤝 Contributing

Contributions are welcome! Please read the documentation and follow the existing code style.

## 📝 License

This project is for educational and research purposes.

## 🆘 Support

For issues and questions:
1. Check the documentation files
2. Run test scripts to diagnose issues
3. See [VOICE_INPUT_SETUP.md](VOICE_INPUT_SETUP.md) for voice input troubleshooting

---

**Made with ❤️ for veterinary professionals**
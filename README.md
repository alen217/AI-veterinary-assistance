# 🐾 AI Veterinary Assistance System

> An intelligent, AI-powered diagnostic assistant that helps analyze veterinary patient symptoms and suggest possible conditions with high confidence scoring.

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.9+-red.svg)](https://pytorch.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Quick Start](#quick-start-5-minutes) • [Features](#features) • [Installation](#installation) • [Usage](#usage) • [Development](#development)

</div>

---

## 🎯 Overview

The **AI Veterinary Assistance System** is a full-stack application that combines Natural Language Processing (NLP), machine learning, and a comprehensive disease database to provide intelligent diagnostic support for veterinary professionals and pet owners.

**Key Innovation:** Uses a custom-trained PyTorch neural network to generate intelligent, contextual follow-up questions that progressively narrow down diagnoses from initial symptom analysis.

### What It Does
✅ **Analyzes Patient Symptoms** - Extracts key information from natural language descriptions  
✅ **Matches Diseases** - Compares symptoms against a comprehensive veterinary disease database  
✅ **AI-Driven Questioning** - Generates contextual follow-up questions to improve accuracy  
✅ **Real-time Updates** - Adjusts disease confidence scores as new information is provided  
✅ **Professional Reporting** - Generates detailed analysis reports with urgency levels  
✅ **History Tracking** - Stores and organizes all consultations  

---

## ✨ Features

### 🧠 Intelligent Analysis
- **NLP Symptom Extraction**: Automatically identifies symptoms, duration, severity, and context from free-form text
- **Smart Disease Matching**: Matches symptoms against 100+ diseases in the database with confidence scoring
- **AI Follow-up Questions**: Neural network generates contextual questions to refine diagnosis
- **Real-time Confidence Updates**: Watch confidence scores improve as you answer questions

### 🎨 User-Friendly Interfaces
- **Web UI (Streamlit)**: Beautiful, interactive dashboard for consultations and history
- **CLI Tool**: Quick command-line analysis for developers and terminal users
- **Python API**: Integrate into other applications

### 🔒 Professional Features
- **User Authentication**: Secure login system for different user types
- **Consultation History**: Track all patient analyses with timestamps
- **Severity Assessment**: Urgency levels (URGENT, HIGH, MODERATE, LOW)
- **Treatment Recommendations**: Evidence-based guidance from disease database
- **Configurable Thresholds**: Adjust confidence targets and question limits

### ⚡ Performance
- **100% Local Processing**: No external API calls (after model training)
- **Privacy-First**: All data stays on your server
- **Fast Analysis**: Results in seconds
- **Scalable Database**: MongoDB for handling thousands of consultations

---

## 🚀 Quick Start (5 Minutes)

### Minimum Requirements
- Python 3.8 or higher
- 2GB RAM minimum
- ~5GB disk space (for dependencies + model)

### Step 1: Clone & Setup
```bash
# Clone the repository
git clone https://github.com/alen217/AI-veterinary-assistance.git
cd AI-veterinary-assistance

# Create virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Tests (to verify installation)
```bash
# Run comprehensive test suite
python test_suite.py
```

You should see:
```
✅ PASS  NLP Analysis Test
✅ PASS  Database Connection Test
✅ PASS  Question Generation Test
✅ PASS  Complete Workflow Test
... and more!
```

### Step 3: Try the System
```bash
# Interactive mode
python main.py

# OR command-line mode
python main.py "My dog has been vomiting for 2 days"

# OR web interface (recommended)
streamlit run app_streamlit.py
```

The web app opens at: **http://localhost:8501**

---

## 📦 Installation

### Full Installation Guide

#### 1. **Python & Virtual Environment**
```bash
# Verify Python version
python --version  # Should be 3.8+

# Create isolated environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
```

#### 2. **Core Dependencies**
```bash
# Install PyTorch (choose one based on your system)
# CPU-only (faster install, works everywhere)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# OR GPU-enabled (if you have NVIDIA GPU with CUDA)
pip install torch torchvision
```

#### 3. **Project Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# (Optional but recommended) Download spaCy language model
python -m spacy download en_core_web_sm
```

#### 4. **Database Setup** (Optional for local demo)
- Default: Uses in-memory SQLite database
- Production: Requires MongoDB Atlas connection (add to `.env` file)

#### 5. **Train the AI Model** (Optional, ~30-60 min)
```bash
cd ml_training/skin_disease
python train.py

# Returns to project root when done
cd ../..
```

This trains a custom neural network on 5000+ synthetic veterinary cases.

#### 6. **Verify Installation**
```bash
python test_suite.py
```

All tests should pass ✅

---

## 💻 Usage

### 🖥️ Web Interface (Recommended)
```bash
streamlit run app_streamlit.py
```
- User-friendly dashboard
- Real-time analysis
- Beautiful visualizations
- History tracking
- Best for demos and regular users

### 📝 Command-Line Interface

**Interactive mode:**
```bash
python main.py
```
Select option "1. Analyze patient text" and paste patient description

**Direct analysis:**
```bash
python main.py "My 4-year-old golden retriever has been vomiting for 2 days and has severe diarrhea"
```

### 🐍 Python API
```python
from disease_predictor import DiseasePredictor
from nlp_patient_analyzer import NLPPatientAnalyzer

# Initialize
analyzer = NLPPatientAnalyzer()
predictor = DiseasePredictor()

# Analyze patient description
patient_data = analyzer.analyze("My dog has been vomiting for 3 days")

# Get disease predictions
results = predictor.predict(patient_data['symptoms'])

# Print results
for disease, confidence in results:
    print(f"{disease}: {confidence}% confidence")
```

### Example Patient Descriptions

**Gastrointestinal Issue:**
```
I have a 4-year-old male golden retriever weighing about 70 lbs.
He's been vomiting 2-3 times daily for 2 days and has severe diarrhea.
He's not eating and seems lethargic. His belly seems tender when I touch it.
```

**Skin Problem:**
```
My 2-year-old female cat has been scratching constantly for 3 weeks.
She has significant hair loss on her hind legs and back.
Her skin looks red and irritated.
```

**Respiratory Issue:**
```
My 5-year-old male beagle has had a persistent cough for 1 week.
He seems tired and doesn't want to play. He has nasal discharge.
His breathing sounds labored at times.
```

---

## 🏗️ Project Structure

```
AI-veterinary-assistance/
├── app.py                          # Flask web app (alternative UI)
├── app_streamlit.py                # Streamlit web interface ⭐
├── main.py                         # CLI entry point
├── requirements.txt                # Python dependencies
│
├── Core Analysis Engine
├── disease_predictor.py            # Disease matching algorithm
├── nlp_patient_analyzer.py         # NLP symptom extraction
├── follow_up_questions.py          # Follow-up question generation
├── dynamic_confidence_updater.py   # Real-time confidence adjustment
│
├── Data & Database
├── mongo_disease_repository.py     # MongoDB disease database
├── user_database.py                # User management
├── consultation_state_updater.py   # Consultation tracking
│
├── Machine Learning
├── ml_training/                    # Training scripts and models
│   └── skin_disease/
│       ├── train.py                # Model training pipeline
│       ├── model.pth               # Trained model weights
│       └── src/
│           ├── dataset.py          # Training dataset preparation
│           └── model.py            # Neural network architecture
│
├── Computer Vision (Optional)
├── ava/
│   ├── imaging/                    # Skin disease image analysis
│   ├── api/                        # REST API for predictions
│   └── skin_disease/               # Image classification model
│
├── Tests
├── test_suite.py                   # Comprehensive test suite
├── test_all_fixes.py               # Verification tests
│
└── Documentation
    ├── README.md                   # This file
    ├── QUICK_START.md              # Quick start guide
    ├── INSTALL.md                  # Detailed installation
    ├── SYSTEM_DOCUMENTATION.md     # Technical architecture
    └── FINAL_SETUP.md              # Deployment guide
```

---

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/alen217/AI-veterinary-assistance.git
cd AI-veterinary-assistance

# Create virtual environment
python -m venv venv
source venv/Scripts/activate

# Install with dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8  # Dev tools
```

### Running Tests

```bash
# Full test suite
python test_suite.py

# Specific test
python test_all_fixes.py

# With pytest (if installed)
pytest test_suite.py -v
```

### Key Components to Understand

#### NLP Analysis Engine (`nlp_patient_analyzer.py`)
Extracts structured information from free-form text:
```python
analyzer = NLPPatientAnalyzer()
result = analyzer.analyze("My 3-year-old dog has been vomiting")
# Returns: {
#   'animal_type': 'dog',
#   'age': 3,
#   'symptoms': [...],
#   'severity': '...',
#   ...
# }
```

#### Disease Predictor (`disease_predictor.py`)
Matches symptoms to diseases with confidence scoring:
```python
predictor = DiseasePredictor()
results = predictor.predict(symptoms)
# Returns: [('Parvovirus', 95), ('Gastroenteritis', 75), ...]
```

#### Follow-up Questions (`follow_up_questions.py`)
Generates intelligent questions using AI:
```python
generator = QuestionGenerator()
next_question = generator.generate(patient_data, current_diseases)
# Returns: "How many times has your dog vomited in 24 hours?"
```

### Extending the System

**Add new diseases to database:**
```python
from mongo_disease_repository import DiseaseRepository

repo = DiseaseRepository()
repo.add_disease({
    'name': 'New Condition',
    'symptoms': ['symptom1', 'symptom2'],
    'severity': 'moderate',
    'treatment': 'Treatment recommendation'
})
```

**Customize NLP extraction:**
Edit `nlp_patient_analyzer.py` to add new entities or symptoms

**Improve ML model:**
```bash
cd ml_training/skin_disease
# Modify train.py and retrain
python train.py
```

---

## 📊 How It Works

### 1️⃣ **Input Analysis**
```
Patient: "My 4-year-old golden retriever has been vomiting for 2 days"
          ↓
        NLP Engine
          ↓
Result: {
  'animal': 'dog',
  'breed': 'golden retriever',
  'age': 4,
  'symptoms': ['vomiting'],
  'duration': '2 days'
}
```

### 2️⃣ **Initial Disease Matching**
```
Symptoms: vomiting, lethargy, diarrhea
          ↓
    Disease Database
          ↓
Top Matches:
  • Parvovirus (75%)
  • Gastroenteritis (65%)
  • Food poisoning (55%)
```

### 3️⃣ **AI-Driven Refinement**
```
Question 1: "How many times has your dog vomited?"
Answer: "6 times"
          ↓
   Confidence Updated
          ↓
Parvovirus: 75% → 85%

Question 2: "Any fever or high temperature?"
Answer: "Yes, very hot"
          ↓
        Stop at >85%
          ↓
🎉 DIAGNOSIS: Parvovirus (92%)
```

### 4️⃣ **Professional Report**
```
CLINICAL ASSESSMENT
  Urgency: URGENT - Seek immediate care
  Condition: Parvovirus (92% confidence)
  
SYMPTOMS MATCHED
  ✓ Vomiting (6x daily)
  ✓ Fever/High temperature
  ✓ Lethargy
  
RECOMMENDED ACTIONS
  1. Contact veterinarian immediately
  2. Hospitalization likely needed
  3. Supportive care required
```

---

## 🐛 Troubleshooting

### Common Issues

**"No module named 'torch'"**
```bash
# PyTorch not installed
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**"Database connection failed"**
```bash
# Check MongoDB connection (if using cloud database)
# Verify .env file has correct credentials
# For local demo, remove MongoDB requirement
```

**"Model file not found"**
```bash
# Train the model:
cd ml_training/skin_disease
python train.py
cd ../..
```

**Slow predictions**
- First run: ~2-5 seconds (model loading)
- Subsequent runs: <1 second
- Use GPU for faster training/predictions

**Memory issues**
- Reduce batch size in training
- Use CPU version of PyTorch
- Close other applications

### Getting Help

1. Check `SYSTEM_DOCUMENTATION.md` for technical details
2. Review test output: `python test_suite.py`
3. Check logs and error messages carefully
4. Try the minimal example: `python main.py "test symptom"`

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test: `python test_suite.py`
4. Commit with clear messages: `git commit -m "Add: feature description"`
5. Push and create a Pull Request

### Areas for Contribution
- 🐛 Bug fixes and stability improvements
- 📚 Additional diseases to database
- 🧠 Improved NLP extraction
- 🎨 UI/UX enhancements
- 📖 Documentation improvements
- 🧪 More comprehensive tests

### Code Style
- Use Python 3.8+ features
- Follow PEP 8 conventions
- Add docstrings to functions
- Write tests for new features

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - 5-minute setup
- **[Installation Guide](INSTALL.md)** - Detailed installation steps
- **[System Documentation](SYSTEM_DOCUMENTATION.md)** - Technical architecture
- **[Setup for Demo](SETUP_FOR_DEMO.md)** - Demo configuration
- **[Final Setup](FINAL_SETUP.md)** - Production deployment

---

## 📋 Requirements

### System Requirements
- **OS**: Windows, macOS, Linux
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 5GB for dependencies and models
- **Internet**: For initial setup and MongoDB (optional)

### Python Dependencies
See `requirements.txt` for complete list:
- PyTorch (ML framework)
- spaCy (NLP processing)
- MongoDB (optional, database)
- Streamlit (web interface)
- Flask (alternative API)
- And more...

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [PyTorch](https://pytorch.org/) for machine learning
- NLP powered by [spaCy](https://spacy.io/)
- Web interface using [Streamlit](https://streamlit.io/)
- Database support via [MongoDB](https://www.mongodb.com/)

---

## 📞 Support & Contact

**For Questions or Issues:**
- 📧 Create an issue on GitHub
- 📖 Check the documentation files
- 🧪 Run `test_suite.py` to diagnose problems

---

<div align="center">

**Made with ❤️ for veterinary professionals and pet lovers**

⭐ If this project helped you, please consider giving it a star!

</div>
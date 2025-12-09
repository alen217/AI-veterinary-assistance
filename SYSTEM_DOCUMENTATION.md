# AI Veterinary Assistance - NLP Patient Analysis System

An intelligent veterinary AI system that analyzes patient text descriptions to extract disease/symptom information, searches a comprehensive database, and generates contextual follow-up questions.

## Features

### 1. **NLP Patient Text Analysis** (`nlp_patient_analyzer.py`)
- Extracts structured information from unstructured patient descriptions:
  - **Patient Demographics**: Animal type, age, breed, gender, weight
  - **Symptoms**: Detailed symptom extraction with:
    - Duration (e.g., "for 3 days")
    - Severity (mild, moderate, severe)
    - Frequency (daily, intermittent, etc.)
    - Context (surrounding text for additional context)
  - **Suspected Diseases**: AI-identified potential conditions with confidence scores
  - **Key Phrases**: Important medical terms extracted from text

- **Comprehensive Symptom Dictionary**: 30+ veterinary symptoms across multiple categories:
  - Gastrointestinal (vomiting, diarrhea, constipation, loss of appetite, abdominal pain)
  - Respiratory (cough, sneezing, labored breathing, wheezing)
  - Dermatological (itching, hair loss, rash, skin lesions)
  - Neurological (seizures, lethargy, incoordination, tremors)
  - Ocular (discharge, redness, swelling)
  - General (fever, dehydration, weight loss)

### 2. **Veterinary Database** (`veterinary_database.py`)
- SQLite-based disease and treatment database with:
  - **8+ Pre-loaded Common Veterinary Conditions**:
    - Gastroenteritis
    - Parvovirus
    - Otitis (ear infections)
    - Dermatitis/Allergies
    - Pneumonia
    - Conjunctivitis
    - Diabetes Mellitus
    - Epilepsy
  
  - For each disease:
    - Scientific name
    - Description and severity level
    - Common symptoms
    - Causes
    - Treatment recommendations
    - Prevention strategies
    - Species affected

- **Advanced Search Capabilities**:
  - Search by symptoms
  - Search by disease name
  - Search by keyword
  - Get disease-specific treatments

### 3. **Follow-up Question Generator** (`follow_up_questions.py`)
- Intelligently generates 6-8 contextual follow-up questions based on:
  - Missing symptom details (duration, severity, frequency)
  - Patient-specific information
  - Database disease information
  - Medical history requirements
  - Lifestyle factors
  
- **Question Categories**:
  - Symptom Details (duration, severity, progression)
  - Disease Confirmation (exposure, vaccination status)
  - Medical History (allergies, medications, previous conditions)
  - Lifestyle (diet, activity, recent changes)
  - Treatment History (previous treatments, home remedies)
  - Additional Symptoms (uncovered health issues)

### 4. **Main Application** (`main.py`)
- **Complete Orchestration**:
  1. Analyzes patient text using NLP
  2. Searches veterinary database for related conditions
  3. Generates follow-up questions
  4. Provides clinical recommendations
  5. Generates comprehensive report

- **Dual Interface**:
  - **Interactive Mode**: Type patient descriptions and get real-time analysis
  - **Command-Line Mode**: `python main.py "patient description text"`

- **Clinical Features**:
  - Urgency assessment (Low/Moderate/High/Urgent)
  - Recommended actions based on symptoms
  - Emergency indicators
  - Comprehensive clinical report generation
  - JSON export capability

## Installation

### 1. Clone the repository
```bash
cd c:\Users\Alen Denny\AVA\AI-veterinary-assistance
```

### 2. Create a Python virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy language model (optional but recommended)
```bash
python -m spacy download en_core_web_sm
```

## Quick Start

### Interactive Mode
```bash
python main.py
```

Then follow the prompts to:
1. Enter patient description
2. View analysis results
3. See follow-up questions
4. View clinical recommendations
5. Save results to JSON

### Command-Line Mode
```bash
python main.py "I have a 5 year old dog who has been vomiting and has diarrhea for 3 days. He seems lethargic and won't eat."
```

### Programmatic Usage
```python
from main import VeterinaryAIAssistant

with VeterinaryAIAssistant() as assistant:
    patient_text = "My cat has been scratching excessively and has hair loss..."
    result = assistant.analyze_patient_text(patient_text)
    
    # Print formatted report
    print(assistant.generate_report(result))
    
    # Save to JSON
    assistant.save_analysis(result, "my_analysis.json")
```

## Example Usage

### Input
```
I have a 5-year-old female golden retriever weighing about 65 lbs.
She has been vomiting and has diarrhea for the past 3 days.
She seems lethargic and is not eating well. Her belly seems tender.
She also has a slight fever. I'm worried about her.
```

### Output Includes
1. **Patient Information**
   - Animal Type: Dog
   - Age: 5 years old
   - Breed: Golden Retriever
   - Gender: Female
   - Weight: 65 lbs

2. **Extracted Symptoms**
   - Vomiting (Duration: 3 days, Severity: moderate)
   - Diarrhea (Duration: 3 days)
   - Lethargy
   - Loss of Appetite
   - Abdominal Pain
   - Fever

3. **Suspected Conditions** (from database)
   - Gastroenteritis (85% confidence)
   - Pancreatitis (65% confidence)
   - Parvovirus (45% confidence)

4. **Follow-up Questions**
   - "How often is your dog experiencing vomiting?"
   - "Is the diarrhea getting worse, staying the same, or improving?"
   - "Has your dog been exposed to contaminated food or other sick dogs?"
   - "Is your dog up to date on vaccinations?"
   - ...and more

5. **Clinical Assessment**
   - Urgency: HIGH - Schedule veterinary appointment within 24 hours
   - Recommended Actions: Hydration management, dietary changes, professional diagnosis
   - Emergency Indicators: When to seek immediate care

## System Architecture

```
┌─────────────────────────────────┐
│   Patient Text Input            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   NLP Patient Analyzer          │
│  - Extract symptoms             │
│  - Extract patient info         │
│  - Identify suspected diseases  │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────────┐  ┌────────────────────┐
│   Symptoms   │  │ Veterinary Database│
│              │  │ - Search by symptom│
│              │  │ - Match diseases   │
└────────┬─────┘  │ - Get treatments   │
         │        └────────┬───────────┘
         │                 │
         └────────┬────────┘
                  │
                  ▼
    ┌──────────────────────────┐
    │ Follow-up Question Gen.  │
    │ - Identify gaps          │
    │ - Generate questions     │
    │ - Prioritize by urgency  │
    └────────────┬─────────────┘
                 │
                 ▼
    ┌──────────────────────────┐
    │ Main Application         │
    │ - Orchestrate pipeline   │
    │ - Generate report        │
    │ - Save results           │
    └────────────┬─────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  Final Report │
         └───────────────┘
```

## File Structure

```
c:\Users\Alen Denny\AVA\AI-veterinary-assistance\
├── main.py                          # Main application & orchestration
├── nlp_patient_analyzer.py          # NLP analysis engine
├── veterinary_database.py           # Database management
├── follow_up_questions.py           # Question generation
├── requirements.txt                 # Python dependencies
├── README.md                        # Documentation
└── veterinary_database.db           # SQLite database (auto-created)
```

## Data Structures

### PatientInfo
```python
PatientInfo(
    animal_type: str,      # "dog", "cat", "bird", etc.
    age: str,              # "5 years old", "3 months", etc.
    breed: str,            # Breed name
    gender: str,           # "male" or "female"
    weight: str            # "65 lbs", "25 kg", etc.
)
```

### SymptomExtraction
```python
SymptomExtraction(
    symptom: str,          # "vomiting", "diarrhea", etc.
    duration: str,         # "3 days", "2 weeks", etc.
    severity: str,         # "mild", "moderate", "severe"
    frequency: str,        # "daily", "intermittent", etc.
    context: str           # Surrounding text
)
```

### DiseaseExtraction
```python
DiseaseExtraction(
    disease_name: str,     # Disease name
    confidence: float,     # 0.0 to 1.0
    related_symptoms: List[str]  # Matching symptoms
)
```

### FollowUpQuestion
```python
FollowUpQuestion(
    category: str,         # Question type
    question: str,         # The question text
    priority: int,         # 1-5, higher = more important
    reason: str            # Why this question matters
)
```

## Usage Examples

### Example 1: Analyze Gastrointestinal Issues
```bash
python main.py "My 3-year-old cat has been vomiting for 2 days and has diarrhea. She's not eating much and seems tired."
```

### Example 2: Analyze Skin Issues
```bash
python main.py "My dog is scratching constantly, especially around his ears and paws. He has some hair loss and red skin."
```

### Example 3: Analyze Respiratory Issues
```bash
python main.py "My bird has been coughing and has difficulty breathing. He's been like this for a week and is less active than usual."
```

## Extension Guide

### Adding New Diseases
```python
from veterinary_database import VeterinaryDatabase, Disease

db = VeterinaryDatabase()
new_disease = Disease(
    id=None,
    name="New Disease",
    scientific_name="Scientific Name",
    description="Description",
    common_symptoms=["symptom1", "symptom2"],
    causes=["cause1", "cause2"],
    treatment="Treatment info",
    prevention="Prevention info",
    severity="moderate",
    affected_species=["dog", "cat"]
)
disease_id = db.add_disease(new_disease)
```

### Adding New Symptoms
Edit the `_load_symptoms_dictionary()` method in `nlp_patient_analyzer.py`:
```python
"new_symptom": ["pattern1", "pattern2", "pattern3"],
```

## Dependencies

- **sqlite3**: Database management (built-in with Python)
- **spacy**: Advanced NLP (optional but recommended)
- **nltk**: Natural language toolkit (optional)
- **json**: Data serialization (built-in)
- **regex**: Pattern matching (built-in)
- **dataclasses**: Data structures (built-in for Python 3.7+)

## Limitations & Considerations

1. **Not a Replacement for Professional Diagnosis**: This system is for information gathering only. Always consult a licensed veterinarian for diagnosis and treatment.

2. **Database Coverage**: Initial database contains common conditions. Can be expanded with more diseases.

3. **Language**: Currently optimized for English-language patient descriptions.

4. **Symptom Extraction**: Relies on pattern matching. Complex descriptions may need clarification.

5. **Accuracy**: Confidence scores are estimates. Professional veterinary assessment is required.

## Future Enhancements

- [ ] Machine learning models for improved confidence scoring
- [ ] Integration with veterinary APIs and drug databases
- [ ] Multi-language support
- [ ] Advanced NLP with transformer models
- [ ] Web interface and API
- [ ] Electronic Health Record (EHR) integration
- [ ] Mobile application
- [ ] Drug interaction checking
- [ ] Treatment cost estimation

## License

Educational and veterinary assistance purposes.

## Support

For issues or suggestions, please refer to the project repository.

---

**Disclaimer**: This AI system is a diagnostic aid only and should never replace professional veterinary judgment. Always consult a licensed veterinarian for proper diagnosis and treatment.

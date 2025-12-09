# Quick Start Guide - Veterinary AI Assistant

## 5-Minute Quick Start

### Step 1: Setup (1 minute)
```bash
# Navigate to project directory
cd c:\Users\Alen Denny\AVA\AI-veterinary-assistance

# Install dependencies
pip install -r requirements.txt

# Download spacy model (optional but recommended)
python -m spacy download en_core_web_sm
```

### Step 2: Run Tests (2 minutes)
```bash
# Run comprehensive test suite to verify installation
python test_suite.py
```

This will run 6 different tests showing:
- NLP analysis capabilities
- Database functionality
- Question generation
- Complete workflow
- And more!

### Step 3: Try Interactive Mode (1 minute)
```bash
# Start interactive analysis session
python main.py
```

Then:
1. Select option "1. Analyze patient text"
2. Paste or type a patient description
3. Type "END" to finish input
4. View the complete analysis report

### Step 4: Try Command-Line Mode (1 minute)
```bash
python main.py "My dog has been vomiting for 3 days and won't eat. He seems lethargic."
```

## Example Patient Descriptions to Try

### Example 1: Gastrointestinal Issue
```
I have a 4-year-old male golden retriever weighing about 70 lbs.
He's been vomiting 2-3 times daily for 2 days and has severe diarrhea.
He's not eating and seems lethargic. His belly seems tender when I touch it.
I don't know what's wrong with him.
```

### Example 2: Skin Problem
```
My 2-year-old female cat has been scratching constantly for 3 weeks.
She has significant hair loss on her hind legs and back.
Her skin looks red and irritated. She's still eating well but seems stressed.
```

### Example 3: Respiratory Issue
```
My 5-year-old male beagle has had a persistent cough for 1 week.
He seems tired and doesn't want to play fetch like he usually does.
He has some nasal discharge and his breathing sounds labored at times.
He had his vaccinations updated 6 months ago.
```

## Understanding the Output

### 1. Patient Information
Shows extracted demographic data:
- Animal type, age, breed, gender, weight

### 2. Extracted Symptoms
Lists all identified symptoms with details:
- Duration (how long)
- Severity (mild/moderate/severe)
- Frequency (how often)
- Context (related information)

### 3. Possible Conditions (Database Match)
Shows potential diseases matched from database:
- Confidence percentage
- Severity level
- Description
- Treatment recommendations

### 4. Clinical Assessment
Provides urgency level:
- **URGENT**: Seek immediate veterinary care
- **HIGH**: Schedule appointment within 24 hours
- **MODERATE**: Schedule appointment within 48 hours
- **LOW**: Monitor and observe

### 5. Recommended Actions
Practical guidance:
- Hydration management
- Dietary adjustments
- When to seek care
- Important precautions

### 6. Follow-up Questions
Contextual questions to gather more information:
- Fill in symptom details
- Confirm potential diagnoses
- Medical history
- Lifestyle information

### 7. Emergency Signs
Critical warning signs requiring immediate veterinary attention

## Tips for Best Results

### 1. Provide Detailed Information
Better input = Better analysis

**Good:** "My 5-year-old dog has been vomiting 3 times daily for 2 days and has moderate abdominal pain"

**Better:** "My 5-year-old male golden retriever (70 lbs) has been vomiting 3 times daily for exactly 2 days. The vomiting is moderate in intensity. He has visible abdominal pain when touched. He hasn't eaten since yesterday. He seems lethargic."

### 2. Include Patient Demographics
- Animal type (dog, cat, bird, etc.)
- Age (important for condition likelihood)
- Breed (some breeds prone to specific conditions)
- Weight (helps assess severity)

### 3. Be Specific About Symptoms
- When did symptoms start?
- How severe are they?
- How often do they occur?
- Are they getting better or worse?

### 4. Mention Medical History
- Vaccinations
- Previous conditions
- Current medications
- Known allergies

### 5. Note Recent Changes
- Diet changes
- Environment changes
- Exposure to other animals
- Travel or new situations

## File Reference

| File | Purpose |
|------|---------|
| `main.py` | Main application - run this! |
| `nlp_patient_analyzer.py` | NLP engine - extracts info from text |
| `veterinary_database.py` | Disease database - stores condition info |
| `follow_up_questions.py` | Question generator - creates follow-ups |
| `test_suite.py` | Tests and examples |
| `requirements.txt` | Python dependencies |
| `veterinary_database.db` | SQLite database (auto-created) |

## Troubleshooting

### "Module not found" error
```bash
# Install all requirements
pip install -r requirements.txt
```

### "spacy model not found" warning
```bash
# Download the model (optional)
python -m spacy download en_core_web_sm
```

### Database errors
```bash
# Delete old database and let it recreate
rm veterinary_database.db
python main.py
```

### Special characters in input
- The system handles most text, but may work better with standard English characters
- Avoid excessive special characters or formatting

## What Happens Behind the Scenes

1. **Text Input** → Your patient description
2. **NLP Analysis** → Extract demographics, symptoms, conditions
3. **Database Search** → Find matching diseases
4. **Question Generation** → Create targeted follow-up questions
5. **Report Generation** → Format results
6. **Optional Export** → Save to JSON

## Next Steps

1. **Explore the code**: Read the source files to understand how it works
2. **Expand the database**: Add more diseases and treatments
3. **Add more symptoms**: Extend the symptom dictionary
4. **Custom questions**: Create domain-specific question templates
5. **Integration**: Connect to veterinary APIs or EHR systems

## Important Disclaimer

⚠️ **This system is for informational purposes only.**

It is NOT a replacement for professional veterinary diagnosis and treatment. Always:
- Consult a licensed veterinarian for diagnosis
- Follow veterinary professional guidance
- Seek immediate care for emergency situations
- Use this system as an information gathering tool

## Support

For issues or questions:
1. Check the test_suite.py for examples
2. Review the source code comments
3. Consult the SYSTEM_DOCUMENTATION.md
4. Review individual module docstrings

---

**Happy analyzing! Remember to always consult with a professional veterinarian.**

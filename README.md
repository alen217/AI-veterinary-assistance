# AI Veterinary Assistance

> **Now with MongoDB Support!** 🎉  
> Upgraded from SQLite to MongoDB for better scalability and flexibility.

An intelligent veterinary assistant system that analyzes patient descriptions, identifies symptoms, matches diseases from a comprehensive database, and generates relevant follow-up questions.

## 🆕 What's New

- **MongoDB Database**: Migrated from SQLite to MongoDB for improved scalability
- **Cloud-Ready**: Deploy easily to MongoDB Atlas
- **Flexible Schema**: Easy to add new fields and features
- **Migration Tools**: Automated script to migrate existing SQLite data

## Features

- 🔍 **Natural Language Processing**: Extracts patient information and symptoms from text
- 🗄️ **MongoDB Database**: Comprehensive veterinary disease database with symptom matching
- 🤖 **AI Analysis**: Intelligent disease matching and confidence scoring
- ❓ **Follow-up Questions**: Contextual question generation for better diagnosis
- 📊 **Detailed Reports**: Comprehensive analysis with recommendations
- ☁️ **Cloud-Ready**: Works with local MongoDB or MongoDB Atlas

## Quick Start

### Prerequisites

1. **MongoDB Atlas** - Free cloud database at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. **Python 3.7+**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/alen217/AI-veterinary-assistance.git
cd AI-veterinary-assistance

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up MongoDB Atlas (Free)
# - Go to https://www.mongodb.com/cloud/atlas
# - Create a free cluster
# - Get your connection string
# - Copy .env.example to .env
# - Add your connection string to .env

# 4. Run examples
python example_with_env.py
```

## Usage

### Basic Usage

```python
from main import VeterinaryAIAssistant

# Create assistant with MongoDB Atlas
mongo_url = "mongodb+srv://user:pass@cluster.mongodb.net/veterinary_ai_db"
with VeterinaryAIAssistant(mongo_url=mongo_url) as assistant:
    # Analyze patient
    patient_text = """
    My 5-year-old golden retriever has been vomiting and has diarrhea 
    for 3 days. He seems lethargic and won't eat.
    """
    
    result = assistant.analyze_patient_text(patient_text)
    print(assistant.generate_report(result))
```

### MongoDB Atlas (Cloud)

```python
from main import VeterinaryAIAssistant

# Connect to MongoDB Atlas
mongo_url = "mongodb+srv://user:password@cluster.mongodb.net/"
with VeterinaryAIAssistant(mongo_url=mongo_url) as assistant:
    # Use the assistant...
    pass
```

## Documentation

- 📘 **[MongoDB Migration Guide](MONGODB_MIGRATION_GUIDE.md)** - Complete setup and migration instructions
- 📙 **[Quick Reference](MONGODB_QUICK_REFERENCE.md)** - Common operations and examples
- 📗 **[Migration Summary](MONGODB_MIGRATION_SUMMARY.md)** - What changed and why
- 💻 **[Examples](mongodb_examples.py)** - 7 practical code examples

## Database Schema

### Diseases Collection
```javascript
{
  "name": "Gastroenteritis",
  "scientific_name": "Gastritis and Enteritis",
  "description": "Inflammation of the stomach and intestines...",
  "common_symptoms": ["vomiting", "diarrhea", "abdominal_pain"],
  "causes": ["dietary indiscretion", "bacterial infection"],
  "treatment": "Dietary management, antibiotics...",
  "prevention": "Consistent diet, avoid table scraps...",
  "severity": "moderate",
  "affected_species": ["dog", "cat", "rabbit"]
}
```

## Testing

```bash
# Run full test suite
python test_suite.py

# Run MongoDB examples
python mongodb_examples.py

# Verify MongoDB setup
python setup_mongodb.py
```

## Migration from SQLite

If you have existing SQLite data:

```bash
python migrate_sqlite_to_mongodb.py [sqlite_path] [mongo_url] [db_name]
```

See [MONGODB_MIGRATION_GUIDE.md](MONGODB_MIGRATION_GUIDE.md) for details.

## Project Structure

```
AI-veterinary-assistance/
├── main.py                          # Main application
├── veterinary_database.py           # MongoDB database (NEW!)
├── nlp_patient_analyzer.py          # NLP analysis
├── follow_up_questions.py           # Question generator
├── test_suite.py                    # Test suite
├── mongodb_examples.py              # Usage examples (NEW!)
├── migrate_sqlite_to_mongodb.py     # Migration script (NEW!)
├── setup_mongodb.py                 # Setup verification (NEW!)
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── MONGODB_MIGRATION_GUIDE.md       # Detailed MongoDB guide (NEW!)
├── MONGODB_QUICK_REFERENCE.md       # Quick reference (NEW!)
└── MONGODB_MIGRATION_SUMMARY.md     # Migration summary (NEW!)
```

## Requirements

```
pymongo>=4.0      # MongoDB driver
spacy>=3.0        # NLP processing
nltk>=3.6         # Text analysis
numpy>=1.21       # Data processing
pandas>=1.3       # Data handling
pytest>=6.2       # Testing
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- 📖 See documentation in `MONGODB_MIGRATION_GUIDE.md`
- 🐛 Report issues on GitHub
- 💬 Check `MONGODB_QUICK_REFERENCE.md` for common questions

## Acknowledgments

- Built with PyMongo and MongoDB
- NLP powered by spaCy and NLTK
- Designed for veterinary professionals

---

**Version**: 2.0 (MongoDB)  
**Last Updated**: December 10, 2025

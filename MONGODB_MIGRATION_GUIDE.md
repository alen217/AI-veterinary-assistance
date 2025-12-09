# MongoDB Migration Guide

## Overview

The Veterinary AI Assistant has been successfully migrated from SQLite to MongoDB. This guide provides instructions for setting up and using the MongoDB-based system.

## What Changed

### Database Implementation
- **Before**: SQLite database (`veterinary_database.db`)
- **After**: MongoDB with PyMongo driver

### Key Changes
1. **`veterinary_database.py`**: Complete rewrite to use MongoDB
   - Collections: `diseases`, `treatments`
   - Indexes on: `name`, `common_symptoms`, `severity`
   
2. **`main.py`**: Updated to accept MongoDB connection parameters
   - Constructor now takes `mongo_url` and `db_name` parameters
   
3. **`requirements.txt`**: Added `pymongo>=4.0` dependency

4. **Data Migration**: Created `migrate_sqlite_to_mongodb.py` script

## Prerequisites

### Install MongoDB

#### Windows
```powershell
# Download MongoDB Community Edition from:
# https://www.mongodb.com/try/download/community

# Or use Chocolatey:
choco install mongodb

# Or use MongoDB Atlas (cloud):
# https://www.mongodb.com/cloud/atlas
```

#### Mac
```bash
brew tap mongodb/brew
brew install mongodb-community
```

#### Linux
```bash
sudo apt-get install -y mongodb-org
```

### Start MongoDB

#### Local Installation
```powershell
# Windows - Start MongoDB service
net start MongoDB

# Or run mongod directly
mongod --dbpath C:\data\db
```

#### MongoDB Atlas (Cloud)
- Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your connection string
- Whitelist your IP address

## Installation

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Verify MongoDB Connection

```python
from pymongo import MongoClient

# Test connection
client = MongoClient("mongodb://localhost:27017/")
print(client.server_info())  # Should print server details
client.close()
```

## Usage

### Basic Usage (Local MongoDB)

```python
from main import VeterinaryAIAssistant

# Connect to local MongoDB (default)
assistant = VeterinaryAIAssistant()

# Analyze patient text
patient_text = """
My 5-year-old dog has been vomiting and has diarrhea for 3 days.
He seems lethargic and won't eat.
"""

result = assistant.analyze_patient_text(patient_text)
print(assistant.generate_report(result))

assistant.close()
```

### Custom MongoDB Connection

```python
from main import VeterinaryAIAssistant

# Connect to custom MongoDB instance
assistant = VeterinaryAIAssistant(
    mongo_url="mongodb://localhost:27017/",
    db_name="my_vet_db"
)

# Use the assistant...
assistant.close()
```

### MongoDB Atlas (Cloud)

```python
from main import VeterinaryAIAssistant

# Connect to MongoDB Atlas
mongo_url = "mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/"
assistant = VeterinaryAIAssistant(
    mongo_url=mongo_url,
    db_name="veterinary_ai_db"
)

# Use the assistant...
assistant.close()
```

### Using Context Manager

```python
from main import VeterinaryAIAssistant

with VeterinaryAIAssistant() as assistant:
    result = assistant.analyze_patient_text(patient_text)
    print(assistant.generate_report(result))
# Connection automatically closed
```

## Migrating Existing Data

If you have existing SQLite data, use the migration script:

### Basic Migration

```powershell
python migrate_sqlite_to_mongodb.py
```

### Custom Migration

```powershell
# Specify custom paths and URLs
python migrate_sqlite_to_mongodb.py <sqlite_db_path> <mongo_url> <mongo_db_name>

# Example:
python migrate_sqlite_to_mongodb.py "old_data.db" "mongodb://localhost:27017/" "vet_db"
```

### Migration Features
- ✓ Automatically maps SQLite IDs to MongoDB ObjectIds
- ✓ Skips duplicate entries
- ✓ Creates indexes
- ✓ Verifies migration
- ✓ Detailed progress reporting

## Database Schema

### Diseases Collection

```javascript
{
  "_id": ObjectId("..."),
  "name": "Gastroenteritis",
  "scientific_name": "Gastritis and Enteritis",
  "description": "Inflammation of the stomach...",
  "common_symptoms": ["vomiting", "diarrhea", "abdominal_pain"],
  "causes": ["dietary indiscretion", "bacterial infection"],
  "treatment": "Dietary management, antibiotics...",
  "prevention": "Consistent diet, avoid table scraps...",
  "severity": "moderate",
  "affected_species": ["dog", "cat", "rabbit"]
}
```

### Treatments Collection

```javascript
{
  "_id": ObjectId("..."),
  "disease_id": "507f1f77bcf86cd799439011",
  "name": "Antibiotic Therapy",
  "description": "Broad-spectrum antibiotic treatment",
  "medication": "Amoxicillin",
  "dosage": "10mg/kg twice daily",
  "duration": "7-10 days",
  "effectiveness": 0.85
}
```

## API Reference

### VeterinaryDatabase Class

```python
class VeterinaryDatabase:
    def __init__(self, mongo_url: str = "mongodb://localhost:27017/", 
                 db_name: str = "veterinary_ai_db"):
        """Initialize MongoDB connection"""
        
    def search_by_symptoms(self, symptoms: List[str]) -> List[Tuple[Disease, int]]:
        """Search diseases by symptoms"""
        
    def search_by_name(self, name: str) -> Optional[Disease]:
        """Search disease by name (case-insensitive)"""
        
    def search_by_keyword(self, keyword: str) -> List[Disease]:
        """Search diseases by keyword"""
        
    def add_disease(self, disease: Disease) -> str:
        """Add new disease, returns MongoDB ObjectId"""
        
    def get_all_diseases(self) -> List[Disease]:
        """Get all diseases"""
        
    def close(self):
        """Close connection"""
```

### Disease Dataclass

```python
@dataclass
class Disease:
    id: str  # MongoDB ObjectId as string
    name: str
    scientific_name: str
    description: str
    common_symptoms: List[str]
    causes: List[str]
    treatment: str
    prevention: str
    severity: str
    affected_species: List[str]
```

## Testing

Run the test suite to verify everything works:

```powershell
python test_suite.py
```

This will test:
- ✓ MongoDB connection
- ✓ Disease search operations
- ✓ Symptom matching
- ✓ Complete analysis workflow

## Troubleshooting

### Connection Errors

**Problem**: `ServerSelectionTimeoutError`

**Solution**:
```powershell
# Check if MongoDB is running
# Windows:
Get-Service MongoDB

# If not running:
net start MongoDB
```

### Authentication Errors

**Problem**: `Authentication failed`

**Solution**:
```python
# Include credentials in connection string
mongo_url = "mongodb://username:password@localhost:27017/"
assistant = VeterinaryAIAssistant(mongo_url=mongo_url)
```

### Database Not Found

**Problem**: Empty database after migration

**Solution**:
```python
# The database auto-populates with default data on first connection
db = VeterinaryDatabase()
diseases = db.get_all_diseases()
print(f"Found {len(diseases)} diseases")
db.close()
```

## Performance Tips

### Indexing

MongoDB automatically creates indexes on:
- `name` (unique)
- `common_symptoms` (for symptom search)
- `severity` (for filtering)

### Connection Pooling

PyMongo handles connection pooling automatically. For high-traffic applications:

```python
from pymongo import MongoClient

# Configure connection pool
client = MongoClient(
    "mongodb://localhost:27017/",
    maxPoolSize=50,
    minPoolSize=10
)
```

## Environment Variables

Create a `.env` file for configuration:

```env
MONGO_URL=mongodb://localhost:27017/
MONGO_DB_NAME=veterinary_ai_db
```

Load in your application:

```python
import os
from dotenv import load_dotenv

load_dotenv()

assistant = VeterinaryAIAssistant(
    mongo_url=os.getenv("MONGO_URL"),
    db_name=os.getenv("MONGO_DB_NAME")
)
```

## Backup and Restore

### Backup

```powershell
# Backup MongoDB database
mongodump --db=veterinary_ai_db --out=backup/

# Backup to compressed archive
mongodump --db=veterinary_ai_db --archive=backup.gz --gzip
```

### Restore

```powershell
# Restore from backup
mongorestore --db=veterinary_ai_db backup/veterinary_ai_db/

# Restore from archive
mongorestore --db=veterinary_ai_db --archive=backup.gz --gzip
```

## Advantages of MongoDB

1. **Flexible Schema**: Easy to add new fields without migrations
2. **Scalability**: Horizontal scaling with sharding
3. **JSON-Native**: Natural fit for Python dictionaries
4. **Rich Queries**: Powerful aggregation framework
5. **Cloud Ready**: Easy deployment to MongoDB Atlas

## Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoDB Compass](https://www.mongodb.com/products/compass) - GUI tool

## Support

For issues or questions:
1. Check this guide
2. Review MongoDB logs
3. Verify connection parameters
4. Test with sample code above

---

**Migration Date**: December 10, 2025  
**Version**: 2.0 (MongoDB)

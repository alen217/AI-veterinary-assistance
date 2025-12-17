# MongoDB Quick Reference for Veterinary AI

## Quick Start

```python
from veterinary_database import VeterinaryDatabase

# Connect to MongoDB
db = VeterinaryDatabase()

# Your code here...

db.close()
```

## Common Operations

### Search by Symptoms
```python
# Find diseases matching symptoms
results = db.search_by_symptoms(['vomiting', 'diarrhea', 'fever'])

for disease, match_count in results:
    print(f"{disease.name}: {match_count} symptoms match")
    print(f"Severity: {disease.severity}")
    print(f"Treatment: {disease.treatment}")
```

### Search by Name
```python
# Find specific disease (case-insensitive)
disease = db.search_by_name("Gastroenteritis")

if disease:
    print(f"Found: {disease.name}")
    print(f"Symptoms: {', '.join(disease.common_symptoms)}")
```

### Search by Keyword
```python
# Search in name or description
diseases = db.search_by_keyword("infection")

for disease in diseases:
    print(f"- {disease.name}")
```

### Add New Disease
```python
from veterinary_database import Disease

new_disease = Disease(
    id="",  # Will be auto-generated
    name="Kennel Cough",
    scientific_name="Canine Infectious Tracheobronchitis",
    description="Highly contagious respiratory disease",
    common_symptoms=["cough", "sneezing", "nasal_discharge"],
    causes=["viral infection", "bacterial infection"],
    treatment="Rest, antibiotics if bacterial, cough suppressants",
    prevention="Vaccination, avoid overcrowding",
    severity="mild",
    affected_species=["dog"]
)

disease_id = db.add_disease(new_disease)
print(f"Added disease with ID: {disease_id}")
```

### Get All Diseases
```python
all_diseases = db.get_all_diseases()
print(f"Total diseases: {len(all_diseases)}")

for disease in all_diseases:
    print(f"- {disease.name} ({disease.severity})")
```

## Connection Options

### Default (Local MongoDB)
```python
db = VeterinaryDatabase()
```

### Custom Local MongoDB
```python
db = VeterinaryDatabase(
    mongo_url="mongodb://localhost:27017/",
    db_name="my_custom_db"
)
```

### MongoDB Atlas (Cloud)
```python
db = VeterinaryDatabase(
    mongo_url="mongodb+srv://user:pass@cluster.mongodb.net/",
    db_name="veterinary_ai_db"
)
```

### With Authentication
```python
db = VeterinaryDatabase(
    mongo_url="mongodb://username:password@localhost:27017/",
    db_name="veterinary_ai_db"
)
```

## Direct MongoDB Queries

### Using PyMongo Directly
```python
# Access collections
diseases_collection = db.diseases
treatments_collection = db.treatments

# Find by severity
severe_diseases = diseases_collection.find({"severity": "severe"})
for disease in severe_diseases:
    print(disease["name"])

# Count documents
count = diseases_collection.count_documents({"severity": "moderate"})
print(f"Moderate diseases: {count}")

# Aggregate
pipeline = [
    {"$group": {
        "_id": "$severity",
        "count": {"$sum": 1}
    }}
]
results = diseases_collection.aggregate(pipeline)
for result in results:
    print(f"{result['_id']}: {result['count']} diseases")
```

## Common MongoDB Shell Commands

```bash
# Connect to MongoDB
mongosh

# Show databases
show dbs

# Use database
use veterinary_ai_db

# Show collections
show collections

# Find all diseases
db.diseases.find()

# Find one disease
db.diseases.findOne({name: "Gastroenteritis"})

# Count documents
db.diseases.countDocuments()

# Find by severity
db.diseases.find({severity: "severe"})

# Find by symptom
db.diseases.find({common_symptoms: "vomiting"})

# Create index
db.diseases.createIndex({name: 1}, {unique: true})

# Show indexes
db.diseases.getIndexes()
```

## Troubleshooting

### Check MongoDB Status
```powershell
# Windows
Get-Service MongoDB

# Start MongoDB
net start MongoDB
```

### Test Connection
```python
from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    print("✓ Connected:", client.server_info()["version"])
except Exception as e:
    print("✗ Connection failed:", e)
finally:
    client.close()
```

### View Database Contents
```python
db = VeterinaryDatabase()

print(f"Diseases: {db.diseases.count_documents({})}")
print(f"Treatments: {db.treatments.count_documents({})}")

# Sample data
sample = db.diseases.find_one()
print(f"Sample disease: {sample['name'] if sample else 'None'}")

db.close()
```

## Data Structure Reference

### Disease Document
```python
{
    "_id": ObjectId("..."),
    "name": str,
    "scientific_name": str,
    "description": str,
    "common_symptoms": [str, ...],
    "causes": [str, ...],
    "treatment": str,
    "prevention": str,
    "severity": "mild" | "moderate" | "severe",
    "affected_species": [str, ...]
}
```

### Treatment Document
```python
{
    "_id": ObjectId("..."),
    "disease_id": str,  # References disease._id
    "name": str,
    "description": str,
    "medication": str,
    "dosage": str,
    "duration": str,
    "effectiveness": float  # 0.0 to 1.0
}
```

## Performance Tips

1. **Use Indexes**: Already created on `name`, `common_symptoms`, `severity`
2. **Limit Results**: Use `.limit()` for large result sets
3. **Project Fields**: Only fetch needed fields
4. **Close Connections**: Always call `db.close()` or use context manager

## Best Practices

```python
# ✓ Good: Use context manager
with VeterinaryDatabase() as db:
    diseases = db.get_all_diseases()
    # Process diseases...
# Connection automatically closed

# ✓ Good: Check existence before adding
existing = db.search_by_name("NewDisease")
if not existing:
    db.add_disease(new_disease)

# ✓ Good: Handle errors
try:
    disease = db.search_by_name("Unknown")
except Exception as e:
    print(f"Error: {e}")
```

## Environment Setup

Create `.env` file:
```env
MONGO_URL=mongodb://localhost:27017/
MONGO_DB_NAME=veterinary_ai_db
```

Use in code:
```python
import os
from dotenv import load_dotenv

load_dotenv()

db = VeterinaryDatabase(
    mongo_url=os.getenv("MONGO_URL"),
    db_name=os.getenv("MONGO_DB_NAME")
)
```

---

**Need More Help?**  
See `MONGODB_MIGRATION_GUIDE.md` for detailed documentation.

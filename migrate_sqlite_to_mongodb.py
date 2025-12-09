"""
Migration Script: SQLite to MongoDB
Transfers existing veterinary database data from SQLite to MongoDB
"""

import sqlite3
import json
from pymongo import MongoClient
from typing import List, Dict


def migrate_sqlite_to_mongodb(
    sqlite_db_path: str = "veterinary_database.db",
    mongo_url: str = "mongodb://localhost:27017/",
    mongo_db_name: str = "veterinary_ai_db"
):
    """
    Migrate data from SQLite database to MongoDB
    
    Args:
        sqlite_db_path: Path to SQLite database file
        mongo_url: MongoDB connection URL
        mongo_db_name: MongoDB database name
    """
    print(f"Starting migration from SQLite to MongoDB...")
    print(f"SQLite database: {sqlite_db_path}")
    print(f"MongoDB URL: {mongo_url}")
    print(f"MongoDB database: {mongo_db_name}\n")
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        print("✓ Connected to SQLite database")
    except Exception as e:
        print(f"✗ Failed to connect to SQLite: {e}")
        return False
    
    # Connect to MongoDB
    try:
        mongo_client = MongoClient(mongo_url)
        mongo_db = mongo_client[mongo_db_name]
        diseases_collection = mongo_db["diseases"]
        treatments_collection = mongo_db["treatments"]
        print("✓ Connected to MongoDB\n")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        sqlite_conn.close()
        return False
    
    # Migrate diseases
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM diseases")
    diseases = cursor.fetchall()
    
    print(f"Migrating {len(diseases)} diseases...")
    disease_id_map = {}  # Map old SQLite IDs to new MongoDB IDs
    
    for disease in diseases:
        disease_dict = dict(disease)
        
        # Parse JSON fields
        try:
            common_symptoms = json.loads(disease_dict['common_symptoms'])
            causes = json.loads(disease_dict['causes'])
            affected_species = json.loads(disease_dict['affected_species'])
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: Error parsing disease '{disease_dict.get('name', 'unknown')}': {e}")
            continue
        
        # Prepare MongoDB document
        mongo_doc = {
            "name": disease_dict['name'],
            "scientific_name": disease_dict['scientific_name'],
            "description": disease_dict['description'],
            "common_symptoms": common_symptoms,
            "causes": causes,
            "treatment": disease_dict['treatment'],
            "prevention": disease_dict['prevention'],
            "severity": disease_dict['severity'],
            "affected_species": affected_species
        }
        
        # Check if disease already exists
        existing = diseases_collection.find_one({"name": disease_dict['name']})
        if existing:
            print(f"  ⊙ Disease '{disease_dict['name']}' already exists, skipping...")
            disease_id_map[disease_dict['id']] = str(existing['_id'])
        else:
            result = diseases_collection.insert_one(mongo_doc)
            disease_id_map[disease_dict['id']] = str(result.inserted_id)
            print(f"  ✓ Migrated: {disease_dict['name']}")
    
    print(f"\n✓ Diseases migration complete\n")
    
    # Migrate treatments
    cursor.execute("SELECT * FROM treatments")
    treatments = cursor.fetchall()
    
    print(f"Migrating {len(treatments)} treatments...")
    
    for treatment in treatments:
        treatment_dict = dict(treatment)
        
        # Map old disease_id to new MongoDB ID
        old_disease_id = treatment_dict['disease_id']
        if old_disease_id not in disease_id_map:
            print(f"  Warning: Cannot find disease for treatment '{treatment_dict.get('name', 'unknown')}'")
            continue
        
        new_disease_id = disease_id_map[old_disease_id]
        
        # Prepare MongoDB document
        mongo_doc = {
            "disease_id": new_disease_id,
            "name": treatment_dict['name'],
            "description": treatment_dict['description'],
            "medication": treatment_dict['medication'],
            "dosage": treatment_dict['dosage'],
            "duration": treatment_dict['duration'],
            "effectiveness": treatment_dict['effectiveness']
        }
        
        # Check if treatment already exists
        existing = treatments_collection.find_one({
            "disease_id": new_disease_id,
            "name": treatment_dict['name']
        })
        
        if existing:
            print(f"  ⊙ Treatment '{treatment_dict['name']}' already exists, skipping...")
        else:
            treatments_collection.insert_one(mongo_doc)
            print(f"  ✓ Migrated: {treatment_dict['name']}")
    
    print(f"\n✓ Treatments migration complete\n")
    
    # Create indexes
    print("Creating indexes...")
    diseases_collection.create_index("name", unique=True)
    diseases_collection.create_index("common_symptoms")
    diseases_collection.create_index("severity")
    print("✓ Indexes created\n")
    
    # Cleanup
    sqlite_conn.close()
    mongo_client.close()
    
    print("="*60)
    print("MIGRATION COMPLETE!")
    print(f"  Diseases migrated: {len(diseases)}")
    print(f"  Treatments migrated: {len(treatments)}")
    print("="*60)
    
    return True


def verify_migration(
    mongo_url: str = "mongodb://localhost:27017/",
    mongo_db_name: str = "veterinary_ai_db"
):
    """
    Verify the migration by checking document counts
    
    Args:
        mongo_url: MongoDB connection URL
        mongo_db_name: MongoDB database name
    """
    print("\nVerifying migration...")
    
    try:
        mongo_client = MongoClient(mongo_url)
        mongo_db = mongo_client[mongo_db_name]
        
        diseases_count = mongo_db["diseases"].count_documents({})
        treatments_count = mongo_db["treatments"].count_documents({})
        
        print(f"  Diseases in MongoDB: {diseases_count}")
        print(f"  Treatments in MongoDB: {treatments_count}")
        
        # Sample a few diseases
        print("\nSample diseases:")
        for disease in mongo_db["diseases"].find().limit(3):
            print(f"  - {disease['name']} (Severity: {disease['severity']})")
        
        mongo_client.close()
        print("\n✓ Verification complete")
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")


if __name__ == "__main__":
    import sys
    
    # Default values
    sqlite_path = "veterinary_database.db"
    mongo_url = "mongodb://localhost:27017/"
    mongo_db = "veterinary_ai_db"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        sqlite_path = sys.argv[1]
    if len(sys.argv) > 2:
        mongo_url = sys.argv[2]
    if len(sys.argv) > 3:
        mongo_db = sys.argv[3]
    
    print("\n" + "="*60)
    print("VETERINARY DATABASE MIGRATION: SQLite → MongoDB")
    print("="*60 + "\n")
    
    # Run migration
    success = migrate_sqlite_to_mongodb(sqlite_path, mongo_url, mongo_db)
    
    if success:
        # Verify migration
        verify_migration(mongo_url, mongo_db)
    else:
        print("\n✗ Migration failed")
        sys.exit(1)

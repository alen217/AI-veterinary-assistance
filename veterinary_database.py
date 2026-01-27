"""
Disease and Treatment Database - MongoDB Version
Provides storage and retrieval of veterinary disease information
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pymongo import MongoClient
import hashlib


@dataclass
class Disease:
    """Disease information"""
    id: int
    name: str
    scientific_name: str
    description: str
    common_symptoms: List[str]
    causes: List[str]
    treatment: str
    prevention: str
    severity: str  # mild, moderate, severe
    affected_species: List[str]


@dataclass
class TreatmentOption:
    """Treatment option for a disease"""
    id: int
    disease_id: int
    name: str
    description: str
    medication: str
    dosage: str
    duration: str
    effectiveness: float  # 0-1


class VeterinaryDatabase:
    """
    Database for storing and retrieving veterinary disease information using MongoDB
    """
    
    def __init__(self, mongo_url: str = None, db_name: str = "veterinary_db"):
        """Initialize MongoDB connection"""
        if mongo_url is None:
            mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
        
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        self.diseases_collection = self.db.diseases
        self.treatments_collection = self.db.treatments
        self.symptoms_collection = self.db.symptoms
        self.analysis_history_collection = self.db.analysis_history
        self.users = self.db.users
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with indexes"""
        # Create indexes for better performance (if they don't exist)
        try:
            self.diseases_collection.create_index("name")
        except:
            pass  # Index might already exist
        try:
            self.users.create_index("username", unique=True)
        except:
            pass  # Index might already exist
        self._populate_default_data()
    
    def _populate_default_data(self):
        """Populate database with default veterinary information"""
        # Check if data already exists
        if self.diseases_collection.count_documents({}) > 0:
            return
        
        diseases_data = [
            {
                "name": "Gastroenteritis",
                "scientific_name": "Gastritis and Enteritis",
                "description": "Inflammation of the stomach and intestines, commonly caused by dietary changes, infections, or ingestion of foreign objects.",
                "common_symptoms": ["vomiting", "diarrhea", "abdominal_pain", "loss_of_appetite"],
                "causes": ["dietary indiscretion", "bacterial infection", "viral infection", "parasites"],
                "treatment": "Dietary management, antibiotics if bacterial, supportive care with fluids",
                "prevention": "Consistent diet, avoid table scraps, regular deworming",
                "severity": "moderate",
                "affected_species": ["dog", "cat", "rabbit"]
            },
            {
                "name": "Parvovirus",
                "scientific_name": "Canine Parvovirus (CPV)",
                "description": "Highly contagious viral infection affecting the gastrointestinal tract, bone marrow, and sometimes the heart.",
                "common_symptoms": ["vomiting", "diarrhea", "lethargy", "loss_of_appetite", "fever"],
                "causes": ["viral infection", "unvaccinated animals"],
                "treatment": "Supportive care, IV fluids, anti-emetics, antibiotics for secondary infections",
                "prevention": "Vaccination, good hygiene",
                "severity": "severe",
                "affected_species": ["dog"]
            },
            {
                "name": "Otitis",
                "scientific_name": "Ear Inflammation",
                "description": "Infection or inflammation of the ear canal, commonly caused by bacteria, yeast, or mites.",
                "common_symptoms": ["itching", "discharge", "redness_eye"],
                "causes": ["ear mites", "bacterial infection", "yeast infection", "allergies"],
                "treatment": "Ear cleaning, topical antibiotics/antifungals, anti-inflammatory drops",
                "prevention": "Regular ear cleaning, treat underlying allergies, moisture control",
                "severity": "mild",
                "affected_species": ["dog", "cat", "rabbit"]
            },
            {
                "name": "Dermatitis",
                "scientific_name": "Allergic Dermatitis",
                "description": "Skin inflammation caused by allergic reactions to food, environment, or parasites.",
                "common_symptoms": ["itching", "redness", "hair_loss"],
                "causes": ["allergies", "fleas", "contact irritants"],
                "treatment": "Identify and remove allergen, antihistamines, topical treatments",
                "prevention": "Regular flea control, hypoallergenic diet if needed",
                "severity": "mild",
                "affected_species": ["dog", "cat"]
            },
            {
                "name": "Upper Respiratory Infection",
                "scientific_name": "Feline/Canine Upper Respiratory Infection",
                "description": "Viral or bacterial infection affecting the nose, throat, and sinuses.",
                "common_symptoms": ["sneezing", "nasal_discharge", "coughing", "lethargy"],
                "causes": ["viral infection", "bacterial infection", "stress"],
                "treatment": "Supportive care, antibiotics if bacterial, antiviral medications",
                "prevention": "Vaccination, minimize stress, good ventilation",
                "severity": "moderate",
                "affected_species": ["dog", "cat"]
            }
        ]
        
        # Insert default diseases
        for disease_data in diseases_data:
            self.diseases_collection.insert_one(disease_data)
    
    def search_by_symptoms(self, symptoms: List[str], limit: int = 10) -> List[Tuple[Disease, int]]:
        """Search for diseases by symptoms"""
        results = []
        
        # Search for diseases containing any of the symptoms
        for disease_doc in self.diseases_collection.find():
            match_count = sum(1 for symptom in symptoms 
                            if symptom.lower() in [s.lower() for s in disease_doc.get('common_symptoms', [])])
            
            if match_count > 0:
                disease = Disease(
                    id=str(disease_doc['_id']),
                    name=disease_doc['name'],
                    scientific_name=disease_doc['scientific_name'],
                    description=disease_doc['description'],
                    common_symptoms=disease_doc['common_symptoms'],
                    causes=disease_doc['causes'],
                    treatment=disease_doc['treatment'],
                    prevention=disease_doc['prevention'],
                    severity=disease_doc['severity'],
                    affected_species=disease_doc['affected_species']
                )
                results.append((disease, match_count))
        
        # Sort by match count (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def search_by_name(self, disease_name: str) -> Optional[Disease]:
        """Search for a specific disease by name"""
        disease_doc = self.diseases_collection.find_one({"name": {"$regex": disease_name, "$options": "i"}})
        
        if disease_doc:
            return Disease(
                id=str(disease_doc['_id']),
                name=disease_doc['name'],
                scientific_name=disease_doc['scientific_name'],
                description=disease_doc['description'],
                common_symptoms=disease_doc['common_symptoms'],
                causes=disease_doc['causes'],
                treatment=disease_doc['treatment'],
                prevention=disease_doc['prevention'],
                severity=disease_doc['severity'],
                affected_species=disease_doc['affected_species']
            )
        return None
    
    def get_all_diseases(self) -> List[Disease]:
        """Get all diseases in database"""
        diseases = []
        for disease_doc in self.diseases_collection.find():
            diseases.append(Disease(
                id=str(disease_doc['_id']),
                name=disease_doc['name'],
                scientific_name=disease_doc['scientific_name'],
                description=disease_doc['description'],
                common_symptoms=disease_doc['common_symptoms'],
                causes=disease_doc['causes'],
                treatment=disease_doc['treatment'],
                prevention=disease_doc['prevention'],
                severity=disease_doc['severity'],
                affected_species=disease_doc['affected_species']
            ))
        return diseases
    
    # User management methods for authentication
    def ensure_default_users(self):
        """Create default admin and user accounts from environment variables"""
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        user_username = os.getenv("USER_USERNAME", "user")
        user_password = os.getenv("USER_PASSWORD", "user123")
        
        # Check if users already exist
        if self.users.count_documents({"username": admin_username}) == 0:
            hashed_admin = hashlib.sha256(admin_password.encode()).hexdigest()
            self.users.insert_one({
                "username": admin_username,
                "password": hashed_admin,
                "role": "admin"
            })
        
        if self.users.count_documents({"username": user_username}) == 0:
            hashed_user = hashlib.sha256(user_password.encode()).hexdigest()
            self.users.insert_one({
                "username": user_username,
                "password": hashed_user,
                "role": "user"
            })
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials and return user info if valid"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = self.users.find_one({"username": username, "password": hashed_password})
        
        if user:
            return {
                "username": user['username'],
                "role": user['role'],
                "created_at": user.get('created_at', '')
            }
        return None
    
    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user account"""
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.users.insert_one({
                "username": username,
                "password": hashed_password,
                "role": role
            })
            return True
        except Exception:
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (excluding passwords)"""
        return [{"username": user['username'], "role": user['role'], "created_at": user.get('created_at', '')} 
                for user in self.users.find({}, {"password": 0})]
    
    def get_user_analysis_history(self, username: str, limit: int = 50) -> List[Dict]:
        """Get analysis history for a specific user"""
        try:
            history = list(self.analysis_history_collection.find(
                {"username": username}
            ).sort("timestamp", -1).limit(limit))
            return history
        except Exception:
            return []
    
    def save_analysis(self, username: str, patient_text: str, analysis_result: Dict) -> bool:
        """Save analysis result to history"""
        try:
            from datetime import datetime
            self.analysis_history_collection.insert_one({
                "username": username,
                "patient_text": patient_text,
                "analysis_result": analysis_result,
                "timestamp": datetime.utcnow()
            })
            return True
        except Exception:
            return False
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Properties for backward compatibility with app_streamlit.py
    @property
    def diseases(self):
        """Alias for diseases_collection"""
        return self.diseases_collection
    
    @property
    def treatments(self):
        """Alias for treatments_collection"""
        return self.treatments_collection
    
    @property
    def symptoms(self):
        """Alias for symptoms_collection"""
        return self.symptoms_collection
    
    @property
    def analysis_history(self):
        """Alias for analysis_history_collection"""
        return self.analysis_history_collection


if __name__ == "__main__":
    # Example usage
    db = VeterinaryDatabase()
    
    # Search by symptoms
    print("Searching for diseases with 'cough' and 'fever'...")
    results = db.search_by_symptoms(['cough', 'fever'])
    for disease, match_count in results[:3]:
        print(f"\n{disease.name} ({match_count} symptoms match)")
        print(f"  Description: {disease.description}")
        print(f"  Severity: {disease.severity}")
    
    # Search by name
    print("\n" + "="*60)
    print("Searching for 'Gastroenteritis'...")
    disease = db.search_by_name("Gastroenteritis")
    if disease:
        print(f"\nFound: {disease.name}")
        print(f"Scientific Name: {disease.scientific_name}")
        print(f"Symptoms: {', '.join(disease.common_symptoms)}")
        print(f"Treatment: {disease.treatment}")
    
    db.close()

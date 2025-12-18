"""
Disease and Treatment Database
Provides storage and retrieval of veterinary disease information
MongoDB Implementation
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import ObjectId

try:
    import bcrypt  # type: ignore
except Exception:  # pragma: no cover
    bcrypt = None


@dataclass
class Disease:
    """Disease information"""
    id: str
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
    id: str
    disease_id: str
    name: str
    description: str
    medication: str
    dosage: str
    duration: str
    effectiveness: float  # 0-1


class VeterinaryDatabase:
    """
    Database for storing and retrieving veterinary information using MongoDB
    """
    
    def __init__(
        self,
        mongo_url: Optional[str] = None,
        db_name: Optional[str] = None,
        server_selection_timeout_ms: int = 8000,
    ):
        """Initialize MongoDB connection.

        If `mongo_url` or `db_name` are not provided, values are read from
        environment variables `MONGO_URL` and `MONGO_DB_NAME` (if available).
        """
        # Best-effort dotenv load (keeps library usable even if python-dotenv isn't installed)
        # Uses a robust lookup so running from other working directories still works.
        try:  # pragma: no cover
            from dotenv import load_dotenv, find_dotenv  # type: ignore

            dotenv_path = find_dotenv(usecwd=True) or str(Path(__file__).resolve().parent / ".env")
            load_dotenv(dotenv_path=dotenv_path, override=False)
        except Exception:
            pass

        resolved_mongo_url = mongo_url or os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
        resolved_db_name = db_name or os.getenv("MONGO_DB_NAME") or "veterinary_ai_db"

        self.client = MongoClient(resolved_mongo_url, serverSelectionTimeoutMS=server_selection_timeout_ms)
        self.db = self.client[resolved_db_name]

        # Fail fast with a clear message (especially when a machine accidentally falls back to localhost).
        try:
            self.client.admin.command("ping")
        except Exception as exc:
            is_local_default = any(host in resolved_mongo_url for host in ("localhost", "127.0.0.1", "mongodb://localhost"))
            hint = ""
            if is_local_default:
                hint = (
                    "\n\nIt looks like you're trying to connect to a local MongoDB instance, but it's not running on this computer. "
                    "If you intended to use MongoDB Atlas, set MONGO_URL in a .env file (copy .env.example -> .env) "
                    "or as an environment variable."
                )
            raise RuntimeError(
                f"MongoDB connection failed for URL={resolved_mongo_url!r}, DB={resolved_db_name!r}." + hint
            ) from exc
        
        # Collections
        self.diseases = self.db["diseases"]
        self.treatments = self.db["treatments"]
        self.users = self.db["users"]
        self.symptoms = self.db["symptoms"]
        
        # Create indexes
        self.diseases.create_index("name", unique=True)
        self.diseases.create_index("common_symptoms")
        self.diseases.create_index("severity")

        self.users.create_index("username", unique=True)
        self.users.create_index("role")
        self.users.create_index("created_at")

        self.symptoms.create_index("key", unique=True)
        self.symptoms.create_index("system")
        
        self._populate_default_data()

    # ---------------------------------------------------------------------
    # Users / Auth
    # ---------------------------------------------------------------------

    def _require_bcrypt(self):
        if bcrypt is None:
            raise RuntimeError("bcrypt is required for user authentication. Install with: pip install bcrypt")

    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a user in MongoDB.

        Returns False if the username already exists.
        """
        self._require_bcrypt()
        username = username.strip()
        role = role.strip() or "user"
        if not username:
            raise ValueError("username is required")

        existing = self.users.find_one({"username": username})
        if existing:
            return False

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        self.users.insert_one(
            {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "created_at": datetime.now(timezone.utc),
                "last_login_at": None,
            }
        )
        return True

    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify a username/password. Returns the user document (without password_hash) on success."""
        self._require_bcrypt()
        user = self.users.find_one({"username": username})
        if not user:
            return None
        stored = user.get("password_hash")
        if not stored:
            return None

        ok = bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
        if not ok:
            return None

        self.users.update_one({"_id": user["_id"]}, {"$set": {"last_login_at": datetime.now(timezone.utc)}})
        user.pop("password_hash", None)
        return user

    def ensure_default_users(self):
        """Ensure default admin/user exist (values from env; safe for demos)."""
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        user_username = os.getenv("DEFAULT_USER_USERNAME", "user")
        user_password = os.getenv("DEFAULT_USER_PASSWORD", "user123")

        # Only create if missing
        if not self.users.find_one({"username": admin_username}):
            self.create_user(admin_username, admin_password, role="admin")
        if not self.users.find_one({"username": user_username}):
            self.create_user(user_username, user_password, role="user")
    
    def _populate_default_data(self):
        """Populate database with default veterinary information"""
        # Check if data already exists
        if self.diseases.count_documents({}) > 0:
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
                "common_symptoms": ["itching", "rash", "hair_loss", "red_skin"],
                "causes": ["food allergies", "environmental allergies", "parasites", "contact dermatitis"],
                "treatment": "Antihistamines, corticosteroids, topical treatments, allergen avoidance",
                "prevention": "Identify and avoid allergens, regular parasite control, omega-3 supplements",
                "severity": "mild",
                "affected_species": ["dog", "cat"]
            },
            {
                "name": "Pneumonia",
                "scientific_name": "Respiratory Infection",
                "description": "Infection of the lungs causing inflammation and fluid accumulation in the alveoli.",
                "common_symptoms": ["cough", "labored_breathing", "fever", "lethargy"],
                "causes": ["bacterial infection", "viral infection", "aspiration", "immunosuppression"],
                "treatment": "Antibiotics, supportive care, oxygen therapy if needed, rest",
                "prevention": "Vaccination, avoid smoke/pollutants, good ventilation",
                "severity": "severe",
                "affected_species": ["dog", "cat", "bird"]
            },
            {
                "name": "Conjunctivitis",
                "scientific_name": "Eye Inflammation",
                "description": "Inflammation of the conjunctiva (pink tissue around the eye) from infection or irritation.",
                "common_symptoms": ["discharge_eye", "redness_eye", "swelling_eye"],
                "causes": ["bacterial infection", "viral infection", "allergies", "foreign objects"],
                "treatment": "Topical antibiotics, saline drops, anti-inflammatory drops, treat underlying cause",
                "prevention": "Keep eyes clean, avoid irritants, treat respiratory infections",
                "severity": "mild",
                "affected_species": ["dog", "cat", "bird"]
            },
            {
                "name": "Diabetes Mellitus",
                "scientific_name": "Diabetes",
                "description": "Endocrine disorder characterized by insufficient insulin production or insulin resistance.",
                "common_symptoms": ["loss_of_appetite", "weight_loss", "lethargy", "dehydration"],
                "causes": ["obesity", "genetics", "pancreatitis", "autoimmune"],
                "treatment": "Insulin therapy, dietary management, weight control, monitoring",
                "prevention": "Maintain healthy weight, proper diet, regular exercise",
                "severity": "moderate",
                "affected_species": ["dog", "cat"]
            },
            {
                "name": "Epilepsy",
                "scientific_name": "Idiopathic Epilepsy",
                "description": "Neurological disorder causing recurrent seizures without identifiable structural brain disease.",
                "common_symptoms": ["seizure", "tremor", "incoordination"],
                "causes": ["genetic", "unknown"],
                "treatment": "Anti-seizure medications (phenobarbital, levetiracetam), seizure management",
                "prevention": "Medication management, stress reduction, regular monitoring",
                "severity": "moderate",
                "affected_species": ["dog", "cat"]
            }
        ]
        
        # Insert all diseases at once
        self.diseases.insert_many(diseases_data)
    
    def search_by_symptoms(self, symptoms: List[str]) -> List[Tuple[Disease, int]]:
        """
        Search diseases by symptoms
        
        Args:
            symptoms: List of symptom keys
            
        Returns:
            List of (Disease, symptom_match_count) tuples sorted by match count
        """
        cursor = self.diseases.find({"common_symptoms": {"$in": symptoms}})
        
        results = []
        for doc in cursor:
            match_count = sum(1 for s in symptoms if s in doc["common_symptoms"])
            results.append((self._doc_to_disease(doc), match_count))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def search_by_name(self, name: str) -> Optional[Disease]:
        """Search disease by name (case-insensitive)"""
        doc = self.diseases.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        return self._doc_to_disease(doc) if doc else None
    
    def search_by_keyword(self, keyword: str) -> List[Disease]:
        """Search diseases by keyword in name or description"""
        cursor = self.diseases.find({
            "$or": [
                {"name": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}}
            ]
        })
        return [self._doc_to_disease(d) for d in cursor]
    
    def get_treatments(self, disease_id: str) -> List[TreatmentOption]:
        """Get treatment options for a disease"""
        cursor = self.treatments.find({"disease_id": disease_id}).sort("effectiveness", -1)
        
        treatments = []
        for doc in cursor:
            treatments.append(TreatmentOption(
                id=str(doc["_id"]),
                disease_id=doc["disease_id"],
                name=doc["name"],
                description=doc["description"],
                medication=doc["medication"],
                dosage=doc["dosage"],
                duration=doc["duration"],
                effectiveness=doc["effectiveness"]
            ))
        
        return treatments
    
    def add_disease(self, disease: Disease) -> str:
        """Add a new disease to the database"""
        result = self.diseases.insert_one({
            "name": disease.name,
            "scientific_name": disease.scientific_name,
            "description": disease.description,
            "common_symptoms": disease.common_symptoms,
            "causes": disease.causes,
            "treatment": disease.treatment,
            "prevention": disease.prevention,
            "severity": disease.severity,
            "affected_species": disease.affected_species
        })
        return str(result.inserted_id)
    
    def add_treatment(self, disease_id: str, treatment: TreatmentOption) -> str:
        """Add a treatment option for a disease"""
        result = self.treatments.insert_one({
            "disease_id": disease_id,
            "name": treatment.name,
            "description": treatment.description,
            "medication": treatment.medication,
            "dosage": treatment.dosage,
            "duration": treatment.duration,
            "effectiveness": treatment.effectiveness
        })
        return str(result.inserted_id)
    
    def get_all_diseases(self) -> List[Disease]:
        """Get all diseases in database"""
        return [self._doc_to_disease(doc) for doc in self.diseases.find()]

    def list_diseases(self, limit: int = 50) -> List[Disease]:
        """List diseases (convenience helper)."""
        return [self._doc_to_disease(doc) for doc in self.diseases.find().limit(int(limit))]
    
    def _doc_to_disease(self, doc: Dict) -> Disease:
        """Convert MongoDB document to Disease object"""
        return Disease(
            id=str(doc["_id"]),
            name=doc["name"],
            scientific_name=doc.get("scientific_name", ""),
            description=doc["description"],
            common_symptoms=doc["common_symptoms"],
            causes=doc["causes"],
            treatment=doc["treatment"],
            prevention=doc["prevention"],
            severity=doc["severity"],
            affected_species=doc["affected_species"]
        )
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Example usage
    print("Connecting to MongoDB...")
    db = VeterinaryDatabase()
    
    # Search by symptoms
    print("\nSearching for diseases with 'cough' and 'fever'...")
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
    print("\nConnection closed.")

"""
Disease and Treatment Database
Provides storage and retrieval of veterinary disease information
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path


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
    Database for storing and retrieving veterinary information
    """
    
    def __init__(self, db_path: str = "veterinary_database.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create diseases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                scientific_name TEXT,
                description TEXT,
                common_symptoms TEXT,
                causes TEXT,
                treatment TEXT,
                prevention TEXT,
                severity TEXT,
                affected_species TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create treatments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                medication TEXT,
                dosage TEXT,
                duration TEXT,
                effectiveness REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (disease_id) REFERENCES diseases(id)
            )
        ''')
        
        # Create symptoms table for quick lookup
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_id INTEGER NOT NULL,
                symptom TEXT NOT NULL,
                FOREIGN KEY (disease_id) REFERENCES diseases(id)
            )
        ''')
        
        self.conn.commit()
        self._populate_default_data()
    
    def _populate_default_data(self):
        """Populate database with default veterinary information"""
        cursor = self.conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM diseases")
        if cursor.fetchone()[0] > 0:
            return
        
        diseases_data = [
            {
                "name": "Gastroenteritis",
                "scientific_name": "Gastritis and Enteritis",
                "description": "Inflammation of the stomach and intestines, commonly caused by dietary changes, infections, or ingestion of foreign objects.",
                "symptoms": ["vomiting", "diarrhea", "abdominal_pain", "loss_of_appetite"],
                "causes": ["dietary indiscretion", "bacterial infection", "viral infection", "parasites"],
                "treatment": "Dietary management, antibiotics if bacterial, supportive care with fluids",
                "prevention": "Consistent diet, avoid table scraps, regular deworming",
                "severity": "moderate",
                "species": ["dog", "cat", "rabbit"]
            },
            {
                "name": "Parvovirus",
                "scientific_name": "Canine Parvovirus (CPV)",
                "description": "Highly contagious viral infection affecting the gastrointestinal tract, bone marrow, and sometimes the heart.",
                "symptoms": ["vomiting", "diarrhea", "lethargy", "loss_of_appetite", "fever"],
                "causes": ["viral infection", "unvaccinated animals"],
                "treatment": "Supportive care, IV fluids, anti-emetics, antibiotics for secondary infections",
                "prevention": "Vaccination, good hygiene",
                "severity": "severe",
                "species": ["dog"]
            },
            {
                "name": "Otitis",
                "scientific_name": "Ear Inflammation",
                "description": "Infection or inflammation of the ear canal, commonly caused by bacteria, yeast, or mites.",
                "symptoms": ["itching", "discharge", "redness_eye"],
                "causes": ["ear mites", "bacterial infection", "yeast infection", "allergies"],
                "treatment": "Ear cleaning, topical antibiotics/antifungals, anti-inflammatory drops",
                "prevention": "Regular ear cleaning, treat underlying allergies, moisture control",
                "severity": "mild",
                "species": ["dog", "cat", "rabbit"]
            },
            {
                "name": "Dermatitis",
                "scientific_name": "Allergic Dermatitis",
                "description": "Skin inflammation caused by allergic reactions to food, environment, or parasites.",
                "symptoms": ["itching", "rash", "hair_loss", "red_skin"],
                "causes": ["food allergies", "environmental allergies", "parasites", "contact dermatitis"],
                "treatment": "Antihistamines, corticosteroids, topical treatments, allergen avoidance",
                "prevention": "Identify and avoid allergens, regular parasite control, omega-3 supplements",
                "severity": "mild",
                "species": ["dog", "cat"]
            },
            {
                "name": "Pneumonia",
                "scientific_name": "Respiratory Infection",
                "description": "Infection of the lungs causing inflammation and fluid accumulation in the alveoli.",
                "symptoms": ["cough", "labored_breathing", "fever", "lethargy"],
                "causes": ["bacterial infection", "viral infection", "aspiration", "immunosuppression"],
                "treatment": "Antibiotics, supportive care, oxygen therapy if needed, rest",
                "prevention": "Vaccination, avoid smoke/pollutants, good ventilation",
                "severity": "severe",
                "species": ["dog", "cat", "bird"]
            },
            {
                "name": "Conjunctivitis",
                "scientific_name": "Eye Inflammation",
                "description": "Inflammation of the conjunctiva (pink tissue around the eye) from infection or irritation.",
                "symptoms": ["discharge_eye", "redness_eye", "swelling_eye"],
                "causes": ["bacterial infection", "viral infection", "allergies", "foreign objects"],
                "treatment": "Topical antibiotics, saline drops, anti-inflammatory drops, treat underlying cause",
                "prevention": "Keep eyes clean, avoid irritants, treat respiratory infections",
                "severity": "mild",
                "species": ["dog", "cat", "bird"]
            },
            {
                "name": "Diabetes Mellitus",
                "scientific_name": "Diabetes",
                "description": "Endocrine disorder characterized by insufficient insulin production or insulin resistance.",
                "symptoms": ["loss_of_appetite", "weight_loss", "lethargy", "dehydration"],
                "causes": ["obesity", "genetics", "pancreatitis", "autoimmune"],
                "treatment": "Insulin therapy, dietary management, weight control, monitoring",
                "prevention": "Maintain healthy weight, proper diet, regular exercise",
                "severity": "moderate",
                "species": ["dog", "cat"]
            },
            {
                "name": "Epilepsy",
                "scientific_name": "Idiopathic Epilepsy",
                "description": "Neurological disorder causing recurrent seizures without identifiable structural brain disease.",
                "symptoms": ["seizure", "tremor", "incoordination"],
                "causes": ["genetic", "unknown"],
                "treatment": "Anti-seizure medications (phenobarbital, levetiracetam), seizure management",
                "prevention": "Medication management, stress reduction, regular monitoring",
                "severity": "moderate",
                "species": ["dog", "cat"]
            }
        ]
        
        for disease_data in diseases_data:
            cursor.execute('''
                INSERT INTO diseases 
                (name, scientific_name, description, common_symptoms, causes, treatment, prevention, severity, affected_species)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                disease_data["name"],
                disease_data["scientific_name"],
                disease_data["description"],
                json.dumps(disease_data["symptoms"]),
                json.dumps(disease_data["causes"]),
                disease_data["treatment"],
                disease_data["prevention"],
                disease_data["severity"],
                json.dumps(disease_data["species"])
            ))
            
            disease_id = cursor.lastrowid
            
            # Insert symptoms for quick lookup
            for symptom in disease_data["symptoms"]:
                cursor.execute('''
                    INSERT INTO symptoms (disease_id, symptom) VALUES (?, ?)
                ''', (disease_id, symptom))
        
        self.conn.commit()
    
    def search_by_symptoms(self, symptoms: List[str]) -> List[Tuple[Disease, int]]:
        """
        Search diseases by symptoms
        
        Args:
            symptoms: List of symptom keys
            
        Returns:
            List of (Disease, symptom_match_count) tuples
        """
        cursor = self.conn.cursor()
        diseases_matches = {}
        
        for symptom in symptoms:
            cursor.execute('''
                SELECT d.* FROM diseases d
                JOIN symptoms s ON d.id = s.disease_id
                WHERE s.symptom = ?
            ''', (symptom,))
            
            for row in cursor.fetchall():
                disease_id = row['id']
                if disease_id not in diseases_matches:
                    diseases_matches[disease_id] = (dict(row), 0)
                diseases_matches[disease_id] = (diseases_matches[disease_id][0], diseases_matches[disease_id][1] + 1)
        
        # Convert to Disease objects and sort by match count
        results = []
        for disease_id, (disease_dict, match_count) in diseases_matches.items():
            disease = self._dict_to_disease(disease_dict)
            results.append((disease, match_count))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def search_by_name(self, name: str) -> Optional[Disease]:
        """Search disease by name"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM diseases WHERE LOWER(name) = LOWER(?)', (name,))
        row = cursor.fetchone()
        
        if row:
            return self._dict_to_disease(dict(row))
        return None
    
    def search_by_keyword(self, keyword: str) -> List[Disease]:
        """Search diseases by keyword in name or description"""
        cursor = self.conn.cursor()
        search_term = f"%{keyword}%"
        cursor.execute('''
            SELECT * FROM diseases 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?)
        ''', (search_term, search_term))
        
        results = []
        for row in cursor.fetchall():
            results.append(self._dict_to_disease(dict(row)))
        
        return results
    
    def get_treatments(self, disease_id: int) -> List[TreatmentOption]:
        """Get treatment options for a disease"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM treatments WHERE disease_id = ?
            ORDER BY effectiveness DESC
        ''', (disease_id,))
        
        treatments = []
        for row in cursor.fetchall():
            treatments.append(TreatmentOption(
                id=row['id'],
                disease_id=row['disease_id'],
                name=row['name'],
                description=row['description'],
                medication=row['medication'],
                dosage=row['dosage'],
                duration=row['duration'],
                effectiveness=row['effectiveness']
            ))
        
        return treatments
    
    def add_disease(self, disease: Disease) -> int:
        """Add a new disease to the database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO diseases 
            (name, scientific_name, description, common_symptoms, causes, treatment, prevention, severity, affected_species)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            disease.name,
            disease.scientific_name,
            disease.description,
            json.dumps(disease.common_symptoms),
            json.dumps(disease.causes),
            disease.treatment,
            disease.prevention,
            disease.severity,
            json.dumps(disease.affected_species)
        ))
        
        disease_id = cursor.lastrowid
        
        # Add symptoms
        for symptom in disease.common_symptoms:
            cursor.execute('''
                INSERT INTO symptoms (disease_id, symptom) VALUES (?, ?)
            ''', (disease_id, symptom))
        
        self.conn.commit()
        return disease_id
    
    def add_treatment(self, disease_id: int, treatment: TreatmentOption) -> int:
        """Add a treatment option for a disease"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO treatments 
            (disease_id, name, description, medication, dosage, duration, effectiveness)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            disease_id,
            treatment.name,
            treatment.description,
            treatment.medication,
            treatment.dosage,
            treatment.duration,
            treatment.effectiveness
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_diseases(self) -> List[Disease]:
        """Get all diseases in database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM diseases')
        
        diseases = []
        for row in cursor.fetchall():
            diseases.append(self._dict_to_disease(dict(row)))
        
        return diseases
    
    @staticmethod
    def _dict_to_disease(row_dict: Dict) -> Disease:
        """Convert database row to Disease object"""
        return Disease(
            id=row_dict['id'],
            name=row_dict['name'],
            scientific_name=row_dict['scientific_name'],
            description=row_dict['description'],
            common_symptoms=json.loads(row_dict['common_symptoms']),
            causes=json.loads(row_dict['causes']),
            treatment=row_dict['treatment'],
            prevention=row_dict['prevention'],
            severity=row_dict['severity'],
            affected_species=json.loads(row_dict['affected_species'])
        )
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


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

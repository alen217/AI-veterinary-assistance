"""
Extract Real Diseases from MongoDB for AI Training
Creates training dataset using actual diseases from the database
"""
import json
from mongo_disease_repository import MongoDiseaseRepository
from typing import List, Dict
import random


class RealDiseaseDatasetGenerator:
    """Generate training data using real diseases from MongoDB"""
    
    def __init__(self):
        self.repo = MongoDiseaseRepository()
        self.diseases = []
        self.load_diseases()
        
    def load_diseases(self):
        """Load all diseases from MongoDB"""
        print("📦 Loading diseases from MongoDB...")
        cursor = self.repo.collection.find({})
        self.diseases = list(cursor)
        print(f"✅ Loaded {len(self.diseases)} diseases from database")
        
    def generate_training_examples(self, num_examples: int = 5000) -> List[Dict]:
        """Generate training examples using real disease data"""
        if not self.diseases:
            raise RuntimeError("No diseases found in database")
        
        examples = []
        animals = ["dog", "cat", "rabbit", "bird", "horse"]
        
        for _ in range(num_examples):
            # Pick random disease
            disease = random.choice(self.diseases)
            
            # Pick random animal (weighted by affected_species if available)
            affected_species = disease.get("affected_species", animals)
            if affected_species:
                animal = random.choice(affected_species)
            else:
                animal = random.choice(animals)
            
            # Get disease symptoms
            disease_symptoms = disease.get("common_symptoms", [])
            if not disease_symptoms:
                continue
            
            # Randomly select 1-3 symptoms that patient has
            num_present_symptoms = random.randint(1, min(3, len(disease_symptoms)))
            present_symptoms = random.sample(disease_symptoms, num_present_symptoms)
            
            # Build patient context
            context = {
                "patient": {
                    "animal_type": animal,
                    "age": f"{random.randint(1, 15)} years",
                    "weight": f"{random.randint(5, 100)} lbs"
                },
                "symptoms": [],
                "suspected_disease": disease.get("name", ""),
                "disease_symptoms": disease_symptoms
            }
            
            # Add symptoms with varying completeness
            for symptom in present_symptoms:
                symptom_data = {
                    "name": symptom,
                    "duration": random.choice([None, "2 days", "1 week", "3 days", "24 hours", "5 days"]),
                    "severity": random.choice([None, "mild", "moderate", "severe"]),
                    "frequency": random.choice([None, "constant", "intermittent", "occasional", "daily"])
                }
                context["symptoms"].append(symptom_data)
            
            # Generate follow-up questions for this disease
            questions = self._generate_disease_specific_questions(
                context, disease, animal
            )
            
            if questions:
                examples.append({
                    "context": context,
                    "questions": questions
                })
        
        return examples
    
    def _generate_disease_specific_questions(
        self, 
        context: Dict, 
        disease: Dict,
        animal: str
    ) -> List[Dict]:
        """Generate questions specific to the disease"""
        questions = []
        present_symptom_names = {s["name"] for s in context["symptoms"]}
        disease_symptoms = set(disease.get("common_symptoms", []))
        
        # Ask about missing critical info first
        for symptom_data in context["symptoms"]:
            symptom_name = symptom_data["name"].replace("_", " ")
            
            if not symptom_data.get("duration"):
                questions.append({
                    "question": f"How long has your {animal} had {symptom_name}?",
                    "category": "symptom_details",
                    "priority": 5,
                    "reasoning": f"Duration of {symptom_name} is critical for diagnosing {disease.get('name')}",
                    "expected_answer": "duration",
                    "updates_confidence": True,
                    "related_disease": disease.get("name")
                })
            
            if not symptom_data.get("severity"):
                questions.append({
                    "question": f"How severe is the {symptom_name}?",
                    "category": "symptom_details",
                    "priority": 4,
                    "reasoning": "Severity helps distinguish between conditions",
                    "expected_answer": "severity",
                    "updates_confidence": True,
                    "related_disease": disease.get("name")
                })
        
        # Ask about missing disease symptoms (disease confirmation)
        missing_symptoms = disease_symptoms - present_symptom_names
        if missing_symptoms:
            for missing in list(missing_symptoms)[:2]:  # Ask about top 2 missing
                missing_display = missing.replace("_", " ")
                questions.append({
                    "question": f"Has your {animal} shown any {missing_display}?",
                    "category": "disease_confirmation",
                    "priority": 4,
                    "reasoning": f"Presence of {missing_display} would strongly indicate {disease.get('name')}",
                    "expected_answer": "yes/no",
                    "updates_confidence": True,
                    "related_disease": disease.get("name"),
                    "symptom_to_check": missing
                })
        
        # Ask about causes if available
        causes = disease.get("causes", [])
        if causes:
            cause = random.choice(causes)
            cause_display = cause.replace("_", " ")
            questions.append({
                "question": f"Has your {animal} been exposed to {cause_display}?",
                "category": "risk_factors",
                "priority": 3,
                "reasoning": f"Exposure to {cause_display} is a known risk factor for {disease.get('name')}",
                "expected_answer": "yes/no",
                "updates_confidence": True,
                "related_disease": disease.get("name")
            })
        
        # Ask about treatment history
        questions.append({
            "question": f"Has your {animal} been treated for this before?",
            "category": "medical_history",
            "priority": 3,
            "reasoning": "Previous treatment history helps assess if this is recurring or new",
            "expected_answer": "yes/no",
            "updates_confidence": False,
            "related_disease": disease.get("name")
        })
        
        # Shuffle and return
        random.shuffle(questions)
        return questions[:6]
    
    def save_dataset(self, filepath: str, num_examples: int = 5000):
        """Generate and save dataset"""
        print(f"🔄 Generating {num_examples} training examples from real diseases...")
        examples = self.generate_training_examples(num_examples)
        
        if not examples:
            print("❌ No examples generated. Check your database has diseases.")
            return
        
        # Split into train/val/test
        random.shuffle(examples)
        train_size = int(0.8 * len(examples))
        val_size = int(0.1 * len(examples))
        
        dataset = {
            "train": examples[:train_size],
            "validation": examples[train_size:train_size+val_size],
            "test": examples[train_size+val_size:],
            "metadata": {
                "total_examples": len(examples),
                "num_diseases": len(self.diseases),
                "diseases": [d.get("name") for d in self.diseases[:20]]  # First 20
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"✅ Dataset saved to {filepath}")
        print(f"   Train: {len(dataset['train'])} examples")
        print(f"   Validation: {len(dataset['validation'])} examples")
        print(f"   Test: {len(dataset['test'])} examples")
        print(f"   Based on {len(self.diseases)} real diseases from database")


if __name__ == "__main__":
    try:
        generator = RealDiseaseDatasetGenerator()
        generator.save_dataset(
            "ml_training/vet_followup_qa/vet_followup_dataset_real.json",
            num_examples=5000
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. MongoDB is connected (check MONGO_URL in .env)")
        print("2. Database has disease data")

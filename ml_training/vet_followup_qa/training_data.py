"""
Generate Training Dataset for Veterinary Follow-up Question AI
Creates synthetic training data for the custom follow-up question generation model
"""
import json
import random
from typing import List, Dict

class VetFollowUpDatasetGenerator:
    """Generate training data for veterinary follow-up question AI"""
    
    def __init__(self):
        self.animals = ["dog", "cat", "rabbit", "hamster", "bird", "horse", "ferret"]
        self.breeds = {
            "dog": ["Labrador", "German Shepherd", "Beagle", "Bulldog", "Poodle", "Golden Retriever"],
            "cat": ["Persian", "Siamese", "Maine Coon", "British Shorthair", "Bengal"],
            "rabbit": ["Dutch", "Flemish Giant", "Lionhead", "Mini Lop"],
        }
        
        # Symptom patterns with typical follow-up questions
        self.symptom_patterns = {
            "vomiting": {
                "critical_questions": [
                    "How many times has your {animal} vomited in the last 24 hours?",
                    "What does the vomit look like (color, consistency)?",
                    "Is there blood in the vomit?",
                    "When did your {animal} last eat or drink?",
                ],
                "secondary_questions": [
                    "Is your {animal} able to keep water down?",
                    "Has there been any recent dietary change?",
                    "Is your {animal} experiencing diarrhea as well?",
                ],
                "priority_order": ["duration", "frequency", "appearance", "hydration", "diet"]
            },
            "diarrhea": {
                "critical_questions": [
                    "How long has your {animal} had diarrhea?",
                    "What color is the diarrhea?",
                    "Is there blood or mucus in the stool?",
                    "How many times has your {animal} had diarrhea today?",
                ],
                "secondary_questions": [
                    "Is your {animal} still eating normally?",
                    "Has your {animal} had access to any unusual foods or objects?",
                    "Is your {animal} drinking more or less water than usual?",
                ],
                "priority_order": ["duration", "appearance", "frequency", "diet", "hydration"]
            },
            "lethargy": {
                "critical_questions": [
                    "How long has your {animal} been lethargic?",
                    "Is your {animal} eating and drinking normally?",
                    "Has there been any fever or temperature change?",
                    "Can your {animal} still walk and move normally?",
                ],
                "secondary_questions": [
                    "Has your {animal}'s sleep pattern changed?",
                    "Is your {animal} responsive to stimulation?",
                    "Have you noticed any other symptoms?",
                ],
                "priority_order": ["duration", "appetite", "mobility", "fever", "progression"]
            },
            "coughing": {
                "critical_questions": [
                    "How long has your {animal} been coughing?",
                    "Is the cough dry or producing mucus?",
                    "How often does your {animal} cough (constant, intermittent)?",
                    "Is your {animal} having difficulty breathing?",
                ],
                "secondary_questions": [
                    "Does the cough worsen at certain times of day?",
                    "Has your {animal} been exposed to smoke or irritants?",
                    "Is there any nasal discharge?",
                ],
                "priority_order": ["duration", "type", "frequency", "breathing", "discharge"]
            },
            "skin_lesion": {
                "critical_questions": [
                    "When did you first notice the skin lesion?",
                    "Is the lesion spreading or growing?",
                    "Is your {animal} scratching or licking the area?",
                    "What does the lesion look like (red, crusty, oozing)?",
                ],
                "secondary_questions": [
                    "Are there multiple lesions or just one?",
                    "Has your {animal} been exposed to other animals with skin issues?",
                    "Is there hair loss around the lesion?",
                ],
                "priority_order": ["onset", "progression", "appearance", "behavior", "spread"]
            },
            "limping": {
                "critical_questions": [
                    "Which leg is your {animal} limping on?",
                    "When did the limping start?",
                    "Was there any injury or trauma?",
                    "Can your {animal} still bear weight on the leg?",
                ],
                "secondary_questions": [
                    "Is the limping constant or intermittent?",
                    "Is there any swelling or heat in the affected leg?",
                    "Does your {animal} cry out when touching the leg?",
                ],
                "priority_order": ["location", "onset", "trauma", "weight_bearing", "pain"]
            },
            "seizure": {
                "critical_questions": [
                    "How long did the seizure last?",
                    "Has your {animal} had seizures before?",
                    "What did the seizure look like (full body convulsions, partial)?",
                    "How many seizures has your {animal} had in the last 24 hours?",
                ],
                "secondary_questions": [
                    "Was your {animal} unconscious during the seizure?",
                    "Has your {animal} been exposed to any toxins?",
                    "Is your {animal} on any medications?",
                ],
                "priority_order": ["duration", "history", "type", "frequency", "consciousness"]
            },
            "loss_of_appetite": {
                "critical_questions": [
                    "How long has your {animal} not been eating?",
                    "Is your {animal} drinking water?",
                    "Has your {animal} refused all food or just certain foods?",
                    "Are there any other symptoms present?",
                ],
                "secondary_questions": [
                    "Has there been any recent stress or environmental change?",
                    "Is your {animal} losing weight?",
                    "Does your {animal} seem interested in food but unable to eat?",
                ],
                "priority_order": ["duration", "hydration", "selectivity", "weight", "comorbidities"]
            },
        }
        
        # Disease-specific question patterns
        self.disease_patterns = {
            "parvovirus": {
                "confirmation_questions": [
                    "Is your {animal} a puppy or young dog?",
                    "Is your {animal} up to date on vaccinations?",
                    "Has your {animal} been exposed to other dogs recently?",
                    "Is there bloody diarrhea?",
                ],
                "priority": 5
            },
            "diabetes": {
                "confirmation_questions": [
                    "Has your {animal} been drinking more water than usual?",
                    "Has your {animal} been urinating more frequently?",
                    "Has there been any weight loss despite normal eating?",
                    "Does your {animal} seem more tired than usual?",
                ],
                "priority": 4
            },
            "kennel_cough": {
                "confirmation_questions": [
                    "Has your {animal} been in a kennel or daycare recently?",
                    "Does the cough sound like a goose honk?",
                    "Is your {animal} otherwise acting normally?",
                    "Has your {animal} been exposed to other dogs?",
                ],
                "priority": 3
            },
            "arthritis": {
                "confirmation_questions": [
                    "Is your {animal} a senior pet?",
                    "Is the stiffness worse in the morning or after rest?",
                    "Does exercise make the symptoms better or worse?",
                    "Have you noticed any joint swelling?",
                ],
                "priority": 4
            },
            "pancreatitis": {
                "confirmation_questions": [
                    "Did your {animal} recently eat fatty or rich food?",
                    "Is there abdominal pain or sensitivity?",
                    "Is your {animal} in a hunched position?",
                    "Has there been both vomiting and diarrhea?",
                ],
                "priority": 5
            },
        }
        
    def generate_training_examples(self, num_examples: int = 5000) -> List[Dict]:
        """Generate training examples for the model"""
        examples = []
        
        for _ in range(num_examples):
            example = self._generate_single_example()
            examples.append(example)
        
        return examples
    
    def _generate_single_example(self) -> Dict:
        """Generate a single training example"""
        # Random patient
        animal = random.choice(self.animals)
        age = f"{random.randint(1, 15)} years old"
        weight = f"{random.randint(5, 100)} lbs"
        
        # Random symptoms (1-3)
        num_symptoms = random.randint(1, 3)
        symptoms = random.sample(list(self.symptom_patterns.keys()), min(num_symptoms, len(self.symptom_patterns)))
        
        # Build context
        context = {
            "patient": {
                "animal_type": animal,
                "age": age,
                "weight": weight
            },
            "symptoms": []
        }
        
        # Add symptoms with varying completeness
        for symptom in symptoms:
            symptom_data = {
                "name": symptom,
                "duration": random.choice([None, "2 days", "1 week", "3 days", "24 hours"]),
                "severity": random.choice([None, "mild", "moderate", "severe"]),
                "frequency": random.choice([None, "constant", "intermittent", "occasional"])
            }
            context["symptoms"].append(symptom_data)
        
        # Generate appropriate follow-up questions
        questions = self._generate_questions_for_context(context)
        
        return {
            "context": context,
            "questions": questions
        }
    
    def _generate_questions_for_context(self, context: Dict) -> List[Dict]:
        """Generate appropriate follow-up questions based on context"""
        questions = []
        animal = context["patient"]["animal_type"]
        
        for symptom in context["symptoms"]:
            symptom_name = symptom["name"]
            if symptom_name not in self.symptom_patterns:
                continue
            
            pattern = self.symptom_patterns[symptom_name]
            
            # Ask about missing critical information
            if not symptom.get("duration"):
                q = random.choice(pattern["critical_questions"][:2])
                questions.append({
                    "question": q.format(animal=animal),
                    "category": "symptom_details",
                    "priority": 5,
                    "reasoning": f"Duration of {symptom_name} is critical for diagnosis"
                })
            
            if not symptom.get("severity"):
                questions.append({
                    "question": f"How severe is the {symptom_name.replace('_', ' ')}?",
                    "category": "symptom_details",
                    "priority": 4,
                    "reasoning": "Severity assessment is needed for urgency determination"
                })
            
            # Add contextual questions
            if len(questions) < 5:
                secondary = random.sample(pattern["secondary_questions"], 
                                        min(2, len(pattern["secondary_questions"])))
                for q in secondary:
                    questions.append({
                        "question": q.format(animal=animal),
                        "category": "disease_confirmation",
                        "priority": 3,
                        "reasoning": f"Helps narrow differential diagnosis for {symptom_name}"
                    })
        
        # Shuffle and limit
        random.shuffle(questions)
        return questions[:6]
    
    def save_dataset(self, filepath: str, num_examples: int = 5000):
        """Generate and save dataset to file"""
        print(f"🔄 Generating {num_examples} training examples...")
        examples = self.generate_training_examples(num_examples)
        
        # Split into train/val/test
        random.shuffle(examples)
        train_size = int(0.8 * len(examples))
        val_size = int(0.1 * len(examples))
        
        dataset = {
            "train": examples[:train_size],
            "validation": examples[train_size:train_size+val_size],
            "test": examples[train_size+val_size:]
        }
        
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"✅ Dataset saved to {filepath}")
        print(f"   Train: {len(dataset['train'])} examples")
        print(f"   Validation: {len(dataset['validation'])} examples")
        print(f"   Test: {len(dataset['test'])} examples")


if __name__ == "__main__":
    generator = VetFollowUpDatasetGenerator()
    generator.save_dataset("vet_followup_dataset.json", num_examples=5000)

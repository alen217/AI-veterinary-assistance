"""
Custom AI Follow-Up Question Generator (Replaces Groq)
Uses the locally trained veterinary model instead of external API
"""
import os
import torch
from typing import List, Dict, Optional
from dataclasses import dataclass
import sys

# Add ml_training path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml_training', 'vet_followup_qa'))

try:
    import model
    from model import VetFollowUpQuestionModel, VetQuestionVocabulary
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("⚠️  Custom AI model not found. Run training first.")


@dataclass
class AIFollowUpQuestion:
    """AI-generated follow-up question with context"""
    question: str
    category: str
    priority: int  # 1-5, higher = more important
    reasoning: str
    expected_answer_type: str


class CustomAIFollowUpGenerator:
    """
    Custom AI-powered follow-up question generator using trained model
    NO EXTERNAL APIs - completely local and free
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize custom AI generator
        
        Args:
            model_path: Path to trained model file (default: auto-detect)
        """
        if not MODEL_AVAILABLE:
            raise RuntimeError(
                "Custom AI model not available. Please train the model first:\n"
                "cd ml_training/vet_followup_qa && python train.py"
            )
        
        # Auto-detect model path
        if model_path is None:
            possible_paths = [
                "ml_training/vet_followup_qa/vet_followup_model.pth",
                "vet_followup_model.pth",
                os.path.join(os.path.dirname(__file__), "ml_training", "vet_followup_qa", "vet_followup_model.pth")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
        
        if model_path is None or not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Trained model not found. Please train the model first:\n"
                f"cd ml_training/vet_followup_qa && python train.py\n"
                f"Expected location: ml_training/vet_followup_qa/vet_followup_model.pth"
            )
        
        # Load model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        
        self.vocab = checkpoint['vocabulary']
        vocab_size = self.vocab.n_words
        
        self.model = VetFollowUpQuestionModel(
            vocab_size=vocab_size,
            embed_dim=checkpoint['embed_dim'],
            hidden_dim=checkpoint['hidden_dim']
        ).to(self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        print(f"✅ Custom AI model loaded from: {model_path}")
        print(f"   Device: {self.device}")
        print(f"   Vocabulary: {vocab_size} words")
    
    def generate_questions(
        self,
        patient_info: Dict,
        symptoms: List[Dict],
        suspected_diseases: List[Dict],
        database_matches: List[Dict],
        max_questions: int = 5,
        previous_answers: Optional[Dict] = None
    ) -> List[AIFollowUpQuestion]:
        """
        Generate AI-powered follow-up questions using custom trained model
        
        Args:
            patient_info: Patient demographic information
            symptoms: Extracted symptoms with details
            suspected_diseases: NLP-extracted disease suspicions
            database_matches: MongoDB disease matches with confidence scores
            max_questions: Maximum number of questions to generate
            previous_answers: Dictionary of previously asked questions and answers (not used yet)
            
        Returns:
            List of AI-generated follow-up questions with priorities
        """
        
        try:
            # Build context from patient info and symptoms
            context_parts = []
            
            # Add patient info
            if patient_info:
                age = patient_info.get('age', 'unknown age')
                species = patient_info.get('species', 'animal')
                context_parts.append(f"{species} {age} years old")
            
            # Add symptoms
            symptom_strs = []
            for symptom in symptoms[:3]:  # Top 3 symptoms
                if isinstance(symptom, dict):
                    symptom_strs.append(symptom.get('symptom', str(symptom)))
                else:
                    symptom_strs.append(str(symptom))
            
            if symptom_strs:
                context_parts.append(f"has {', '.join(symptom_strs)}")
            
            context_text = " ".join(context_parts)
            
            # Generate questions using model inference
            generated_questions = self._generate_with_model(
                context_text, 
                max_questions
            )
            
            # Convert to AIFollowUpQuestion objects
            ai_questions = []
            for i, question_text in enumerate(generated_questions):
                ai_questions.append(AIFollowUpQuestion(
                    question=question_text,
                    category='symptom_details',
                    priority=max_questions - i,  # Higher priority for earlier questions
                    reasoning='Generated by AI based on patient context',
                    expected_answer_type='descriptive'
                ))
            
            return ai_questions[:max_questions]
            
            # Post-process: add critical missing info questions if needed
            ai_questions = self._add_critical_questions(ai_questions, symptoms, patient_info)
            
            # Sort by priority
            ai_questions.sort(key=lambda x: x.priority, reverse=True)
            
            return ai_questions[:max_questions]
            
        except Exception as e:
            print(f"⚠️  Custom AI generation error: {e}")
            return self._generate_fallback_questions(patient_info, symptoms, max_questions)
    
    def _generate_with_model(self, context_text: str, num_questions: int = 5) -> List[str]:
        """
        Generate questions using the trained neural network model
        
        Args:
            context_text: Patient context (e.g., "dog 5 years old has vomiting diarrhea")
            num_questions: Number of questions to generate
            
        Returns:
            List of generated question strings
        """
        generated_questions = []
        
        with torch.no_grad():
            # Convert context to indices
            context_indices = self.vocab.sentence_to_indices(context_text, max_length=50)
            context_tensor = torch.tensor([context_indices], dtype=torch.long).to(self.device)
            
            # Generate multiple questions with slight variations
            for i in range(num_questions):
                # Vary temperature for diversity
                temp = 0.9 + (i * 0.05)  # 0.9, 0.95, 1.0, etc.
                
                # Use model's generate_question method (singular, not plural)
                question_text = self.model.generate_question(
                    context_tensor,
                    self.vocab,
                    max_length=30,
                    temperature=temp
                )
                
                # Clean up the question
                question_text = question_text.strip()
                if question_text and not question_text.endswith('?'):
                    question_text += '?'
                
                if question_text and question_text not in generated_questions:
                    generated_questions.append(question_text)
        
        return generated_questions
    
    def _calculate_priority(self, question: str, symptoms: List[Dict], 
                          database_matches: List[Dict]) -> int:
        """Calculate question priority based on content"""
        question_lower = question.lower()
        
        # Critical keywords (priority 5)
        critical_words = ['how long', 'duration', 'blood', 'breathing', 'seizure', 'unconscious']
        if any(word in question_lower for word in critical_words):
            return 5
        
        # High priority keywords (priority 4)
        high_priority_words = ['severe', 'frequency', 'eating', 'drinking', 'vomit', 'pain']
        if any(word in question_lower for word in high_priority_words):
            return 4
        
        # Check if related to high-confidence disease
        if database_matches and database_matches[0].get('confidence', 0) > 0.7:
            disease_name = database_matches[0].get('name', '').lower()
            if disease_name and any(word in question_lower for word in disease_name.split()):
                return 4
        
        # Default moderate priority
        return 3
    
    def _add_critical_questions(self, questions: List[AIFollowUpQuestion], 
                               symptoms: List[Dict], patient_info: Dict) -> List[AIFollowUpQuestion]:
        """Add critical missing information questions if model missed them"""
        
        animal = patient_info.get('animal_type', 'pet')
        
        # Check for missing duration/severity
        for symptom in symptoms:
            symptom_name = symptom.get('name', symptom.get('symptom', '')).replace('_', ' ')
            
            if not symptom.get('duration'):
                duration_q = f"How long has your {animal} had {symptom_name}?"
                if not any(q.question == duration_q for q in questions):
                    questions.insert(0, AIFollowUpQuestion(
                        question=duration_q,
                        category='symptom_details',
                        priority=5,
                        reasoning='Duration is critical for diagnosis',
                        expected_answer_type='duration'
                    ))
            
            if not symptom.get('severity'):
                severity_q = f"How severe is the {symptom_name}?"
                if not any(q.question == severity_q for q in questions):
                    questions.insert(1, AIFollowUpQuestion(
                        question=severity_q,
                        category='symptom_details',
                        priority=4,
                        reasoning='Severity helps assess urgency',
                        expected_answer_type='severity'
                    ))
        
        return questions
    
    def _generate_fallback_questions(
        self,
        patient_info: Dict,
        symptoms: List[Dict],
        max_questions: int
    ) -> List[AIFollowUpQuestion]:
        """Generate basic fallback questions if AI fails"""
        
        animal = patient_info.get('animal_type', 'pet')
        questions = []
        
        if symptoms:
            symptom = symptoms[0]
            symptom_name = symptom.get('name', symptom.get('symptom', 'symptoms')).replace('_', ' ')
            
            if not symptom.get('duration'):
                questions.append(AIFollowUpQuestion(
                    question=f"How long has your {animal} had {symptom_name}?",
                    category="symptom_details",
                    priority=5,
                    reasoning="Duration is critical for diagnosis",
                    expected_answer_type="duration"
                ))
            
            if not symptom.get('severity'):
                questions.append(AIFollowUpQuestion(
                    question=f"How severe is the {symptom_name}?",
                    category="symptom_details",
                    priority=4,
                    reasoning="Severity helps assess urgency",
                    expected_answer_type="severity"
                ))
        
        # General questions
        questions.extend([
            AIFollowUpQuestion(
                question=f"Is your {animal} eating and drinking normally?",
                category="additional_symptoms",
                priority=4,
                reasoning="Appetite changes indicate systemic illness",
                expected_answer_type="yes/no"
            ),
            AIFollowUpQuestion(
                question=f"Are there any other symptoms you've noticed?",
                category="additional_symptoms",
                priority=3,
                reasoning="Additional symptoms help narrow diagnosis",
                expected_answer_type="descriptive"
            ),
            AIFollowUpQuestion(
                question=f"Is your {animal} on any medications?",
                category="medical_history",
                priority=3,
                reasoning="Medications can affect symptoms and treatment",
                expected_answer_type="descriptive"
            )
        ])
        
        return questions[:max_questions]
    
    def format_questions_for_display(self, questions: List[AIFollowUpQuestion]) -> str:
        """Format AI-generated questions for user-friendly display"""
        
        output = []
        output.append("\n" + "="*70)
        output.append("🤖 CUSTOM AI-GENERATED FOLLOW-UP QUESTIONS")
        output.append("="*70 + "\n")
        
        current_category = None
        question_num = 1
        
        for question in questions:
            if question.category != current_category:
                current_category = question.category
                category_display = question.category.replace("_", " ").title()
                output.append(f"\n📋 [{category_display}]")
            
            # Priority indicator
            if question.priority >= 5:
                priority_str = "⚠️  CRITICAL"
            elif question.priority >= 4:
                priority_str = "⭐ HIGH"
            elif question.priority >= 3:
                priority_str = "○ MODERATE"
            else:
                priority_str = "· LOW"
            
            output.append(f"  {question_num}. {question.question}")
            output.append(f"     {priority_str} | {question.reasoning}\n")
            question_num += 1
        
        output.append("="*70)
        return "\n".join(output)


# Test/example usage
if __name__ == "__main__":
    print("🧪 Testing Custom AI Follow-Up Question Generator\n")
    
    try:
        generator = CustomAIFollowUpGenerator()
        
        # Test data
        patient_info = {
            "animal_type": "dog",
            "age": "5 years",
            "weight": "70 lbs"
        }
        
        symptoms = [
            {
                "symptom": "vomiting",
                "duration": "2 days",
                "severity": "moderate",
                "frequency": None
            },
            {
                "symptom": "lethargy",
                "duration": None,
                "severity": None,
                "frequency": None
            }
        ]
        
        database_matches = [
            {
                "name": "Gastroenteritis",
                "confidence": 0.78
            }
        ]
        
        questions = generator.generate_questions(
            patient_info=patient_info,
            symptoms=symptoms,
            suspected_diseases=[],
            database_matches=database_matches,
            max_questions=5
        )
        
        print(generator.format_questions_for_display(questions))
        print(f"\n✅ Generated {len(questions)} questions successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTo fix this:")
        print("1. cd ml_training/vet_followup_qa")
        print("2. python train.py")
        print("3. Wait for training to complete")
        print("4. Run this test again")

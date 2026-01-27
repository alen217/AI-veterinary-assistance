"""
Follow-up Question Generator
Generates contextual follow-up questions based on patient analysis and database search results
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from nlp_patient_analyzer import PatientInfo, SymptomExtraction, DiseaseExtraction
from veterinary_database import Disease, VeterinaryDatabase


@dataclass
class FollowUpQuestion:
    """Structured follow-up question"""
    category: str  # symptom_details, disease_confirmation, treatment_history, lifestyle, etc.
    question: str
    priority: int  # 1-5, higher = more important
    reason: str  # Why this question is being asked


class FollowUpQuestionGenerator:
    """
    Generates contextual follow-up questions based on patient analysis
    """
    
    def __init__(self, db: Optional[VeterinaryDatabase] = None):
        """Initialize generator with optional database"""
        self.db = db
        self.question_templates = self._load_question_templates()
    
    @staticmethod
    def _load_question_templates() -> Dict[str, List[Dict]]:
        """Load question templates organized by category"""
        return {
            "symptom_details": [
                {
                    "template": "How long has your {animal} had {symptom}?",
                    "keywords": ["symptom"],
                    "priority": 4
                },
                {
                    "template": "Is the {symptom} getting worse, staying the same, or improving?",
                    "keywords": ["symptom"],
                    "priority": 3
                },
                {
                    "template": "Have you noticed any patterns to when the {symptom} occurs (time of day, after eating, etc.)?",
                    "keywords": ["symptom"],
                    "priority": 2
                },
                {
                    "template": "Is your {animal} in pain or experiencing discomfort with the {symptom}?",
                    "keywords": ["symptom"],
                    "priority": 3
                }
            ],
            "additional_symptoms": [
                {
                    "template": "Have you noticed any changes in your {animal}'s appetite or drinking habits?",
                    "keywords": [],
                    "priority": 4
                },
                {
                    "template": "Is your {animal} experiencing any eye or ear discharge or irritation?",
                    "keywords": [],
                    "priority": 3
                },
                {
                    "template": "Have you noticed any changes in weight, energy level, or activity?",
                    "keywords": [],
                    "priority": 3
                },
                {
                    "template": "Is your {animal} scratching, licking, or showing skin issues anywhere?",
                    "keywords": [],
                    "priority": 2
                }
            ],
            "disease_confirmation": [
                {
                    "template": "Has your {animal} been exposed to other sick animals recently?",
                    "keywords": ["infectious"],
                    "priority": 4
                },
                {
                    "template": "Is your {animal} up to date on vaccinations?",
                    "keywords": ["viral", "infectious"],
                    "priority": 4
                },
                {
                    "template": "When was your {animal}'s last veterinary checkup?",
                    "keywords": [],
                    "priority": 3
                },
                {
                    "template": "Has your {animal} had this condition before?",
                    "keywords": [],
                    "priority": 2
                }
            ],
            "medical_history": [
                {
                    "template": "Does your {animal} have any known allergies or sensitivities?",
                    "keywords": [],
                    "priority": 4
                },
                {
                    "template": "Is your {animal} on any current medications or supplements?",
                    "keywords": [],
                    "priority": 4
                },
                {
                    "template": "Has your {animal} had any surgeries or significant injuries?",
                    "keywords": [],
                    "priority": 2
                }
            ],
            "lifestyle": [
                {
                    "template": "What type of food and diet is your {animal} on?",
                    "keywords": ["diarrhea", "vomiting", "loss_of_appetite"],
                    "priority": 4
                },
                {
                    "template": "How much exercise and activity does your {animal} get daily?",
                    "keywords": [],
                    "priority": 2
                },
                {
                    "template": "Has there been any recent change in diet, environment, or routine?",
                    "keywords": ["vomiting", "diarrhea"],
                    "priority": 3
                },
                {
                    "template": "Does your {animal} have access to outdoor areas or other animals?",
                    "keywords": [],
                    "priority": 2
                }
            ],
            "treatment_history": [
                {
                    "template": "Has your {animal} been treated for this issue before? If yes, what was the treatment?",
                    "keywords": [],
                    "priority": 3
                },
                {
                    "template": "Are you currently giving any home remedies or over-the-counter treatments?",
                    "keywords": [],
                    "priority": 3
                }
            ],
            "symptom_severity": [
                {
                    "template": "Is your {animal} able to eat and drink normally despite the {symptom}?",
                    "keywords": ["symptom"],
                    "priority": 4
                },
                {
                    "template": "Has this condition affected your {animal}'s daily activities or sleep?",
                    "keywords": ["symptom"],
                    "priority": 3
                },
                {
                    "template": "Are there any other symptoms you've noticed that seem unusual?",
                    "keywords": [],
                    "priority": 2
                }
            ]
        }
    
    def generate_questions(
        self,
        patient_info: PatientInfo,
        symptoms: List[SymptomExtraction],
        diseases: List[DiseaseExtraction],
        max_questions: int = 8
    ) -> List[FollowUpQuestion]:
        """
        Generate contextual follow-up questions
        
        Args:
            patient_info: Patient demographic information
            symptoms: Extracted symptoms
            diseases: Suspected diseases
            max_questions: Maximum number of questions to generate
            
        Returns:
            List of prioritized follow-up questions
        """
        questions = []
        animal = patient_info.animal_type or "pet"
        
        # Generate symptom detail questions
        for symptom in symptoms:
            questions.extend(self._generate_symptom_questions(symptom, animal))
        
        # Generate disease-specific questions
        for disease in diseases[:3]:  # Top 3 suspected diseases
            questions.extend(self._generate_disease_questions(disease, animal))
        
        # Generate general medical history questions
        questions.extend(self._generate_medical_history_questions(animal))
        
        # Generate additional symptom questions
        questions.extend(self._generate_additional_symptom_questions(symptoms, animal))
        
        # Remove duplicates and sort by priority
        questions = self._deduplicate_questions(questions)
        questions.sort(key=lambda q: q.priority, reverse=True)
        
        return questions[:max_questions]
    
    def _generate_symptom_questions(self, symptom: SymptomExtraction, animal: str) -> List[FollowUpQuestion]:
        """Generate questions about specific symptoms"""
        questions = []
        symptom_display = symptom.symptom.replace("_", " ")
        
        # If duration is missing
        if not symptom.duration:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How long has your {animal} had {symptom_display}?",
                priority=5,
                reason=f"Duration of {symptom_display} is important for diagnosis"
            ))
        
        # If severity is missing
        if not symptom.severity:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How severe is the {symptom_display} (mild, moderate, or severe)?",
                priority=4,
                reason=f"Severity helps assess urgency and disease progression"
            ))
        
        # If frequency is missing
        if not symptom.frequency:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How often is your {animal} experiencing {symptom_display} (daily, intermittent, etc.)?",
                priority=3,
                reason=f"Frequency patterns can indicate disease type"
            ))
        
        # General symptom progression question
        questions.append(FollowUpQuestion(
            category="symptom_details",
            question=f"Is the {symptom_display} getting worse, staying the same, or improving?",
            priority=3,
            reason="Progression indicates disease trajectory"
        ))
        
        return questions
    
    def _generate_disease_questions(self, disease: DiseaseExtraction, animal: str) -> List[FollowUpQuestion]:
        """Generate questions about suspected diseases"""
        questions = []
        disease_name = disease.disease_name.replace("_", " ")
        
        # Look up disease in database for more specific questions
        if self.db:
            db_disease = self.db.search_by_name(disease.disease_name)
            if db_disease:
                # Ask about missing symptoms
                missing_symptoms = self._find_missing_symptoms(
                    db_disease.common_symptoms,
                    {s.symptom for s in []}  # Would be actual symptoms
                )
                
                if missing_symptoms:
                    symptoms_display = " or ".join([s.replace('_', ' ') for s in missing_symptoms])
                    questions.append(FollowUpQuestion(
                        category="disease_confirmation",
                        question=f"Has your {animal} shown any {symptoms_display}?",
                        priority=4,
                        reason=f"These symptoms are commonly associated with {disease_name}"
                    ))
                
                # Ask about causes if relevant
                if db_disease.causes:
                    cause_str = " or ".join(db_disease.causes[:2])
                    questions.append(FollowUpQuestion(
                        category="disease_confirmation",
                        question=f"Has your {animal} been exposed to {cause_str}?",
                        priority=3,
                        reason=f"These are common causes of {disease_name}"
                    ))
        
        # General disease questions
        questions.append(FollowUpQuestion(
            category="disease_confirmation",
            question=f"Is your {animal} up to date on vaccinations?",
            priority=4,
            reason=f"Vaccination status is crucial for infectious diseases like {disease_name}"
        ))
        
        questions.append(FollowUpQuestion(
            category="medical_history",
            question=f"Has your {animal} been diagnosed with {disease_name} before?",
            priority=2,
            reason=f"Previous occurrences help confirm recurrent conditions"
        ))
        
        return questions
    
    def _generate_medical_history_questions(self, animal: str) -> List[FollowUpQuestion]:
        """Generate general medical history questions"""
        return [
            FollowUpQuestion(
                category="medical_history",
                question=f"Is your {animal} on any current medications or supplements?",
                priority=4,
                reason="Medications can interact with treatments and mask symptoms"
            ),
            FollowUpQuestion(
                category="medical_history",
                question=f"Does your {animal} have any known allergies or sensitivities?",
                priority=4,
                reason="Allergies can cause or complicate symptoms"
            ),
            FollowUpQuestion(
                category="lifestyle",
                question=f"What type of food and diet is your {animal} on?",
                priority=3,
                reason="Diet directly impacts gastrointestinal and systemic health"
            ),
            FollowUpQuestion(
                category="lifestyle",
                question=f"Has there been any recent change in diet, environment, or routine?",
                priority=3,
                reason="Changes often trigger acute illness or symptom onset"
            )
        ]
    
    def _generate_additional_symptom_questions(
        self,
        current_symptoms: List[SymptomExtraction],
        animal: str
    ) -> List[FollowUpQuestion]:
        """Generate questions about additional symptoms not yet mentioned"""
        current_symptom_keys = {s.symptom for s in current_symptoms}
        questions = []
        
        # Important symptoms to check
        important_symptom_groups = [
            {
                "question": f"Have you noticed any changes in your {animal}'s appetite or drinking habits?",
                "symptoms": ["loss_of_appetite", "dehydration"],
                "priority": 4,
                "reason": "Appetite and hydration changes indicate systemic illness"
            },
            {
                "question": f"Is your {animal} experiencing any vomiting or diarrhea?",
                "symptoms": ["vomiting", "diarrhea"],
                "priority": 4,
                "reason": "GI symptoms are very common and important for diagnosis"
            },
            {
                "question": f"Have you noticed any fever, unusual energy levels, or lethargy?",
                "symptoms": ["fever", "lethargy"],
                "priority": 4,
                "reason": "These indicate systemic or infectious disease"
            },
            {
                "question": f"Is your {animal} scratching, licking, or showing any skin or ear issues?",
                "symptoms": ["itching", "skin_lesion", "discharge"],
                "priority": 3,
                "reason": "Dermatological issues are common and often missed"
            }
        ]
        
        for group in important_symptom_groups:
            if not any(s in current_symptom_keys for s in group["symptoms"]):
                questions.append(FollowUpQuestion(
                    category="additional_symptoms",
                    question=group["question"],
                    priority=group["priority"],
                    reason=group["reason"]
                ))
        
        return questions
    
    @staticmethod
    def _find_missing_symptoms(
        expected_symptoms: List[str],
        found_symptoms: Set[str]
    ) -> List[str]:
        """Find expected symptoms that haven't been mentioned"""
        return [s for s in expected_symptoms if s not in found_symptoms]
    
    @staticmethod
    def _deduplicate_questions(questions: List[FollowUpQuestion]) -> List[FollowUpQuestion]:
        """Remove duplicate questions"""
        seen = set()
        unique = []
        
        for q in questions:
            normalized = q.question.lower()
            if normalized not in seen:
                seen.add(normalized)
                unique.append(q)
        
        return unique
    
    def format_questions_for_display(self, questions: List[FollowUpQuestion]) -> str:
        """Format questions as readable output"""
        output = []
        output.append("\n" + "="*70)
        output.append("RECOMMENDED FOLLOW-UP QUESTIONS")
        output.append("="*70 + "\n")
        
        current_category = None
        question_num = 1
        
        for question in questions:
            if question.category != current_category:
                current_category = question.category
                category_display = question.category.replace("_", " ").title()
                output.append(f"\n[{category_display}]")
            
            priority_str = "⚠️  CRITICAL" if question.priority >= 5 else "★ HIGH" if question.priority >= 4 else "○ MEDIUM"
            output.append(f"  {question_num}. {question.question}")
            output.append(f"     {priority_str} | Reason: {question.reason}\n")
            question_num += 1
        
        output.append("="*70)
        return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    from nlp_patient_analyzer import PatientInfo, SymptomExtraction
    
    # Create sample data
    patient_info = PatientInfo(
        animal_type="dog",
        age="5 years old",
        breed="labrador",
        gender="male",
        weight="65 lbs"
    )
    
    symptoms = [
        SymptomExtraction(
            symptom="vomiting",
            duration="3 days",
            severity="moderate",
            frequency=None,
            context="Has been vomiting once per day"
        ),
        SymptomExtraction(
            symptom="diarrhea",
            duration="3 days",
            severity=None,
            frequency="intermittent",
            context="Loose stools, intermittent throughout the day"
        )
    ]
    
    diseases = [
        DiseaseExtraction(
            disease_name="gastroenteritis",
            confidence=0.85,
            related_symptoms=["vomiting", "diarrhea", "loss_of_appetite"]
        ),
        DiseaseExtraction(
            disease_name="pancreatitis",
            confidence=0.65,
            related_symptoms=["vomiting", "abdominal_pain"]
        )
    ]
    
    # Generate questions
    db = VeterinaryDatabase()
    generator = FollowUpQuestionGenerator(db)
    questions = generator.generate_questions(patient_info, symptoms, diseases)
    
    print(generator.format_questions_for_display(questions))
    
    db.close()

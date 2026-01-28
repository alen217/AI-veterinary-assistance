from typing import List, Optional, Set
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer, util


# ---------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------

@dataclass
class SymptomExtraction:
    symptom: str
    duration: Optional[str] = None
    severity: Optional[str] = None
    frequency: Optional[str] = None


@dataclass
class DiseaseExtraction:
    disease_name: str
    confidence: float


@dataclass
class FollowUpQuestion:
    category: str
    question: str
    priority: int          # higher = more important
    reasoning: str


@dataclass
class PatientInfo:
    animal_type: Optional[str] = None
    age: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[str] = None


# ---------------------------------------------------------------------
# Database placeholder
# ---------------------------------------------------------------------

class VeterinaryDatabase:
    def search_by_name(self, name: str):
        """
        Returns a disease object with attributes:
        - common_symptoms: List[str]
        - causes: List[str]
        """
        return None   # replace with real implementation


# ---------------------------------------------------------------------
# Follow-up Question Generator
# ---------------------------------------------------------------------

class FollowUpQuestionGenerator:
    """
    Generates disease-relevant, confidence-aware follow-up questions.
    Uses deterministic rules with optional AI-based priority boosting.
    """


    def __init__(self, db: Optional[VeterinaryDatabase] = None):
        self.db = db
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # -----------------------------------------------------------------
    # AI relevance scoring (SAFE STUB)
    # -----------------------------------------------------------------
    def _ai_score_question(self, question: str, context: dict) -> int:
        """
        Local AI relevance scoring using sentence embeddings.
        Returns a score from 1 to 5.
        """

        # 1. Build context text
        context_text = (
            f"Animal: {context['animal']}. "
            f"Symptoms: {', '.join([s['name'] for s in context['symptoms']])}. "
            f"Diseases: {', '.join([d['name'] for d in context['diseases']])}."
     )

        # 2. Compute embeddings
        embeddings = self.embedding_model.encode(
            [question, context_text],
            convert_to_tensor=True
        )

        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

        # 3. Map similarity → priority boost
        if similarity >= 0.80:
            return 5
        elif similarity >= 0.60:
            return 4
        elif similarity >= 0.45:
            return 3
        elif similarity >= 0.30:
            return 2
        else:
            return 1
    # -----------------------------------------------------------------
    # Main entry point
    # -----------------------------------------------------------------
    def generate_questions(
        self,
        patient_info: PatientInfo,
        symptoms: List[SymptomExtraction],
        diseases: List[DiseaseExtraction],
        max_questions: int = 8
    ) -> List[FollowUpQuestion]:

        animal = (patient_info.animal_type or "pet").lower()

        context = {
            "animal": animal,
            "patient": {
                "age": patient_info.age,
                "breed": patient_info.breed,
                "gender": patient_info.gender,
                "weight": patient_info.weight
            },
            "symptoms": [
                {
                    "name": s.symptom,
                    "duration": s.duration,
                    "severity": s.severity,
                    "frequency": s.frequency
                }
                for s in symptoms if s.symptom
            ],
            "diseases": [
                {"name": d.disease_name, "confidence": d.confidence}
                for d in diseases
            ]
        }

        extracted_symptoms: Set[str] = {
            s.symptom.lower() for s in symptoms if s.symptom
        }

        questions: List[FollowUpQuestion] = []

        # 1️⃣ Ask only missing details for reported symptoms
        for symptom in symptoms:
            if symptom.symptom:
                questions.extend(
                    self._generate_missing_symptom_detail_questions(symptom, animal)
                )

        # 2️⃣ Disease-specific confirmation (confidence gated)
        for disease in diseases:
            if disease.confidence >= 0.5:
                questions.extend(
                    self._generate_disease_specific_questions(
                        disease, animal, extracted_symptoms
                    )
                )

        # 3️⃣ General history / lifestyle questions (context-aware)
        questions.extend(
            self._generate_relevant_history_questions(symptoms, animal)
        )

        # Deduplicate
        questions = self._deduplicate_questions(questions)

        # --- AI relevance scoring (SAFE MODE) ---
        for q in questions:
            ai_score = self._ai_score_question(q.question, context)
            if ai_score > q.priority:
                q.priority = ai_score
        # --------------------------------------

        # Sort & limit
        questions.sort(key=lambda q: q.priority, reverse=True)
        return questions[:max_questions]

    # -----------------------------------------------------------------
    # Symptom detail questions
    # -----------------------------------------------------------------
    def _generate_missing_symptom_detail_questions(
        self,
        symptom: SymptomExtraction,
        animal: str
    ) -> List[FollowUpQuestion]:

        qs: List[FollowUpQuestion] = []
        name = symptom.symptom.replace("_", " ").strip()

        if not symptom.duration:
            qs.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How long has your {animal} had {name}?",
                priority=5,
                reasoning="Duration helps distinguish acute vs chronic conditions"
            ))

        if not symptom.severity:
            qs.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How severe is the {name} (mild, moderate, or severe)?",
                priority=4,
                reasoning="Severity indicates urgency and disease progression"
            ))

        if not symptom.frequency:
            qs.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How often does your {animal} experience {name}?",
                priority=3,
                reasoning="Frequency patterns aid differential diagnosis"
            ))

        return qs

    # -----------------------------------------------------------------
    # Disease-specific questions
    # -----------------------------------------------------------------
    def _generate_disease_specific_questions(
        self,
        disease: DiseaseExtraction,
        animal: str,
        extracted_symptoms: Set[str]
    ) -> List[FollowUpQuestion]:

        if not self.db:
            return []

        db_disease = self.db.search_by_name(disease.disease_name)
        if not db_disease:
            return []

        qs: List[FollowUpQuestion] = []
        disease_name = disease.disease_name.replace("_", " ").strip()
        base_priority = 5 if disease.confidence >= 0.8 else 4

        # Missing hallmark symptoms
        if hasattr(db_disease, "common_symptoms") and db_disease.common_symptoms:
            missing = self._find_missing_symptoms(
                db_disease.common_symptoms, extracted_symptoms
            )
            if missing:
                display = " or ".join(s.replace("_", " ") for s in missing[:2])
                qs.append(FollowUpQuestion(
                    category="disease_confirmation",
                    question=f"Has your {animal} shown any {display}?",
                    priority=base_priority,
                    reasoning=f"These symptoms are commonly associated with {disease_name}"
                ))

        # Exposure / cause questions (high confidence only)
        if (
            disease.confidence >= 0.7
            and hasattr(db_disease, "causes")
            and db_disease.causes
        ):
            causes = " or ".join(c.replace("_", " ") for c in db_disease.causes[:2])
            qs.append(FollowUpQuestion(
                category="disease_confirmation",
                question=f"Has your {animal} been exposed to {causes} recently?",
                priority=base_priority - 1,
                reasoning=f"Exposure history helps confirm or rule out {disease_name}"
            ))

        return qs

    # -----------------------------------------------------------------
    # General history questions
    # -----------------------------------------------------------------
    def _generate_relevant_history_questions(
        self,
        symptoms: List[SymptomExtraction],
        animal: str
    ) -> List[FollowUpQuestion]:

        symptom_set = {s.symptom.lower() for s in symptoms if s.symptom}
        qs: List[FollowUpQuestion] = []

        if {"vomiting", "diarrhea", "regurgitation"} & symptom_set:
            qs.append(FollowUpQuestion(
                category="lifestyle",
                question=f"What is your {animal}'s current diet and feeding routine?",
                priority=4,
                reasoning="Diet strongly influences gastrointestinal conditions"
            ))

        if {"lethargy", "fever", "weakness", "inappetence"} & symptom_set:
            qs.append(FollowUpQuestion(
                category="medical_history",
                question=f"Is your {animal} currently on any medications or supplements?",
                priority=4,
                reasoning="Medications can mask or worsen symptoms"
            ))

        return qs

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------
    @staticmethod
    def _find_missing_symptoms(
        expected: List[str],
        found: Set[str]
    ) -> List[str]:
        expected_lower = {s.lower() for s in expected}
        return [s for s in expected if s.lower() not in found]

    @staticmethod
    def _deduplicate_questions(
        questions: List[FollowUpQuestion]
    ) -> List[FollowUpQuestion]:

        seen = set()
        unique: List[FollowUpQuestion] = []

        for q in questions:
            key = (q.category, q.question.lower().strip())
            if key not in seen:
                seen.add(key)
                unique.append(q)

        return unique

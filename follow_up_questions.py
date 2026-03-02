"""
Follow-up Question Generator
Generates contextual follow-up questions based on patient analysis and database search results.

Bugs fixed from original:
  1. Animal relevance filter was applied to an empty list (before questions were built).
     Now applied AFTER all questions are collected.
  2. Disease confirmation only checked diseases[0]; now iterates all diseases via
     _generate_disease_crosscheck_questions() for every suspected disease.
  3. _generate_disease_crosscheck_questions() was never called â€” now wired into
     generate_questions().
  4. _generate_symptom_questions() was never called â€” generate_questions() now
     delegates to it instead of duplicating incomplete inline logic.
  5. format_questions_for_display() emitted duplicate category headers when
     priority-sorted questions interleaved categories. Now groups by category first.
  6. max_questions <= 0 now raises ValueError with a clear message.
"""

import os
import re
from typing import List, Dict, Optional, Set
from collections import Counter
from dataclasses import dataclass

from nlp_patient_analyzer import PatientInfo, SymptomExtraction, DiseaseExtraction
from mongo_disease_repository import MongoDiseaseRepository


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class FollowUpQuestion:
    """Structured follow-up question."""
    category: str   # symptom_details | disease_confirmation | medical_history | lifestyle | â€¦
    question: str
    priority: int   # 1â€“5, higher = more important
    reasoning: str  # Why this question is being asked


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class FollowUpQuestionGenerator:
    """Generates contextual follow-up questions based on patient analysis."""

    #: Animal types we handle explicitly; anything else is normalised to "pet".
    VALID_ANIMALS: Set[str] = {"dog", "cat", "bird", "rabbit", "horse", "cow"}
    STRUCTURE_LIMITS = {
        "top_disease": 3,
        "cross_disease": 2,
        "symptom_details": 4,
        "additional_symptoms": 2,
        "medical_history": 2,
    }

    def __init__(self, disease_repo: MongoDiseaseRepository) -> None:
        self.disease_repo = disease_repo
        self.question_templates = self._load_question_templates()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_questions(
        self,
        patient_info: PatientInfo,
        symptoms: List[SymptomExtraction],
        diseases: List[DiseaseExtraction],
        max_questions: int = 5,
    ) -> List[FollowUpQuestion]:
        """
        Generate a prioritised list of follow-up questions.

        Args:
            patient_info: Patient demographic information.
            symptoms:     Extracted symptoms (may have missing fields).
            diseases:     Suspected diseases ranked by confidence.
            max_questions: Maximum number of questions to return (must be > 0).

        Returns:
            List of FollowUpQuestion objects in deterministic stage order.

        Raises:
            ValueError: If max_questions is not a positive integer.
        """
        if max_questions <= 0:
            raise ValueError(f"max_questions must be a positive integer, got {max_questions}")

        # Resolve animal label.
        animal = (patient_info.animal_type or "").strip().lower()
        if animal not in self.VALID_ANIMALS:
            animal = "pet"

        ranked_diseases = sorted(diseases, key=lambda d: d.confidence, reverse=True)
        questions: List[FollowUpQuestion] = []

        # 1) Ask top-disease symptom confirmations first.
        questions.extend(
            self._generate_top_disease_symptom_questions(
                ranked_diseases,
                symptoms,
                animal,
                max_questions=self.STRUCTURE_LIMITS["top_disease"],
            )
        )

        # 2) Ask cross-check symptoms from other top diseases.
        questions.extend(
            self._generate_disease_crosscheck_questions(
                ranked_diseases[1:],
                symptoms,
                animal,
                max_per_disease=1,
            )[:self.STRUCTURE_LIMITS["cross_disease"]]
        )

        # 3) Fill missing details for currently extracted symptoms.
        detail_questions: List[FollowUpQuestion] = []
        for symptom in symptoms:
            detail_questions.extend(self._generate_symptom_questions(symptom, animal))
        questions.extend(detail_questions[:self.STRUCTURE_LIMITS["symptom_details"]])

        # 4) Ask additional symptom screening questions.
        questions.extend(
            self._generate_additional_symptom_questions(symptoms, animal)[
                :self.STRUCTURE_LIMITS["additional_symptoms"]
            ]
        )

        # 5) Ask brief medical history/lifestyle questions last.
        questions.extend(
            self._generate_medical_history_questions(animal)[
                :self.STRUCTURE_LIMITS["medical_history"]
            ]
        )

        # Filter out questions mentioning the wrong animal.
        questions = [q for q in questions if self._is_relevant_for_animal(q, animal)]

        # Deduplicate and cap.
        questions = self._deduplicate_questions(questions)
        return questions[:max_questions]

    def get_next_question(
        self,
        patient_info: PatientInfo,
        symptoms: List[SymptomExtraction],
        diseases: List[DiseaseExtraction],
    ) -> Optional[FollowUpQuestion]:
        """Return the single highest-priority question, or None if there are none."""
        questions = self.generate_questions(
            patient_info, symptoms, diseases, max_questions=1
        )
        return questions[0] if questions else None

    # ------------------------------------------------------------------
    # Private helpers â€” question builders
    # ------------------------------------------------------------------

    def _generate_symptom_questions(
        self, symptom: SymptomExtraction, animal: str
    ) -> List[FollowUpQuestion]:
        """
        Generate detail questions for a single symptom.
        FIX: this method now replaces the incomplete inline logic that was
        previously duplicated inside generate_questions().
        """
        questions: List[FollowUpQuestion] = []
        display = symptom.symptom.replace("_", " ")

        if not symptom.duration:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How long has your {animal} had {display}?",
                priority=5,
                reasoning=f"Duration of {display} is important for diagnosis",
            ))

        if not symptom.severity:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How severe is the {display} (mild, moderate, or severe)?",
                priority=4,
                reasoning="Severity helps assess urgency and disease progression",
            ))

        if not symptom.frequency:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"How often is your {animal} experiencing {display} (daily, intermittent, etc.)?",
                priority=3,
                reasoning="Frequency patterns can indicate disease type",
            ))

        # Only ask about progression once we have duration + severity context
        if symptom.duration and symptom.severity:
            questions.append(FollowUpQuestion(
                category="symptom_details",
                question=f"Is the {display} getting worse, staying the same, or improving?",
                priority=2,
                reasoning="Progression helps track disease trajectory",
            ))

        return questions

    def _generate_additional_symptom_questions(
        self,
        current_symptoms: List[SymptomExtraction],
        animal: str,
    ) -> List[FollowUpQuestion]:
        """Ask about common symptom groups not yet reported by the owner."""
        current_keys = {s.symptom for s in current_symptoms}

        groups = [
            {
                "question": f"Have you noticed any changes in your {animal}'s appetite or drinking habits?",
                "symptoms": ["loss_of_appetite", "dehydration"],
                "priority": 4,
                "reasoning": "Appetite and hydration changes indicate systemic illness",
            },
            {
                "question": f"Is your {animal} experiencing any vomiting or diarrhea?",
                "symptoms": ["vomiting", "diarrhea"],
                "priority": 4,
                "reasoning": "GI symptoms are very common and important for diagnosis",
            },
            {
                "question": f"Have you noticed any fever, unusual energy levels, or lethargy?",
                "symptoms": ["fever", "lethargy"],
                "priority": 4,
                "reasoning": "These indicate systemic or infectious disease",
            },
            {
                "question": f"Is your {animal} scratching, licking, or showing any skin or ear issues?",
                "symptoms": ["itching", "skin_lesion", "discharge"],
                "priority": 3,
                "reasoning": "Dermatological issues are common and often missed",
            },
        ]

        return [
            FollowUpQuestion(
                category="additional_symptoms",
                question=g["question"],
                priority=g["priority"],
                reasoning=g["reasoning"],
            )
            for g in groups
            if not any(s in current_keys for s in g["symptoms"])
        ]

    def _generate_medical_history_questions(self, animal: str) -> List[FollowUpQuestion]:
        """Return standard medical history and lifestyle questions."""
        return [
            FollowUpQuestion(
                category="medical_history",
                question=f"Is your {animal} on any current medications or supplements?",
                priority=4,
                reasoning="Medications can interact with treatments and mask symptoms",
            ),
            FollowUpQuestion(
                category="medical_history",
                question=f"Does your {animal} have any known allergies or sensitivities?",
                priority=4,
                reasoning="Allergies can cause or complicate symptoms",
            ),
            FollowUpQuestion(
                category="lifestyle",
                question=f"What type of food and diet is your {animal} on?",
                priority=3,
                reasoning="Diet directly impacts gastrointestinal and systemic health",
            ),
            FollowUpQuestion(
                category="lifestyle",
                question=f"Has there been any recent change in diet, environment, or routine?",
                priority=3,
                reasoning="Changes often trigger acute illness or symptom onset",
            ),
        ]

    def _generate_disease_questions(
        self,
        disease: DiseaseExtraction,
        animal: str,
        symptoms: List[SymptomExtraction],
    ) -> List[FollowUpQuestion]:
        """
        Ask about common symptoms of a single disease that haven't been reported.
        Capped at 2 questions per disease to avoid overwhelming the user.
        """
        db_disease = self.disease_repo.find_by_name(disease.disease_name)
        if not db_disease:
            return []

        present = {s.symptom for s in symptoms}
        missing = [
            s for s in db_disease.get("common_symptoms", [])
            if s not in present
        ]

        return [
            FollowUpQuestion(
                category="disease_confirmation",
                question=f"Has your {animal} also shown {sym.replace('_', ' ')}?",
                priority=4,
                reasoning=f"This symptom commonly occurs in {disease.disease_name}",
            )
            for sym in missing[:2]
        ]

    def _generate_top_disease_symptom_questions(
        self,
        diseases: List[DiseaseExtraction],
        symptoms: List[SymptomExtraction],
        animal: str,
        max_questions: int = 3,
    ) -> List[FollowUpQuestion]:
        """
        Ask confirmation questions from the top-ranked disease first.
        """
        if not diseases:
            return []

        top_disease = diseases[0]
        db_top = self.disease_repo.find_by_name(top_disease.disease_name)
        if not db_top:
            return []

        top_common = [s for s in db_top.get("common_symptoms", []) if s]
        if not top_common:
            return []

        present = {s.symptom for s in symptoms}
        missing = [sym for sym in top_common if sym not in present]
        if not missing:
            return []

        # Prioritise symptoms that are less common in other high-ranked diseases.
        other_top_symptoms: Set[str] = set()
        for candidate in diseases[1:3]:
            db_candidate = self.disease_repo.find_by_name(candidate.disease_name)
            if db_candidate:
                other_top_symptoms.update(db_candidate.get("common_symptoms", []) or [])

        missing.sort(key=lambda sym: (sym in other_top_symptoms, sym))
        top_label = top_disease.disease_name.replace("_", " ").title()

        return [
            FollowUpQuestion(
                category="disease_confirmation",
                question=f"Is your {animal} showing {sym.replace('_', ' ')}? (yes/no)",
                priority=5,
                reasoning=f"Top match is {top_label}; this symptom confirms or rules it out",
            )
            for sym in missing[:max_questions]
        ]

    def _generate_disease_crosscheck_questions(
        self,
        diseases: List[DiseaseExtraction],
        symptoms: List[SymptomExtraction],
        animal: str,
        max_per_disease: int = 2,
    ) -> List[FollowUpQuestion]:
        """
        Generate discriminating cross-check questions across the top suspected diseases.

        Symptoms that appear in only one disease (unique/discriminating) get priority 4.
        Symptoms shared across multiple diseases get priority 3.

        FIX: this method is now actually called from generate_questions(),
        replacing the broken single-disease logic that was there before.
        """
        if not diseases:
            return []

        present = {s.symptom for s in symptoms}

        # Collect symptom data for top-3 diseases by confidence
        disease_infos = []
        for disease in sorted(diseases, key=lambda d: d.confidence, reverse=True)[:3]:
            db_disease = self.disease_repo.find_by_name(disease.disease_name)
            if not db_disease:
                continue
            common = [s for s in db_disease.get("common_symptoms", []) if s]
            if not common:
                continue
            disease_infos.append({
                "name": disease.disease_name,
                "confidence": disease.confidence,
                "common_symptoms": common,
            })

        if not disease_infos:
            return []

        # Count how many diseases share each symptom
        symptom_frequency: Counter = Counter()
        for info in disease_infos:
            for sym in set(info["common_symptoms"]):
                symptom_frequency[sym] += 1

        questions: List[FollowUpQuestion] = []
        for info in disease_infos:
            missing = [s for s in info["common_symptoms"] if s not in present]
            if not missing:
                continue

            # Sort: unique (low frequency) symptoms first, then alphabetically for stability
            missing.sort(key=lambda s: (symptom_frequency[s], s))

            for sym in missing[:max_per_disease]:
                is_unique = symptom_frequency[sym] == 1
                questions.append(FollowUpQuestion(
                    category="disease_confirmation",
                    question=f"Has your {animal} shown {sym.replace('_', ' ')}? (yes/no)",
                    priority=4 if is_unique else 3,
                    reasoning=(
                        f"Cross-checks a common symptom of {info['name']} "
                        "to confirm or rule it out"
                    ),
                ))

        return questions

    # ------------------------------------------------------------------
    # Private helpers â€” filtering / utility
    # ------------------------------------------------------------------

    @staticmethod
    def _is_relevant_for_animal(question: FollowUpQuestion, animal: str) -> bool:
        """
        Return False if the question mentions a different animal species.
        Generic questions (containing only the target animal or no animal keyword) pass.

        FIX: was previously applied before questions were built, making it a no-op.
        """
        if animal == "pet":
            return True  # Generic fallback â€” allow everything

        animal_keywords = {"dog", "cat", "bird", "rabbit", "horse", "cow", "hamster"}
        question_text = question.question.lower()
        return not any(
            a in question_text
            for a in animal_keywords
            if a != animal
        )

    @staticmethod
    def _find_missing_symptoms(
        expected_symptoms: List[str],
        found_symptoms: Set[str],
    ) -> List[str]:
        """Return expected symptoms that are absent from found_symptoms."""
        return [s for s in expected_symptoms if s not in found_symptoms]

    @staticmethod
    def _deduplicate_questions(questions: List[FollowUpQuestion]) -> List[FollowUpQuestion]:
        """Remove duplicate questions while preserving order."""
        seen: Set[str] = set()
        seen_symptom_checks: Set[str] = set()
        unique: List[FollowUpQuestion] = []
        for q in questions:
            key = q.question.lower()
            if key not in seen:
                if q.category == "disease_confirmation":
                    symptom_key = FollowUpQuestionGenerator._canonical_confirmation_symptom_key(q.question)
                    if symptom_key and symptom_key in seen_symptom_checks:
                        continue
                    if symptom_key:
                        seen_symptom_checks.add(symptom_key)
                seen.add(key)
                unique.append(q)
        return unique

    @staticmethod
    def _canonical_confirmation_symptom_key(question: str) -> Optional[str]:
        """
        Extract normalized symptom phrase from yes/no disease confirmation prompts.
        """
        q_lower = (question or "").lower().strip()
        match = re.search(r"\bshow(?:ing|n)\s+(.+?)\?\s*(?:\(yes/no\))?$", q_lower)
        if not match:
            return None
        return re.sub(r"\s+", " ", match.group(1).strip())

    @staticmethod
    def _is_core_symptom_complete(symptoms: List[SymptomExtraction]) -> bool:
        """Return True only if every symptom has both duration and severity filled in."""
        return all(s.duration and s.severity for s in symptoms)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def format_questions_for_display(self, questions: List[FollowUpQuestion]) -> str:
        """
        Format questions as a readable, category-grouped block of text.

        FIX: original sorted by priority first, causing the same category header
        to be printed multiple times when questions from the same category were
        interleaved with other categories. Now groups by category before rendering.
        """
        lines = [
            "",
            "=" * 70,
            "RECOMMENDED FOLLOW-UP QUESTIONS",
            "=" * 70,
            "",
        ]

        # Group questions by category, preserving within-category priority order
        from collections import defaultdict
        by_category: Dict[str, List[FollowUpQuestion]] = defaultdict(list)
        category_order: List[str] = []
        for q in questions:
            if q.category not in by_category:
                category_order.append(q.category)
            by_category[q.category].append(q)

        question_num = 1
        for category in category_order:
            category_display = category.replace("_", " ").title()
            lines.append(f"\n[{category_display}]")
            for q in sorted(by_category[category], key=lambda x: x.priority, reverse=True):
                if q.priority >= 5:
                    priority_str = "âš ï¸  CRITICAL"
                elif q.priority >= 4:
                    priority_str = "â˜… HIGH"
                else:
                    priority_str = "â—‹ MEDIUM"
                lines.append(f"  {question_num}. {q.question}")
                lines.append(f"     {priority_str} | Reasoning: {q.reasoning}")
                lines.append("")
                question_num += 1

        lines.append("=" * 70)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Template loader (retained for potential future template-driven use)
    # ------------------------------------------------------------------

    @staticmethod
    def _load_question_templates() -> Dict[str, List[Dict]]:
        """Question templates organised by category (available for template-driven extensions)."""
        return {
            "symptom_details": [
                {"template": "How long has your {animal} had {symptom}?",                      "priority": 4},
                {"template": "Is the {symptom} getting worse, staying the same, or improving?", "priority": 3},
                {"template": "Have you noticed any patterns to when the {symptom} occurs?",     "priority": 2},
                {"template": "Is your {animal} in pain or experiencing discomfort with the {symptom}?", "priority": 3},
            ],
            "additional_symptoms": [
                {"template": "Have you noticed any changes in your {animal}'s appetite or drinking habits?", "priority": 4},
                {"template": "Is your {animal} experiencing any eye or ear discharge or irritation?",        "priority": 3},
                {"template": "Have you noticed any changes in weight, energy level, or activity?",           "priority": 3},
                {"template": "Is your {animal} scratching, licking, or showing skin issues anywhere?",       "priority": 2},
            ],
            "disease_confirmation": [
                {"template": "Has your {animal} been exposed to other sick animals recently?", "priority": 4},
                {"template": "Is your {animal} up to date on vaccinations?",                  "priority": 4},
                {"template": "When was your {animal}'s last veterinary checkup?",             "priority": 3},
                {"template": "Has your {animal} had this condition before?",                  "priority": 2},
            ],
            "medical_history": [
                {"template": "Does your {animal} have any known allergies or sensitivities?",  "priority": 4},
                {"template": "Is your {animal} on any current medications or supplements?",    "priority": 4},
                {"template": "Has your {animal} had any surgeries or significant injuries?",   "priority": 2},
            ],
            "lifestyle": [
                {"template": "What type of food and diet is your {animal} on?",               "priority": 4},
                {"template": "How much exercise and activity does your {animal} get daily?",   "priority": 2},
                {"template": "Has there been any recent change in diet, environment, or routine?", "priority": 3},
                {"template": "Does your {animal} have access to outdoor areas or other animals?",  "priority": 2},
            ],
            "treatment_history": [
                {"template": "Has your {animal} been treated for this issue before? If yes, what was the treatment?", "priority": 3},
                {"template": "Are you currently giving any home remedies or over-the-counter treatments?",             "priority": 3},
            ],
            "symptom_severity": [
                {"template": "Is your {animal} able to eat and drink normally despite the {symptom}?", "priority": 4},
                {"template": "Has this condition affected your {animal}'s daily activities or sleep?",  "priority": 3},
                {"template": "Are there any other symptoms you've noticed that seem unusual?",           "priority": 2},
            ],
        }


# ---------------------------------------------------------------------------
# Manual smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    class MockRepo:
        def find_by_name(self, name: str):
            return {"common_symptoms": ["loss_of_appetite", "fever"], "causes": ["dietary_indiscretion"]}

    patient = PatientInfo(animal_type="dog", age="5 years", breed="labrador", gender="male", weight="65 lbs")

    symptoms = [
        SymptomExtraction(symptom="vomiting",  duration="3 days", severity="moderate", frequency=None, context="Owner reports vomiting for 3 days"),
        SymptomExtraction(symptom="diarrhea",  duration="3 days", severity=None,       frequency="intermittent", context="Owner reports intermittent diarrhea for 3 days"),
    ]

    diseases = [
        DiseaseExtraction(disease_name="gastroenteritis", confidence=0.85, related_symptoms=["vomiting", "diarrhea"]),
        DiseaseExtraction(disease_name="pancreatitis",    confidence=0.65, related_symptoms=["vomiting", "abdominal_pain"]),
    ]

    gen = FollowUpQuestionGenerator(MockRepo())

    next_q = gen.get_next_question(patient, symptoms, diseases)
    print(f"Next Question: {next_q.question if next_q else 'None'}")

    questions = gen.generate_questions(patient, symptoms, diseases, max_questions=7)
    print(gen.format_questions_for_display(questions))


class FollowUpQuestionGenerator:
    """
    Generates disease-relevant, confidence-aware follow-up questions
    """


    def __init__(self, db: Optional[VeterinaryDatabase] = None):
        self.db = db

    def generate_questions(
        self,
        patient_info: PatientInfo,
        symptoms: List[SymptomExtraction],
        diseases: List[DiseaseExtraction],
        max_questions: int = 8
    ) -> List[FollowUpQuestion]:

        animal = patient_info.animal_type or "pet"
        context = {
    "animal": animal,
    "symptoms": [
        {
            "name": s.symptom,
            "duration": s.duration,
            "severity": s.severity,
            "frequency": s.frequency
        }
        for s in symptoms
    ],
    "diseases": [
        {
            "name": d.disease_name,
            "confidence": d.confidence
        }
        for d in diseases
    ]
}

        questions: List[FollowUpQuestion] = []

        extracted_symptoms = {s.symptom for s in symptoms}

        # 1. Ask ONLY missing details for PRESENT symptoms
        for symptom in symptoms:
            questions.extend(
                self._generate_missing_symptom_detail_questions(symptom, animal)
            )

        # 2. Ask disease-confirmation questions ONLY for high-confidence diseases
        for disease in diseases:
            if disease.confidence >= 0.5:
                questions.extend(
                    self._generate_disease_specific_questions(
                        disease,
                        animal,
                        extracted_symptoms
                    )
                )

        # 3. Ask general history ONLY if still relevant
        questions.extend(
            self._generate_relevant_history_questions(symptoms, animal)
        )

        # Deduplicate + sort
        questions = self._deduplicate_questions(questions)
        questions.sort(key=lambda q: q.priority, reverse=True)

        return questions[:max_questions]

    # ------------------------------------------------------------------

    def _generate_missing_symptom_detail_questions(
        self,
        symptom: SymptomExtraction,
        animal: str
    ) -> List[FollowUpQuestion]:

        q = []
        name = symptom.symptom.replace("_", " ")

        if not symptom.duration:
            q.append(FollowUpQuestion(
                "symptom_details",
                f"How long has your {animal} had {name}?",
                5,
                "Symptom duration is critical for diagnosis"
            ))

        if not symptom.severity:
            q.append(FollowUpQuestion(
                "symptom_details",
                f"How severe is the {name} (mild, moderate, severe)?",
                4,
                "Severity determines urgency and disease stage"
            ))

        if not symptom.frequency:
            q.append(FollowUpQuestion(
                "symptom_details",
                f"How often does the {name} occur?",
                3,
                "Frequency helps distinguish acute vs chronic illness"
            ))

        return q

    # ------------------------------------------------------------------

    def _generate_disease_specific_questions(
        self,
        disease: DiseaseExtraction,
        animal: str,
        extracted_symptoms: set
    ) -> List[FollowUpQuestion]:

        q = []
        disease_name = disease.disease_name.replace("_", " ")

        base_priority = 5 if disease.confidence >= 0.8 else 4

        if not self.db:
            return q

        db_disease = self.db.search_by_name(disease.disease_name)
        if not db_disease:
            return q

        # Ask ONLY about symptoms NOT yet mentioned
        missing = self._find_missing_symptoms(
            db_disease.common_symptoms,
            extracted_symptoms
        )

        if missing:
            display = " or ".join(s.replace("_", " ") for s in missing[:2])
            q.append(FollowUpQuestion(
                "disease_confirmation",
                f"Has your {animal} shown any {display}?",
                base_priority,
                f"These symptoms are commonly linked to {disease_name}"
            ))

        # Cause exposure question (only if disease confidence is high)
        if db_disease.causes and disease.confidence >= 0.7:
            causes = " or ".join(db_disease.causes[:2])
            q.append(FollowUpQuestion(
                "disease_confirmation",
                f"Has your {animal} been exposed to {causes}?",
                base_priority - 1,
                f"Exposure helps confirm {disease_name}"
            ))

        return q

    # ------------------------------------------------------------------

    def _generate_relevant_history_questions(
        self,
        symptoms: List[SymptomExtraction],
        animal: str
    ) -> List[FollowUpQuestion]:

        symptom_keys = {s.symptom for s in symptoms}
        q = []

        if {"vomiting", "diarrhea"} & symptom_keys:
            q.append(FollowUpQuestion(
                "lifestyle",
                f"What type of food and diet is your {animal} on?",
                4,
                "Diet is closely linked to gastrointestinal conditions"
            ))

        if not symptom_keys.isdisjoint({"lethargy", "fever"}):
            q.append(FollowUpQuestion(
                "medical_history",
                f"Is your {animal} currently on any medications?",
                4,
                "Medications may mask or worsen symptoms"
            ))

        return q

    # ------------------------------------------------------------------

    @staticmethod
    def _find_missing_symptoms(expected: List[str], found: set) -> List[str]:
        return [s for s in expected if s not in found]

    @staticmethod
    def _deduplicate_questions(questions: List[FollowUpQuestion]) -> List[FollowUpQuestion]:
        seen = set()
        unique = []
        for q in questions:
            key = q.question.lower()
            if key not in seen:
                seen.add(key)
                unique.append(q)
        return unique

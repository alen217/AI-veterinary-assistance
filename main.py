"""
Main Veterinary AI Assistant Application
Orchestrates patient text analysis, database searching, and follow-up question generation
"""
from mongo_disease_repository import MongoDiseaseRepository

from typing import Dict, List
import json

from nlp_patient_analyzer import VeterinaryNLPAnalyzer, AnalysisResult
from follow_up_questions import FollowUpQuestionGenerator

from ava.skin_disease.adapter import SkinDiseaseAdapter


class VeterinaryAIAssistant:
    """
    Main AI assistant for veterinary patient analysis.
    Integrates NLP analysis, database search, and follow-up question generation.
    """

    
    def __init__(self, disease_repo: MongoDiseaseRepository | None = None):
        self.analyzer = VeterinaryNLPAnalyzer()
        self.disease_repo = disease_repo or MongoDiseaseRepository()
        self.question_generator = FollowUpQuestionGenerator(self.disease_repo)  

        
    class VeterinaryAIAssistant:
        def __init__(self, disease_repo=None):
            self.analyzer = VeterinaryNLPAnalyzer()
            self.disease_repo = disease_repo or MongoDiseaseRepository()
            self.question_generator = FollowUpQuestionGenerator(self.disease_repo)
            self.skin_adapter = SkinDiseaseAdapter()
    
    def analyze_skin_image(self, image_path: str) -> dict:
    
        """
        Optional ML-based skin disease analysis
        """
        return self.skin_adapter.analyze_image(image_path)

    # ------------------------------------------------------------------
    # MAIN PIPELINE
    # ------------------------------------------------------------------
    def _decide_question_limit(self, db_matches: list[dict]) -> int:
        if not db_matches:
            return 6  # low confidence fallback

        top_confidence = db_matches[0].get("confidence", 0.0)

        if top_confidence >= 0.75:
            return 2
        elif top_confidence >= 0.40:
            return 4
        else:
            return 6

    def analyze_patient_text(
        self,
        patient_text: str,
        generate_questions: bool = True
    ) -> Dict:
        """
        Complete analysis of patient text.
        """

        # Step 1: NLP analysis
        analysis = self.analyzer.analyze(patient_text)

        # Step 2: Database search
        related_diseases = self._search_for_related_diseases(analysis)

        # Step 3: Follow-up questions
        questions = []
        if generate_questions:
            limit = self._decide_question_limit(related_diseases)

            questions = self.question_generator.generate_questions(
                analysis.patient_info,
                analysis.symptoms,
                analysis.suspected_diseases,
                max_questions=limit
            )


        result = {
            "patient_analysis": analysis,
            "database_matches": related_diseases,
            "follow_up_questions": questions,
            "recommendations": self._generate_recommendations(
                analysis, related_diseases
            )
        }

        return result

    # ------------------------------------------------------------------
    # DATABASE MATCHING
    # ------------------------------------------------------------------

    def _search_for_related_diseases(self, analysis: AnalysisResult) -> List[Dict]:
        if not analysis.symptoms:
            return []

        symptom_keys = [s.symptom for s in analysis.symptoms]

        db_results = self.disease_repo.find_by_symptoms(symptom_keys)

        results = []
        for disease in db_results:
            results.append({
                "name": disease["name"],
                "scientific_name": disease.get("scientific_name"),
                "description": disease.get("description"),
                "treatment": disease.get("treatment"),
                "prevention": disease.get("prevention"),
                "severity": disease.get("severity"),
                "affected_species": disease.get("affected_species", []),
                "confidence": disease.get("match_score", 0.0),
                "symptom_matches": disease.get("match_count", 0),
            })

        return results[:5]



    # ------------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self,
        analysis: AnalysisResult,
        db_matches: List[Dict]
    ) -> Dict:

        return {
            "urgency": self._assess_urgency(analysis, db_matches),
            "recommended_actions": self._get_recommended_actions(
                analysis, db_matches
            ),
            "important_notes": self._get_important_notes(analysis),
            "when_to_seek_immediate_care":
                self._get_emergency_indicators(),
        }

    def _assess_urgency(
        self,
        analysis: AnalysisResult,
        db_matches: List[Dict]
    ) -> str:

        severe_symptoms = {
            "labored_breathing", "seizure", "fever", "severe_lethargy"
        }

        has_severe = any(
            s.symptom in severe_symptoms for s in analysis.symptoms
        )

        has_severe_disease = any(
            d["severity"] == "severe" for d in db_matches
        )

        if has_severe or has_severe_disease:
            return "URGENT – Immediate veterinary care recommended"
        elif analysis.suspected_diseases:
            return "MODERATE – Schedule vet visit within 24–48 hours"
        else:
            return "LOW – Monitor symptoms closely"

    def _get_recommended_actions(
        self,
        analysis: AnalysisResult,
        db_matches: List[Dict]
    ) -> List[str]:

        actions = ["Schedule a veterinary consultation"]

        symptom_set = {s.symptom for s in analysis.symptoms}

        if symptom_set & {"vomiting", "diarrhea", "fever"}:
            actions.append(
                "Ensure adequate hydration and monitor intake"
            )

        if symptom_set & {"vomiting", "loss_of_appetite"}:
            actions.append(
                "Temporarily offer a bland diet if advised by a vet"
            )

        if db_matches and db_matches[0]["severity"] == "severe":
            actions.append("Do not delay professional treatment")

        actions.append(
            "Track symptom progression, duration, and triggers"
        )

        return actions

    def _get_important_notes(
        self,
        analysis: AnalysisResult
    ) -> List[str]:

        notes = []

        if analysis.patient_info.animal_type:
            notes.append(
                f"Species: {analysis.patient_info.animal_type}"
            )

        if any(s.severity == "severe" for s in analysis.symptoms):
            notes.append(
                "Severe symptoms detected — urgent evaluation advised"
            )

        if len(analysis.suspected_diseases) > 2:
            notes.append(
                "Multiple possible conditions — professional diagnosis essential"
            )

        return notes

    def _get_emergency_indicators(self) -> List[str]:
        return [
            "Severe breathing difficulty",
            "Unconsciousness or collapse",
            "Uncontrolled seizures",
            "Heavy bleeding",
            "Suspected poisoning",
        ]

    # ------------------------------------------------------------------
    # REPORTING
    # ------------------------------------------------------------------

    def generate_report(self, analysis_result: Dict) -> str:
        """
        Generate a human-readable report.
        """
        return json.dumps(
            {
                "patient_info":
                    analysis_result["patient_analysis"].patient_info.__dict__,
                "symptoms": [
                    s.__dict__
                    for s in analysis_result["patient_analysis"].symptoms
                ],
                "matches": analysis_result["database_matches"],
                "recommendations": analysis_result["recommendations"],
                "follow_up_questions": [
                    q.question
                    for q in analysis_result["follow_up_questions"]
                ],
            },
            indent=2,
            default=str,
        )

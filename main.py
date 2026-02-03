from mongo_disease_repository import MongoDiseaseRepository
from nlp_patient_analyzer import VeterinaryNLPAnalyzer, AnalysisResult
from follow_up_questions import FollowUpQuestionGenerator
from custom_ai_followup import CustomAIFollowUpGenerator, AIFollowUpQuestion
from dynamic_confidence_updater import DynamicDiseaseRanker, FollowUpAnswer, AdaptiveQuestionGenerator
from ava.skin_disease.adapter import SkinDiseaseAdapter
from typing import Dict, List, Optional
import json
import os


class VeterinaryAIAssistant:
    """
    Main AI assistant for veterinary patient analysis.

    Responsibilities:
    - NLP symptom extraction
    - MongoDB disease matching
    - Explainable follow-up questions
    - Optional skin disease ML inference
    """

    def __init__(self, disease_repo: MongoDiseaseRepository | None = None, use_ai_questions: bool = True):
        # NLP
        self.analyzer = VeterinaryNLPAnalyzer()

        # Mongo disease repository
        self.disease_repo = disease_repo or MongoDiseaseRepository()

        # Follow-up questions - Choose between AI or Template-based
        self.use_ai_questions = use_ai_questions
        
        # Template-based (fallback)
        self.question_generator = FollowUpQuestionGenerator(self.disease_repo)
        
        # Custom AI-powered question generator (trained model)
        try:
            if use_ai_questions:
                self.ai_question_generator = CustomAIFollowUpGenerator()
                print("✅ Custom AI-powered question generation ENABLED (local model)")
            else:
                self.ai_question_generator = None
                print("⚠️  AI question generation disabled - using template-based questions")
        except Exception as e:
            self.ai_question_generator = None
            print(f"⚠️  Custom AI model unavailable: {e}")
            print("   Falling back to template-based questions")
            print("   To enable: cd ml_training/vet_followup_qa && python train.py")

        # Optional skin disease ML adapter
        self.skin_adapter = SkinDiseaseAdapter()
        
        # Dynamic disease ranker for confidence updates
        self.disease_ranker = None  # Initialized after first analysis

    # ------------------------------------------------------------------
    # OPTIONAL ML: SKIN DISEASE ANALYSIS
    # ------------------------------------------------------------------
    def analyze_skin_image(self, image_path: str) -> Dict | None:
        """
        Run ML-based skin disease prediction if model is available.
        Returns None if ML is unavailable.
        """
        if not getattr(self.skin_adapter, "available", False):
            return None
    
        return self.skin_adapter.analyze_image(image_path)

    # ------------------------------------------------------------------
    # MAIN NLP + MONGO PIPELINE
    # ------------------------------------------------------------------
    def analyze_patient_text(
        self,
        patient_text: str,
        generate_questions: bool = True,
        previous_answers: Dict = None
    ) -> Dict:
        """
        Full text-based patient analysis pipeline.
        Now with AI-powered or template-based follow-up questions.
        
        Args:
            patient_text: Patient description from user
            generate_questions: Whether to generate follow-up questions
            previous_answers: Dict of previously answered questions (for AI context)
        """

        # Step 1: NLP
        analysis: AnalysisResult = self.analyzer.analyze(patient_text)

        # Step 2: MongoDB disease search with improved scoring
        related_diseases = self._search_for_related_diseases(analysis)

        # Step 3: Follow-up questions (AI or Template-based)
        questions = []
        if generate_questions:
            limit = self._decide_question_limit(related_diseases)
            
            # Try AI-generated questions first
            if self.ai_question_generator:
                questions = self._generate_ai_questions(
                    analysis, related_diseases, limit, previous_answers
                )
            
            # Fallback to template-based questions if AI fails or unavailable
            if not questions:
                questions = self.question_generator.generate_questions(
                    analysis.patient_info,
                    analysis.symptoms,
                    analysis.suspected_diseases,
                    max_questions=limit
                )

        return {
            "patient_analysis": analysis,
            "database_matches": related_diseases,
            "follow_up_questions": questions,
            "recommendations": self._generate_recommendations(
                analysis, related_diseases
            ),
            "question_source": "ai" if (self.ai_question_generator and questions) else "template"
        }

    # ------------------------------------------------------------------
    # MONGO SEARCH
    # ------------------------------------------------------------------
    def _search_for_related_diseases(self, analysis: AnalysisResult) -> List[Dict]:
        if not analysis.symptoms:
            return []

        symptom_keys = [s.symptom for s in analysis.symptoms]

        db_results = self.disease_repo.find_by_symptoms(symptom_keys)

        results = []
        for d in db_results:
            results.append({
                "name": d.get("name"),
                "scientific_name": d.get("scientific_name"),
                "description": d.get("description"),
                "treatment": d.get("treatment"),
                "prevention": d.get("prevention"),
                "severity": d.get("severity"),
                "affected_species": d.get("affected_species", []),
                "confidence": d.get("match_score", d.get("confidence", 0.0)),
                "symptom_match_count": d.get("symptom_match_count", 0)
            })

        return results[:5]
    
    # ------------------------------------------------------------------
    # AI QUESTION GENERATION
    # ------------------------------------------------------------------
    def _generate_ai_questions(
        self,
        analysis: AnalysisResult,
        related_diseases: List[Dict],
        limit: int,
        previous_answers: Dict = None
    ) -> List:
        """Generate AI-powered follow-up questions"""
        try:
            # Convert analysis objects to dicts for AI
            patient_dict = {
                "animal_type": analysis.patient_info.animal_type,
                "age": analysis.patient_info.age,
                "breed": analysis.patient_info.breed,
                "weight": analysis.patient_info.weight,
                "gender": analysis.patient_info.gender
            }
            
            symptoms_dict = [
                {
                    "symptom": s.symptom,
                    "duration": s.duration,
                    "severity": s.severity,
                    "frequency": s.frequency,
                    "context": s.context
                }
                for s in analysis.symptoms
            ]
            
            suspected_dict = [
                {
                    "disease_name": d.disease_name,
                    "confidence": d.confidence
                }
                for d in analysis.suspected_diseases
            ]
            
            # Generate AI questions
            ai_questions = self.ai_question_generator.generate_questions(
                patient_info=patient_dict,
                symptoms=symptoms_dict,
                suspected_diseases=suspected_dict,
                database_matches=related_diseases,
                max_questions=limit,
                previous_answers=previous_answers
            )
            
            return ai_questions
            
        except Exception as e:
            print(f"⚠️  AI question generation failed: {e}")
            return []

    # ------------------------------------------------------------------
    # QUESTION LIMIT LOGIC
    # ------------------------------------------------------------------
    def _decide_question_limit(self, db_matches: List[Dict]) -> int:
        if not db_matches:
            return 6

        top_confidence = db_matches[0].get("confidence", 0.0)

        if top_confidence >= 0.75:
            return 2
        elif top_confidence >= 0.40:
            return 4
        else:
            return 6

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
    # DYNAMIC CONFIDENCE UPDATING
    # ------------------------------------------------------------------
    
    def update_diagnosis_with_answer(
        self,
        question: str,
        answer: str,
        category: str = "general",
        related_disease: str = None,
        symptom_to_check: str = None
    ) -> Dict:
        """
        Update disease confidence based on follow-up answer.
        Implements feedback loop for continuous refinement.
        
        Args:
            question: The follow-up question that was asked
            answer: User's answer to the question
            category: Question category (disease_confirmation, symptom_details, etc.)
            related_disease: Which disease this question relates to
            symptom_to_check: Specific symptom being checked
            
        Returns:
            Updated disease rankings and explanation
        """
        if not self.disease_ranker:
            return {
                "error": "No active diagnosis session. Run analyze_patient_text first.",
                "diseases": []
            }
        
        # Create answer object
        follow_up_answer = FollowUpAnswer(
            question=question,
            answer=answer,
            category=category,
            related_disease=related_disease,
            symptom_to_check=symptom_to_check
        )
        
        # Update confidence scores
        updated_diseases = self.disease_ranker.update_confidence_with_answer(follow_up_answer)
        
        # Generate explanation
        explanation = self.disease_ranker.explain_ranking()
        
        # Get next best questions
        patient_symptoms = [d.get('symptom_match_count', 0) for d in updated_diseases]
        adaptive_gen = AdaptiveQuestionGenerator(self.disease_ranker, self.disease_repo)
        next_questions = adaptive_gen.get_next_best_questions([], max_questions=3)
        
        return {
            "updated_diseases": updated_diseases,
            "explanation": explanation,
            "next_questions": next_questions,
            "answer_processed": True
        }
    
    def start_dynamic_diagnosis_session(self, initial_diseases: List[Dict]):
        """
        Initialize dynamic disease ranker for a consultation session
        
        Args:
            initial_diseases: Initial disease matches from analyze_patient_text
        """
        # Store initial confidence for tracking
        for disease in initial_diseases:
            disease['initial_confidence'] = disease.get('confidence', 0.0)
        
        self.disease_ranker = DynamicDiseaseRanker(initial_diseases)
        print("✅ Dynamic diagnosis session started")
        print(f"   Tracking {len(initial_diseases)} diseases")

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
                    q.question if hasattr(q, 'question') else str(q)
                    for q in analysis_result["follow_up_questions"]
                ],
            },
            indent=2,
            default=str,
        )
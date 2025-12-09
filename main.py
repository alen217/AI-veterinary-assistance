"""
Main Veterinary AI Assistant Application
Orchestrates patient text analysis, database searching, and follow-up question generation
"""

from typing import Optional, Dict, List
import json
from nlp_patient_analyzer import VeterinaryNLPAnalyzer, AnalysisResult
from veterinary_database import VeterinaryDatabase
from follow_up_questions import FollowUpQuestionGenerator, FollowUpQuestion


class VeterinaryAIAssistant:
    """
    Main AI assistant for veterinary patient analysis
    Integrates NLP analysis, database search, and question generation
    """
    
    def __init__(self, db_path: str = "veterinary_database.db"):
        """Initialize the assistant"""
        self.analyzer = VeterinaryNLPAnalyzer()
        self.db = VeterinaryDatabase(db_path)
        self.question_generator = FollowUpQuestionGenerator(self.db)
        self.analysis_history = []
    
    def analyze_patient_text(self, patient_text: str, generate_questions: bool = True) -> Dict:
        """
        Complete analysis of patient text
        
        Args:
            patient_text: Raw patient description
            generate_questions: Whether to generate follow-up questions
            
        Returns:
            Dictionary with all analysis results
        """
        # Step 1: Analyze patient text
        print("Step 1: Analyzing patient text...")
        analysis = self.analyzer.analyze(patient_text)
        
        # Step 2: Search database for related diseases
        print("Step 2: Searching disease database...")
        related_diseases = self._search_for_related_diseases(analysis)
        
        # Step 3: Generate follow-up questions
        questions = []
        if generate_questions:
            print("Step 3: Generating follow-up questions...")
            questions = self.question_generator.generate_questions(
                analysis.patient_info,
                analysis.symptoms,
                analysis.suspected_diseases
            )
        
        # Compile results
        result = {
            "patient_analysis": analysis,
            "database_matches": related_diseases,
            "follow_up_questions": questions,
            "recommendations": self._generate_recommendations(analysis, related_diseases)
        }
        
        self.analysis_history.append(result)
        return result
    
    def _search_for_related_diseases(self, analysis: AnalysisResult) -> List[Dict]:
        """Search database for diseases matching the symptoms"""
        if not analysis.symptoms:
            return []
        
        symptom_keys = [s.symptom for s in analysis.symptoms]
        db_results = self.db.search_by_symptoms(symptom_keys)
        
        matched_diseases = []
        for disease, symptom_match_count in db_results:
            # Find corresponding suspected disease if exists
            suspected = next(
                (d for d in analysis.suspected_diseases if d.disease_name == disease.name.lower()),
                None
            )
            
            confidence = suspected.confidence if suspected else (symptom_match_count / len(disease.common_symptoms))
            
            matched_diseases.append({
                "name": disease.name,
                "scientific_name": disease.scientific_name,
                "confidence": confidence,
                "symptom_matches": symptom_match_count,
                "description": disease.description,
                "treatment": disease.treatment,
                "prevention": disease.prevention,
                "severity": disease.severity,
                "affected_species": disease.affected_species
            })
        
        return matched_diseases[:5]  # Top 5 matches
    
    def _generate_recommendations(self, analysis: AnalysisResult, db_matches: List[Dict]) -> Dict:
        """Generate clinical recommendations"""
        recommendations = {
            "urgency": self._assess_urgency(analysis, db_matches),
            "recommended_actions": self._get_recommended_actions(analysis, db_matches),
            "important_notes": self._get_important_notes(analysis),
            "when_to_seek_immediate_care": self._get_emergency_indicators(analysis)
        }
        return recommendations
    
    def _assess_urgency(self, analysis: AnalysisResult, db_matches: List[Dict]) -> str:
        """Assess how urgent the situation is"""
        severe_symptoms = [
            "labored_breathing", "seizure", "fever", "severe_lethargy"
        ]
        
        critical_severity_diseases = [d for d in db_matches if d["severity"] == "severe"]
        
        has_severe_symptoms = any(
            s.symptom in severe_symptoms for s in analysis.symptoms
        )
        
        severe_symptom_presence = sum(
            1 for s in analysis.symptoms if s.severity == "severe"
        )
        
        if has_severe_symptoms or critical_severity_diseases:
            if critical_severity_diseases:
                return "URGENT - Immediate veterinary consultation recommended"
            return "HIGH - Schedule veterinary appointment soon"
        elif severe_symptom_presence > 0 or analysis.suspected_diseases:
            return "MODERATE - Schedule veterinary appointment within 24-48 hours"
        else:
            return "LOW - Monitor and schedule appointment if symptoms persist"
    
    def _get_recommended_actions(self, analysis: AnalysisResult, db_matches: List[Dict]) -> List[str]:
        """Get recommended actions based on analysis"""
        actions = [
            "Schedule veterinary appointment for professional diagnosis"
        ]
        
        # Hydration advice for GI symptoms
        if any(s.symptom in ["vomiting", "diarrhea", "fever"] for s in analysis.symptoms):
            actions.append("Ensure your pet has access to fresh water to prevent dehydration")
        
        # Food management
        if any(s.symptom in ["vomiting", "diarrhea", "loss_of_appetite"] for s in analysis.symptoms):
            actions.append("Consider withholding food for 12-24 hours, then introduce bland diet")
        
        # Medication advice
        if db_matches:
            best_match = db_matches[0]
            if best_match["severity"] == "severe":
                actions.append("Do not delay professional treatment")
        
        # Environment modification
        if any(s.symptom in ["itching", "rash"] for s in analysis.symptoms):
            actions.append("Check for parasites and environmental irritants")
        
        actions.append("Keep detailed notes of symptoms, duration, and any triggers")
        
        return actions
    
    def _get_important_notes(self, analysis: AnalysisResult) -> List[str]:
        """Get important clinical notes"""
        notes = []
        
        # Patient-specific notes
        if analysis.patient_info.animal_type:
            notes.append(f"Species: {analysis.patient_info.animal_type}")
        
        # Symptom progression notes
        if analysis.symptoms:
            if any(s.severity == "severe" for s in analysis.symptoms):
                notes.append("Severe symptoms present - requires urgent evaluation")
            
            if any((s.duration and ("3" in s.duration or "4" in s.duration or "5" in s.duration))
                   for s in analysis.symptoms):
                notes.append("Symptoms lasting several days - may indicate systemic issue")
        
        # Multiple conditions
        if len(analysis.suspected_diseases) > 2:
            notes.append("Multiple conditions are possible - professional diagnosis is essential")
        
        return notes
    
    def _get_emergency_indicators(self, analysis: AnalysisResult) -> List[str]:
        """Get signs to watch for that need immediate veterinary care"""
        emergency_indicators = [
            "Severe difficulty breathing or gasping for air",
            "Unconsciousness or inability to stand",
            "Uncontrollable seizures or convulsions",
            "Severe bleeding or wound not stopping after 5-10 minutes",
            "Signs of extreme pain or distress",
            "Inability to urinate or defecate for more than 24 hours",
            "Severe abdominal swelling or pain",
            "Ingestion of toxic substances"
        ]
        return emergency_indicators
    
    def generate_report(self, analysis_result: Dict) -> str:
        """Generate a comprehensive report of the analysis"""
        lines = []
        
        # Header
        lines.append("\n" + "="*80)
        lines.append("VETERINARY AI ANALYSIS REPORT".center(80))
        lines.append("="*80)
        
        # Patient Information Section
        lines.append("\n[PATIENT INFORMATION]")
        patient = analysis_result["patient_analysis"].patient_info
        if patient.animal_type:
            lines.append(f"  Animal Type: {patient.animal_type.title()}")
        if patient.age:
            lines.append(f"  Age: {patient.age}")
        if patient.breed:
            lines.append(f"  Breed: {patient.breed.title()}")
        if patient.gender:
            lines.append(f"  Gender: {patient.gender.title()}")
        if patient.weight:
            lines.append(f"  Weight: {patient.weight}")
        
        # Symptoms Section
        lines.append("\n[EXTRACTED SYMPTOMS]")
        if analysis_result["patient_analysis"].symptoms:
            for symptom in analysis_result["patient_analysis"].symptoms:
                details = []
                if symptom.duration:
                    details.append(f"Duration: {symptom.duration}")
                if symptom.severity:
                    details.append(f"Severity: {symptom.severity}")
                if symptom.frequency:
                    details.append(f"Frequency: {symptom.frequency}")
                
                detail_str = f" ({', '.join(details)})" if details else ""
                lines.append(f"  • {symptom.symptom.replace('_', ' ').title()}{detail_str}")
        else:
            lines.append("  No symptoms extracted")
        
        # Database Matches Section
        lines.append("\n[POSSIBLE CONDITIONS (Database Match)]")
        if analysis_result["database_matches"]:
            for i, disease in enumerate(analysis_result["database_matches"][:3], 1):
                confidence = disease["confidence"] * 100
                lines.append(f"  {i}. {disease['name']}")
                lines.append(f"     Confidence: {confidence:.1f}%")
                lines.append(f"     Severity: {disease['severity'].title()}")
                lines.append(f"     Description: {disease['description']}")
                lines.append(f"     Treatment: {disease['treatment']}")
                lines.append("")
        else:
            lines.append("  No matching conditions found in database")
        
        # Recommendations Section
        recommendations = analysis_result["recommendations"]
        
        lines.append("\n[CLINICAL ASSESSMENT]")
        lines.append(f"  Urgency Level: {recommendations['urgency']}")
        
        lines.append("\n[RECOMMENDED ACTIONS]")
        for action in recommendations["recommended_actions"]:
            lines.append(f"  {action}")
        
        lines.append("\n[IMPORTANT NOTES]")
        for note in recommendations["important_notes"]:
            lines.append(f"  - {note}")
        
        lines.append("\n[EMERGENCY SIGNS - SEEK IMMEDIATE CARE IF]")
        for indicator in recommendations["when_to_seek_immediate_care"][:5]:
            lines.append(f"  * {indicator}")
        
        # Follow-up Questions Section
        lines.append("\n[FOLLOW-UP QUESTIONS FOR PATIENT]")
        if analysis_result["follow_up_questions"]:
            for i, q in enumerate(analysis_result["follow_up_questions"][:8], 1):
                lines.append(f"  {i}. {q.question}")
                lines.append(f"     (Category: {q.category.replace('_', ' ').title()})")
        else:
            lines.append("  No follow-up questions generated")
        
        # Footer
        lines.append("\n" + "="*80)
        lines.append("NOTE: This analysis is for informational purposes only and should not")
        lines.append("replace professional veterinary diagnosis and treatment.")
        lines.append("="*80 + "\n")
        
        return "\n".join(lines)
    
    def save_analysis(self, analysis_result: Dict, filename: str = "analysis_report.json"):
        """Save analysis result to JSON file"""
        serializable = {
            "patient_info": {
                "animal_type": analysis_result["patient_analysis"].patient_info.animal_type,
                "age": analysis_result["patient_analysis"].patient_info.age,
                "breed": analysis_result["patient_analysis"].patient_info.breed,
                "gender": analysis_result["patient_analysis"].patient_info.gender,
                "weight": analysis_result["patient_analysis"].patient_info.weight,
            },
            "symptoms": [
                {
                    "symptom": s.symptom,
                    "duration": s.duration,
                    "severity": s.severity,
                    "frequency": s.frequency,
                }
                for s in analysis_result["patient_analysis"].symptoms
            ],
            "database_matches": analysis_result["database_matches"],
            "recommendations": analysis_result["recommendations"],
            "questions_count": len(analysis_result["follow_up_questions"])
        }
        
        with open(filename, 'w') as f:
            json.dump(serializable, f, indent=2)
        
        print(f"Analysis saved to {filename}")
    
    def close(self):
        """Clean up resources"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def interactive_session():
    """Run an interactive analysis session"""
    print("\n" + "="*80)
    print("VETERINARY AI ASSISTANT - PATIENT ANALYSIS SYSTEM".center(80))
    print("="*80 + "\n")
    print("This system analyzes patient descriptions to extract disease and symptom")
    print("information, searches a veterinary database, and generates follow-up questions.\n")
    
    with VeterinaryAIAssistant() as assistant:
        while True:
            print("\nOptions:")
            print("  1. Analyze patient text")
            print("  2. View database diseases")
            print("  3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\nEnter patient description (type 'END' on a new line when finished):")
                lines = []
                while True:
                    line = input()
                    if line.upper() == "END":
                        break
                    lines.append(line)
                
                if lines:
                    patient_text = "\n".join(lines)
                    print("\nProcessing...")
                    
                    result = assistant.analyze_patient_text(patient_text)
                    report = assistant.generate_report(result)
                    print(report)
                    
                    # Ask if user wants to save
                    save = input("Save analysis to file? (y/n): ").strip().lower()
                    if save == 'y':
                        filename = input("Enter filename (default: analysis_report.json): ").strip()
                        if not filename:
                            filename = "analysis_report.json"
                        assistant.save_analysis(result, filename)
            
            elif choice == "2":
                print("\nDiseases in database:")
                diseases = assistant.db.get_all_diseases()
                for i, disease in enumerate(diseases[:10], 1):
                    print(f"  {i}. {disease.name}")
                    print(f"     Severity: {disease.severity}")
                    print(f"     Common symptoms: {', '.join(disease.common_symptoms[:3])}")
            
            elif choice == "3":
                print("\nGoodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode - analyze provided text
        patient_text = " ".join(sys.argv[1:])
        
        with VeterinaryAIAssistant() as assistant:
            result = assistant.analyze_patient_text(patient_text)
            print(assistant.generate_report(result))
    else:
        # Interactive mode
        interactive_session()

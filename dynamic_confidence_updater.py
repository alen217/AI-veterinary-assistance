"""
Dynamic Disease Confidence Updater
Updates disease priorities based on follow-up question answers
Implements feedback loop for continuous refinement
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
import re
import json


@dataclass
class FollowUpAnswer:
    """User's answer to a follow-up question"""
    question: str
    answer: str
    category: str
    related_disease: str = None
    symptom_to_check: str = None
    symptom_confirmed: bool = False
    symptom_ruled_out: bool = False
    mentioned_symptom: str = None
    severity_level: str = None


class DynamicDiseaseRanker:
    """
    Dynamically updates disease confidence based on follow-up answers
    Implements Bayesian-like updating of probabilities
    """
    
    def __init__(self, initial_diseases: List[Dict]):
        """
        Initialize with initial disease matches
        
        Args:
            initial_diseases: List of diseases with initial confidence scores
        """
        self.diseases = {d['name']: d for d in initial_diseases}
        self.answer_history = []
        
    def update_confidence_with_answer(
        self, 
        answer: FollowUpAnswer
    ) -> List[Dict]:
        """
        Update disease confidences based on a follow-up answer
        
        Args:
            answer: The user's answer to a follow-up question
            
        Returns:
            Updated list of diseases sorted by new confidence
        """
        self.answer_history.append(answer)
        
        # Process answer based on type
        if answer.category == "disease_confirmation":
            self._update_for_disease_confirmation(answer)
        elif answer.category == "symptom_details":
            self._update_for_symptom_details(answer)
        elif answer.category == "risk_factors":
            self._update_for_risk_factors(answer)
        
        # Return updated sorted list
        return self.get_ranked_diseases()
    
    def _update_for_disease_confirmation(self, answer: FollowUpAnswer):
        """Update when checking for specific disease symptoms"""
        # Use symptom_confirmed/ruled_out from answer if available
        answer_lower = answer.answer.lower()
        inferred_positive, inferred_negative = self._classify_yes_no(answer_lower)
        is_positive = answer.symptom_confirmed or inferred_positive
        is_negative = answer.symptom_ruled_out or inferred_negative
        
        # Get the symptom being checked
        symptom_checked = answer.symptom_to_check or answer.mentioned_symptom
        
        # Update all diseases that have this symptom
        for disease_name, disease in self.diseases.items():
            disease_symptoms = disease.get('common_symptoms', [])
            
            if symptom_checked and symptom_checked in disease_symptoms:
                current_conf = disease.get('confidence', 0.5)
                
                # Negative evidence should override accidental positive token hits.
                if is_negative:
                    # Symptom NOT present - REDUCE confidence
                    penalty = 0.10  # 10% penalty
                    new_conf = max(0.0, current_conf - penalty)
                    disease['confidence'] = new_conf
                    print(f"[DOWN] Reduced {disease['name']} confidence: {current_conf:.2f} -> {new_conf:.2f}")

                elif is_positive:
                    # Symptom confirmed - BOOST confidence significantly
                    boost = 0.15  # 15% boost
                    new_conf = min(1.0, current_conf + boost)
                    disease['confidence'] = new_conf
                    disease['matched_additional_symptoms'] = disease.get('matched_additional_symptoms', [])
                    if symptom_checked not in disease['matched_additional_symptoms']:
                        disease['matched_additional_symptoms'].append(symptom_checked)
                    print(f"[UP] Boosted {disease['name']} confidence: {current_conf:.2f} -> {new_conf:.2f}")

    @staticmethod
    def _classify_yes_no(answer_lower: str) -> Tuple[bool, bool]:
        """
        Return (is_positive, is_negative) from free-text answers.
        Uses word boundaries to avoid false positives such as matching 'has' in 'hasn't'.
        """
        negative_patterns = [
            r"\bno\b",
            r"\bnot\b",
            r"\bnever\b",
            r"\bnone\b",
            r"\bwithout\b",
            r"\bhasn['’]?t\b",
            r"\bhaven['’]?t\b",
            r"\bdoesn['’]?t\b",
            r"\bdidn['’]?t\b",
            r"\bisn['’]?t\b",
            r"\baren['’]?t\b",
        ]
        positive_patterns = [
            r"\byes\b",
            r"\byep\b",
            r"\byeah\b",
            r"\bpresent\b",
            r"\bshowing\b",
            r"\bexperiencing\b",
            r"\bhas\b",
            r"\bhave\b",
        ]

        is_negative = any(re.search(pattern, answer_lower) for pattern in negative_patterns)
        is_positive = any(re.search(pattern, answer_lower) for pattern in positive_patterns)
        return is_positive, is_negative
    
    def _update_for_symptom_details(self, answer: FollowUpAnswer):
        """Update based on symptom severity/duration details"""
        answer_lower = answer.answer.lower()
        
        # Severity indicators
        if 'severe' in answer_lower or 'critical' in answer_lower or 'extreme' in answer_lower:
            # Boost severe diseases
            for name, disease in self.diseases.items():
                if disease.get('severity') == 'severe':
                    current_conf = disease['confidence']
                    disease['confidence'] = min(1.0, current_conf + 0.10)
                    print(f"[SEVERE] Boosted severe disease {name}: {current_conf:.2f} -> {disease['confidence']:.2f}")
        
        # Duration indicators
        if any(word in answer_lower for word in ['chronic', 'weeks', 'months', 'long time']):
            # Boost chronic conditions
            for name, disease in self.diseases.items():
                if 'chronic' in disease.get('description', '').lower():
                    current_conf = disease['confidence']
                    disease['confidence'] = min(1.0, current_conf + 0.08)
        
        elif any(word in answer_lower for word in ['acute', 'sudden', 'today', 'yesterday', 'hours']):
            # Boost acute conditions
            for name, disease in self.diseases.items():
                if 'acute' in disease.get('description', '').lower():
                    current_conf = disease['confidence']
                    disease['confidence'] = min(1.0, current_conf + 0.08)
    
    def _update_for_risk_factors(self, answer: FollowUpAnswer):
        """Update based on risk factor exposure"""
        if not answer.related_disease or answer.related_disease not in self.diseases:
            return
        
        disease = self.diseases[answer.related_disease]
        current_conf = disease['confidence']
        
        answer_lower = answer.answer.lower()
        is_exposed = any(word in answer_lower for word in ['yes', 'exposed', 'contact', 'around'])
        
        if is_exposed:
            # Confirmed exposure - boost confidence
            boost = 0.12
            disease['confidence'] = min(1.0, current_conf + boost)
            print(f"[RISK] Risk factor confirmed for {disease['name']}: {current_conf:.2f} -> {disease['confidence']:.2f}")
    
    def get_ranked_diseases(self) -> List[Dict]:
        """Get diseases sorted by current confidence"""
        disease_list = list(self.diseases.values())
        disease_list.sort(key=lambda d: d['confidence'], reverse=True)
        return disease_list
    
    def get_confidence_changes(self) -> Dict[str, Tuple[float, float]]:
        """Get confidence changes for all diseases (initial → current)"""
        changes = {}
        for name, disease in self.diseases.items():
            # Assume we stored initial confidence somewhere
            initial = disease.get('initial_confidence', disease['confidence'])
            current = disease['confidence']
            if initial != current:
                changes[name] = (initial, current)
        return changes
    
    def explain_ranking(self) -> str:
        """Explain why diseases are ranked the way they are"""
        output = []
        output.append("\n" + "="*70)
        output.append("DYNAMIC DISEASE RANKING EXPLANATION")
        output.append("="*70 + "\n")
        
        for i, disease in enumerate(self.get_ranked_diseases()[:5], 1):
            output.append(f"{i}. {disease['name']}")
            output.append(f"   Current Confidence: {disease['confidence']:.1%}")
            output.append(f"   Symptom Matches: {disease.get('symptom_match_count', 0)}")
            
            # Additional symptoms found
            additional = disease.get('matched_additional_symptoms', [])
            if additional:
                output.append(f"   Additional Symptoms Confirmed: {', '.join(additional)}")
            
            output.append("")
        
        # Show answer history impact
        if self.answer_history:
            output.append("\n📊 Follow-Up Answer Impact:")
            for i, ans in enumerate(self.answer_history, 1):
                output.append(f"   {i}. Q: {ans.question[:60]}...")
                output.append(f"      A: {ans.answer[:50]}")
                if ans.related_disease:
                    output.append(f"      → Updated confidence for {ans.related_disease}")
                output.append("")
        
        output.append("="*70)
        return "\n".join(output)


class AdaptiveQuestionGenerator:
    """
    Generates next questions based on current disease rankings
    Focuses on questions that will have highest discriminatory power
    """
    
    def __init__(self, disease_ranker: DynamicDiseaseRanker, disease_repo):
        self.ranker = disease_ranker
        self.disease_repo = disease_repo
    
    def get_next_best_questions(
        self, 
        patient_symptoms: List[str],
        max_questions: int = 3
    ) -> List[Dict]:
        """
        Generate questions that will most help discriminate between top diseases
        
        Returns questions with highest information gain potential
        """
        top_diseases = self.ranker.get_ranked_diseases()[:5]
        questions = []
        
        # For each top disease, find discriminating symptoms
        for disease in top_diseases:
            disease_data = self.disease_repo.find_by_name(disease['name'])
            if not disease_data:
                continue
            
            disease_symptoms = set(disease_data.get('common_symptoms', []))
            patient_symptom_set = set(patient_symptoms)
            
            # Find symptoms that would confirm/rule out this disease
            missing_symptoms = disease_symptoms - patient_symptom_set
            
            for symptom in list(missing_symptoms)[:2]:
                questions.append({
                    'question': f"Has the patient shown any {symptom.replace('_', ' ')}?",
                    'priority': 5,
                    'reasoning': f"Would strongly indicate or rule out {disease['name']}",
                    'category': 'disease_confirmation',
                    'related_disease': disease['name'],
                    'symptom_to_check': symptom
                })
        
        # Sort by priority and return top N
        questions.sort(key=lambda q: q['priority'], reverse=True)
        return questions[:max_questions]


# Example usage
if __name__ == "__main__":
    # Simulate initial disease matches
    initial_diseases = [
        {
            'name': 'Gastroenteritis',
            'confidence': 0.75,
            'symptom_match_count': 3,
            'severity': 'moderate',
            'initial_confidence': 0.75
        },
        {
            'name': 'Pancreatitis',
            'confidence': 0.65,
            'symptom_match_count': 2,
            'severity': 'severe',
            'initial_confidence': 0.65
        },
        {
            'name': 'Food Poisoning',
            'confidence': 0.55,
            'symptom_match_count': 2,
            'severity': 'mild',
            'initial_confidence': 0.55
        }
    ]
    
    # Create ranker
    ranker = DynamicDiseaseRanker(initial_diseases)
    
    print("Initial Rankings:")
    for d in ranker.get_ranked_diseases():
        print(f"  {d['name']}: {d['confidence']:.1%}")
    
    # Simulate follow-up answers
    print("\n" + "="*70)
    print("Simulating Follow-Up Question Answers")
    print("="*70 + "\n")
    
    # Answer 1: Confirming symptom for top disease
    answer1 = FollowUpAnswer(
        question="Has your dog shown any loss of appetite?",
        answer="Yes, not eating at all",
        category="disease_confirmation",
        related_disease="Gastroenteritis",
        symptom_to_check="loss_of_appetite"
    )
    
    print("Q1: Has your dog shown any loss of appetite?")
    print("A1: Yes, not eating at all")
    ranker.update_confidence_with_answer(answer1)
    
    # Answer 2: Symptom severity
    answer2 = FollowUpAnswer(
        question="How severe is the vomiting?",
        answer="Very severe, constant vomiting",
        category="symptom_details",
        related_disease="Pancreatitis"
    )
    
    print("\nQ2: How severe is the vomiting?")
    print("A2: Very severe, constant vomiting")
    ranker.update_confidence_with_answer(answer2)
    
    # Answer 3: Negative confirmation
    answer3 = FollowUpAnswer(
        question="Has your dog eaten any spoiled food?",
        answer="No, regular diet",
        category="disease_confirmation",
        related_disease="Food Poisoning",
        symptom_to_check="dietary_indiscretion"
    )
    
    print("\nQ3: Has your dog eaten any spoiled food?")
    print("A3: No, regular diet")
    ranker.update_confidence_with_answer(answer3)
    
    # Show updated rankings
    print("\n" + "="*70)
    print("Updated Rankings After Follow-Up:")
    print("="*70)
    for d in ranker.get_ranked_diseases():
        print(f"  {d['name']}: {d['confidence']:.1%}")
    
    # Show explanation
    print(ranker.explain_ranking())

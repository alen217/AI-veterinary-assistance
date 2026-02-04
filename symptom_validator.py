"""
Official Symptom List Validator
Prevents hallucination by constraining symptom extraction to database symptoms only
Implements AVA paper methodology for symptom validation
"""
from typing import List, Set, Tuple
from difflib import get_close_matches


class SymptomValidator:
    """
    Validates extracted symptoms against official database symptom list
    Helps prevent hallucination as per AVA paper approach
    """
    
    def __init__(self, database_repo):
        self.repo = database_repo
        self._official_symptoms = None
        self._load_official_symptoms()
    
    def _load_official_symptoms(self):
        """Load all unique symptoms from database as official list"""
        try:
            db = self.repo.db
            all_diseases = db.diseases.find({}, {"common_symptoms": 1})
            
            symptoms_set = set()
            for disease in all_diseases:
                symptoms = disease.get("common_symptoms", [])
                symptoms_set.update(symptoms)
            
            self._official_symptoms = list(symptoms_set)
            print(f"✅ Loaded {len(self._official_symptoms)} official symptoms from database")
        except Exception as e:
            print(f"⚠️ Could not load official symptoms: {e}")
            self._official_symptoms = []
    
    @property
    def official_symptoms(self) -> List[str]:
        """Get the official symptom list"""
        if self._official_symptoms is None:
            self._load_official_symptoms()
        return self._official_symptoms
    
    def validate_symptom(self, symptom: str, threshold: float = 0.8) -> Tuple[bool, str, float]:
        """
        Validate a single symptom against official list
        
        Returns:
            (is_valid, matched_symptom, similarity_score)
        """
        symptom_lower = symptom.lower().strip()
        
        # Exact match
        for official in self.official_symptoms:
            if official.lower() == symptom_lower:
                return True, official, 1.0
        
        # Fuzzy match
        matches = get_close_matches(
            symptom_lower,
            [s.lower() for s in self.official_symptoms],
            n=1,
            cutoff=threshold
        )
        
        if matches:
            matched_lower = matches[0]
            # Find original casing
            for official in self.official_symptoms:
                if official.lower() == matched_lower:
                    similarity = self._calculate_similarity(symptom_lower, matched_lower)
                    return True, official, similarity
        
        return False, symptom, 0.0
    
    def validate_symptoms(self, symptoms: List[str]) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
        """
        Validate multiple symptoms
        
        Returns:
            (valid_symptoms, invalid_symptoms, corrections)
            corrections = [(original, corrected)]
        """
        valid = []
        invalid = []
        corrections = []
        
        for symptom in symptoms:
            is_valid, matched, score = self.validate_symptom(symptom)
            
            if is_valid:
                valid.append(matched)
                if matched.lower() != symptom.lower():
                    corrections.append((symptom, matched))
            else:
                invalid.append(symptom)
        
        # Remove duplicates while preserving order
        valid = list(dict.fromkeys(valid))
        
        return valid, invalid, corrections
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity score"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio()
    
    def suggest_symptoms(self, partial: str, limit: int = 5) -> List[str]:
        """
        Suggest official symptoms based on partial input
        Useful for autocomplete functionality
        """
        partial_lower = partial.lower().strip()
        
        if len(partial_lower) < 2:
            return []
        
        # Find symptoms containing the partial string
        matches = [
            s for s in self.official_symptoms
            if partial_lower in s.lower()
        ]
        
        # If no substring matches, use fuzzy matching
        if not matches:
            matches = get_close_matches(
                partial_lower,
                [s.lower() for s in self.official_symptoms],
                n=limit,
                cutoff=0.6
            )
            # Convert back to original casing
            matches = [
                official for official in self.official_symptoms
                if official.lower() in matches
            ]
        
        return matches[:limit]
    
    def get_symptom_statistics(self) -> dict:
        """Get statistics about official symptom list"""
        return {
            'total_symptoms': len(self.official_symptoms),
            'symptom_list': self.official_symptoms[:20],  # First 20 for preview
            'sample_symptoms': sorted(self.official_symptoms)[:10]
        }

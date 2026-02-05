from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class MongoDiseaseRepository:
    def __init__(self):
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            raise RuntimeError("MONGO_URL not set")

        self.client = MongoClient(mongo_url)
        self.db = self.client[os.getenv("MONGO_DB_NAME", "veterinary_ai_db")]
        self.collection = self.db.diseases

    def find_by_symptoms(self, symptoms: list[str], limit: int = 50, species: str = None) -> list[dict]:
        """
        Find diseases that match given symptoms with AVA-style confidence scoring.
        
        Scoring methodology (based on AVA paper):
        - Primary: Match count (number of matched symptoms)
        - Secondary: Match ratio (matched/total disease symptoms) for tie-breaking
        - Bonus: Patient coverage and severity adjustments
        - Species filtering to show only relevant diseases
        """
        # Build query with species filter
        query = {"common_symptoms": {"$in": symptoms}}
        if species:
            # Filter by species (case-insensitive) - match any of the common variations
            query["affected_species"] = {
                "$in": [species, species.lower(), species.upper(), species.capitalize()]
            }
        
        cursor = self.collection.find(query)

        diseases = []
        for d in cursor:
            disease_symptoms = set(d.get("common_symptoms", []))
            patient_symptoms = set(symptoms)
            
            # Calculate overlap
            matched_symptoms = patient_symptoms & disease_symptoms
            match_count = len(matched_symptoms)
            
            # Only add diseases that actually have symptom matches
            if match_count == 0:
                continue
            
            # AVA Paper Metric: Match Ratio = matched / total_disease_symptoms
            # This is used as tie-breaker when match counts are equal
            if len(disease_symptoms) > 0:
                match_ratio = match_count / len(disease_symptoms)
            else:
                match_ratio = 0.0
            
            # Base score: What percentage of patient symptoms match this disease?
            if len(patient_symptoms) > 0:
                patient_coverage = match_count / len(patient_symptoms)
            else:
                patient_coverage = 0.0
            
            # Combined confidence score (weighted average)
            # When patient and disease symptoms match perfectly, should be near 100%
            # Prioritize: match count, then coverage, then ratio
            normalized_match_count = min(1.0, match_count / 8.0)  # Normalize to 0-1 (max 8 symptoms)
            
            # Perfect match bonus: if all patient symptoms match AND all disease symptoms match
            perfect_match = (patient_coverage == 1.0 and match_ratio == 1.0)
            
            if perfect_match:
                # Perfect match gets very high confidence
                confidence_score = 0.95
            else:
                # Weighted scoring
                confidence_score = (
                    0.45 * normalized_match_count +  # 45% weight on match count
                    0.40 * patient_coverage +         # 40% weight on patient coverage  
                    0.15 * match_ratio                # 15% weight on match ratio
                )
            
            # Severity bonus: increase confidence for severe diseases with many matches
            severity = d.get("severity", "moderate")
            if severity == "severe" and match_count >= 3:
                confidence_score = min(1.0, confidence_score * 1.20)  # 20% boost
            elif severity == "severe" and match_count >= 2:
                confidence_score = min(1.0, confidence_score * 1.10)  # 10% boost
            
            # Store all metrics for AVA display
            d["symptom_match_count"] = match_count
            d["match_ratio"] = round(match_ratio, 3)  # AVA metric
            d["match_score"] = round(confidence_score, 3)
            d["confidence"] = round(confidence_score, 3)
            d["patient_coverage"] = round(patient_coverage, 3)
            d["matched_symptoms"] = list(matched_symptoms)
            
            diseases.append(d)

        # Sort by confidence score (which already incorporates match count priority)
        diseases.sort(key=lambda x: (x["confidence"], x["symptom_match_count"]), reverse=True)
        
        # Apply limit after sorting
        if limit and limit > 0:
            return diseases[:limit]
        return diseases
    
    def find_by_name(self, name: str) -> dict | None:
        if not name:
            return None

        return self.collection.find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"_id": 0}
    )


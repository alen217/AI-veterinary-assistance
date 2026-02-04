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

    def find_by_symptoms(self, symptoms: list[str], limit: int = 5, species: str = None) -> list[dict]:
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
            # Filter by species (case-insensitive)
            query["affected_species"] = {"$regex": f"^{species}$", "$options": "i"}
        
        cursor = self.collection.find(query)

        diseases = []
        for d in cursor:
            disease_symptoms = set(d.get("common_symptoms", []))
            patient_symptoms = set(symptoms)
            
            # Calculate overlap
            matched_symptoms = patient_symptoms & disease_symptoms
            match_count = len(matched_symptoms)
            
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
            # Patient coverage is more important (70%) than match ratio (30%)
            confidence_score = (0.7 * patient_coverage) + (0.3 * match_ratio)
            
            # Severity bonus: increase confidence for severe diseases with many matches
            severity = d.get("severity", "moderate")
            if severity == "severe" and match_count >= 2:
                confidence_score = min(1.0, confidence_score * 1.15)
            
            # Store all metrics for AVA display
            d["symptom_match_count"] = match_count
            d["match_ratio"] = round(match_ratio, 3)  # AVA metric
            d["match_score"] = round(confidence_score, 3)
            d["confidence"] = round(confidence_score, 3)
            d["patient_coverage"] = round(patient_coverage, 3)
            
            # Only add diseases that actually have symptom matches
            if match_count > 0:
                diseases.append(d)

        # Sort by match count first (primary), then match ratio (secondary) - AVA methodology
        diseases.sort(key=lambda x: (x["symptom_match_count"], x["match_ratio"]), reverse=True)
        return diseases[:limit]
    
    def find_by_name(self, name: str) -> dict | None:
        if not name:
            return None

        return self.collection.find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"_id": 0}
    )


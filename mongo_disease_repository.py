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

    def find_by_symptoms(
        self,
        symptoms: list[str],
        limit: int = 5,
        species: str | None = None,
    ) -> list[dict]:
        """
        Find diseases that match given symptoms with proper confidence scoring.
        
        Scoring methodology:
        - Base score: percentage of patient symptoms that match disease symptoms
        - Bonus: additional disease symptoms present increase confidence
        - Penalty: severity mismatch reduces confidence
        """
        species_filter = self._normalize_species(species)
        cursor = self.collection.find(
            {"common_symptoms": {"$in": symptoms}}
        )

        diseases = []
        for d in cursor:
            if species_filter and not self._disease_matches_species(d, species_filter):
                continue

            disease_symptoms = set(d.get("common_symptoms", []))
            patient_symptoms = set(symptoms)
            
            # Calculate overlap
            matched_symptoms = patient_symptoms & disease_symptoms
            match_count = len(matched_symptoms)
            
            # Base score: What percentage of patient symptoms match this disease?
            if len(patient_symptoms) > 0:
                patient_coverage = match_count / len(patient_symptoms)
            else:
                patient_coverage = 0.0
            
            # Bonus: What percentage of disease symptoms are present?
            if len(disease_symptoms) > 0:
                disease_coverage = match_count / len(disease_symptoms)
            else:
                disease_coverage = 0.0
            
            # Combined confidence score (weighted average)
            # Patient coverage is more important (70%) than disease coverage (30%)
            confidence_score = (0.7 * patient_coverage) + (0.3 * disease_coverage)
            
            # Severity bonus: increase confidence for severe diseases with many matches
            severity = d.get("severity", "moderate")
            if severity == "severe" and match_count >= 2:
                confidence_score = min(1.0, confidence_score * 1.15)
            
            d["symptom_match_count"] = match_count
            d["match_score"] = round(confidence_score, 3)
            d["confidence"] = round(confidence_score, 3)
            diseases.append(d)

        # Sort by confidence score first, then by match count
        diseases.sort(key=lambda x: (x["match_score"], x["symptom_match_count"]), reverse=True)
        return diseases[:limit]

    @staticmethod
    def _normalize_species(species: str | None) -> str | None:
        if not species:
            return None
        return str(species).strip().lower()

    @classmethod
    def _species_aliases(cls, species: str) -> set[str]:
        alias_map = {
            "dog": {"dog", "dogs", "canine", "canines"},
            "cat": {"cat", "cats", "feline", "felines"},
            "bird": {"bird", "birds", "avian"},
            "rabbit": {"rabbit", "rabbits", "bunny", "bunnies"},
            "horse": {"horse", "horses", "equine", "equines"},
            "cow": {"cow", "cows", "cattle", "bovine"},
            "goat": {"goat", "goats", "caprine"},
        }
        aliases = alias_map.get(species, {species})
        return {cls._canonical_species_token(a) for a in aliases if a}

    @staticmethod
    def _canonical_species_token(value: str) -> str:
        return str(value).strip().lower().replace("_", " ").replace("-", " ")

    @classmethod
    def _disease_matches_species(cls, disease_doc: dict, species_filter: str) -> bool:
        """
        Strict species filtering:
        - if species is known (e.g., cat), only include diseases that explicitly list that species
          (or a generic all-species marker).
        """
        raw = disease_doc.get("affected_species")

        if isinstance(raw, list):
            disease_species = [cls._canonical_species_token(s) for s in raw if s]
        elif isinstance(raw, str) and raw.strip():
            disease_species = [cls._canonical_species_token(raw)]
        else:
            disease_species = []

        if not disease_species:
            return False

        generic_markers = {
            "all",
            "all species",
            "all animals",
            "any",
            "any species",
            "multiple species",
            "multispecies",
            "general",
        }
        if any(marker in generic_markers for marker in disease_species):
            return True

        species_aliases = cls._species_aliases(species_filter)
        disease_species_set = set(disease_species)
        return bool(species_aliases & disease_species_set)
    
    def find_by_name(self, name: str) -> dict | None:
        if not name:
            return None

        return self.collection.find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"_id": 0}
    )


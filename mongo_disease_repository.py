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

    def find_by_symptoms(self, symptoms: list[str], limit: int = 5) -> list[dict]:
        """
        Find diseases that match given symptoms.
        """
        cursor = self.collection.find(
            {"common_symptoms": {"$in": symptoms}}
        )

        diseases = []
        for d in cursor:
            match_count = len(set(symptoms) & set(d.get("common_symptoms", [])))
            d["symptom_match_count"] = match_count
            diseases.append(d)

        diseases.sort(key=lambda x: x["symptom_match_count"], reverse=True)
        return diseases[:limit]

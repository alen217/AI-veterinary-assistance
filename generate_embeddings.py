"""
Generate semantic embeddings for diseases and store them in `diseases_vector`.

Usage:
  python generate_embeddings.py
  python generate_embeddings.py --limit 200
  python generate_embeddings.py --overwrite
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Dict, Any

from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

import os


def build_profile_text(doc: Dict[str, Any]) -> str:
    name = str(doc.get("name", ""))
    description = str(doc.get("description", ""))
    common_symptoms = ", ".join(str(s).replace("_", " ") for s in (doc.get("common_symptoms") or []))
    causes = ", ".join(str(c) for c in (doc.get("causes") or []))
    parts = [name, description, f"Symptoms: {common_symptoms}", f"Causes: {causes}"]
    return " | ".join(part for part in parts if part.strip())


def main():
    load_dotenv(find_dotenv())
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("MONGO_DB_NAME", "veterinary_ai_db")

    if not mongo_url:
        raise RuntimeError("MONGO_URL not set in environment.")
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers is not installed. Install with: pip install sentence-transformers")

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Number of diseases to process (0 = all)")
    parser.add_argument("--overwrite", action="store_true", help="Recompute even when embedding already exists")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    args = parser.parse_args()

    client = MongoClient(mongo_url)
    db = client[db_name]
    diseases = db["diseases"]
    vector_collection = db["diseases_vector"]

    model = SentenceTransformer(args.model)

    query = {}
    cursor = diseases.find(
        query,
        {
            "_id": 1,
            "name": 1,
            "description": 1,
            "common_symptoms": 1,
            "causes": 1,
            "category": 1,
            "severity": 1,
            "affected_species": 1,
        },
    )
    if args.limit and args.limit > 0:
        cursor = cursor.limit(args.limit)

    processed = 0
    skipped = 0
    for doc in cursor:
        name = doc.get("name")
        if not name:
            skipped += 1
            continue

        if not args.overwrite:
            exists = vector_collection.find_one(
                {"name": name, "embedding": {"$exists": True}},
                {"_id": 1},
            )
            if exists:
                skipped += 1
                continue

        profile_text = build_profile_text(doc)
        if not profile_text.strip():
            skipped += 1
            continue

        embedding = model.encode(profile_text).tolist()
        vector_doc = {
            "name": name,
            "disease_id": str(doc["_id"]),
            "profile_text": profile_text,
            "common_symptoms": doc.get("common_symptoms") or [],
            "category": doc.get("category"),
            "severity": doc.get("severity"),
            "affected_species": doc.get("affected_species") or [],
            "embedding": embedding,
            "embedding_model": args.model,
            "updated_at": datetime.now(timezone.utc),
        }
        vector_collection.update_one(
            {"name": name},
            {"$set": vector_doc},
            upsert=True,
        )
        processed += 1

    print(f"Embedding generation complete. processed={processed}, skipped={skipped}")


if __name__ == "__main__":
    main()

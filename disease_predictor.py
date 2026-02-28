"""
Semantic disease predictor for differential diagnosis support.

This module is intentionally independent from the existing diagnosis pipeline.
It can be used as an optional feature in Streamlit without changing the
behavior of current NLP + scoring flows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math
import re

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


def _normalize_text(value: str) -> str:
    return str(value or "").strip().lower()


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", _normalize_text(value)))


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    denom = float(np.linalg.norm(vec1) * np.linalg.norm(vec2))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(vec1, vec2) / denom)


@dataclass
class PredictionMeta:
    engine_mode: str
    category_hint: Optional[str]
    used_candidates: int


class DiseasePredictor:
    """Optional semantic predictor with graceful lexical fallback."""

    PRIORITY_KEYWORDS = (
        "inability",
        "complete",
        "no urine",
        "blockage",
        "severe",
        "pain",
        "distension",
        "collapse",
        "bloody",
        "straining",
    )

    SPECIES_ALIASES: Dict[str, set[str]] = {
        "dog": {"dog", "dogs", "canine", "canines"},
        "cat": {"cat", "cats", "feline", "felines"},
        "bird": {"bird", "birds", "avian"},
        "rabbit": {"rabbit", "rabbits", "bunny", "bunnies"},
        "horse": {"horse", "horses", "equine", "equines"},
        "cow": {"cow", "cows", "cattle", "bovine"},
        "goat": {"goat", "goats", "caprine"},
    }

    def __init__(self, db: Any, embedding_model_name: str = "all-MiniLM-L6-v2"):
        self.db = db
        self.disease_collection = db["diseases"]
        self.vector_collection = db["diseases_vector"]
        self.embedding_model_name = embedding_model_name
        self._encoder = None
        self._encoder_error: Optional[str] = None
        self._index: List[Dict[str, Any]] = []
        self._index_built = False

    def _load_encoder(self):
        if self._encoder is not None or self._encoder_error is not None:
            return
        if SentenceTransformer is None:
            self._encoder_error = "sentence-transformers not installed"
            return
        try:
            self._encoder = SentenceTransformer(self.embedding_model_name)
        except Exception as exc:
            self._encoder_error = str(exc)

    def _infer_category(self, symptom_text: str) -> Optional[str]:
        text = _normalize_text(symptom_text)
        if any(word in text for word in ("urine", "urinate", "pee", "bladder")):
            return "urinary"
        if any(word in text for word in ("vomit", "diarrhea", "stomach", "abdomen")):
            return "gastrointestinal"
        if any(word in text for word in ("cough", "breathing", "lungs", "respiratory")):
            return "respiratory"
        if any(word in text for word in ("itch", "skin", "rash", "hair loss")):
            return "dermatological"
        return None

    @staticmethod
    def _build_profile_text(doc: Dict[str, Any]) -> str:
        name = str(doc.get("name", ""))
        description = str(doc.get("description", ""))
        symptoms = ", ".join(str(s).replace("_", " ") for s in (doc.get("common_symptoms") or []))
        causes = ", ".join(str(c) for c in (doc.get("causes") or []))
        return " | ".join(
            part for part in (name, description, f"Symptoms: {symptoms}", f"Causes: {causes}") if part.strip()
        )

    @classmethod
    def _species_match(cls, doc: Dict[str, Any], species: Optional[str]) -> bool:
        if not species:
            return True
        species_key = _normalize_text(species)
        aliases = cls.SPECIES_ALIASES.get(species_key, {species_key})
        raw = doc.get("affected_species") or []
        if isinstance(raw, str):
            raw = [raw]
        disease_species = {_normalize_text(s).replace("-", " ").replace("_", " ") for s in raw if s}
        if not disease_species:
            return False
        generic = {
            "all",
            "all species",
            "all animals",
            "any",
            "any species",
            "multiple species",
            "multispecies",
            "general",
        }
        if disease_species & generic:
            return True
        return bool(disease_species & aliases)

    @staticmethod
    def _matched_symptoms(symptom_text: str, common_symptoms: List[str]) -> List[str]:
        text_lc = _normalize_text(symptom_text)
        matched: List[str] = []
        for symptom in common_symptoms or []:
            cleaned = str(symptom).replace("_", " ").lower().strip()
            if cleaned and cleaned in text_lc:
                matched.append(cleaned)
        return matched

    def _build_index(self):
        if self._index_built:
            return

        self._load_encoder()
        index: List[Dict[str, Any]] = []

        try:
            vector_docs = list(
                self.vector_collection.find(
                    {},
                    {
                        "_id": 0,
                        "name": 1,
                        "embedding": 1,
                        "common_symptoms": 1,
                        "affected_species": 1,
                        "category": 1,
                        "severity": 1,
                        "profile_text": 1,
                    },
                )
            )
        except Exception:
            vector_docs = []

        if vector_docs:
            for doc in vector_docs:
                embedding = doc.get("embedding")
                if not embedding:
                    continue
                doc_copy = dict(doc)
                doc_copy["_embedding"] = np.array(embedding, dtype=float)
                doc_copy["_profile_tokens"] = _tokens(doc.get("profile_text", ""))
                index.append(doc_copy)

        if not index:
            diseases = list(
                self.disease_collection.find(
                    {},
                    {
                        "_id": 0,
                        "name": 1,
                        "description": 1,
                        "common_symptoms": 1,
                        "affected_species": 1,
                        "category": 1,
                        "severity": 1,
                        "causes": 1,
                    },
                )
            )
            for doc in diseases:
                profile_text = self._build_profile_text(doc)
                row = dict(doc)
                row["profile_text"] = profile_text
                row["_profile_tokens"] = _tokens(profile_text)
                if self._encoder is not None:
                    row["_embedding"] = np.array(self._encoder.encode(profile_text), dtype=float)
                else:
                    row["_embedding"] = None
                index.append(row)

        self._index = index
        self._index_built = True

    def _semantic_score(
        self,
        query_text: str,
        query_tokens: set[str],
        query_embedding: Optional[np.ndarray],
        disease: Dict[str, Any],
    ) -> float:
        disease_embedding = disease.get("_embedding")
        if query_embedding is not None and disease_embedding is not None:
            return _cosine_similarity(query_embedding, disease_embedding)

        disease_tokens = disease.get("_profile_tokens") or set()
        if not disease_tokens:
            return 0.0
        intersect = len(query_tokens & disease_tokens)
        union = len(query_tokens | disease_tokens)
        if union == 0:
            return 0.0
        return float(intersect / union)

    def predict_disease(
        self,
        symptom_text: str,
        species: Optional[str] = None,
        top_k: int = 5,
        return_meta: bool = False,
    ) -> Any:
        self._build_index()
        if not self._index:
            if return_meta:
                return [], PredictionMeta(engine_mode="unavailable", category_hint=None, used_candidates=0)
            return []

        category_hint = self._infer_category(symptom_text)
        query_tokens = _tokens(symptom_text)
        query_embedding: Optional[np.ndarray] = None

        if self._encoder is not None:
            query_embedding = np.array(self._encoder.encode(symptom_text), dtype=float)
            engine_mode = "semantic-embeddings"
        else:
            engine_mode = "lexical-fallback"

        results: List[Dict[str, Any]] = []
        for disease in self._index:
            semantic = self._semantic_score(symptom_text, query_tokens, query_embedding, disease)
            symptoms = disease.get("common_symptoms") or []
            matched_symptoms = self._matched_symptoms(symptom_text, symptoms)
            overlap_ratio = (
                len(matched_symptoms) / len(symptoms)
                if symptoms
                else 0.0
            )

            score = (0.75 * semantic) + (0.25 * overlap_ratio) + (0.06 * len(matched_symptoms))

            species_ok = self._species_match(disease, species)
            if species:
                score += 0.05 if species_ok else -0.08

            disease_category = _normalize_text(disease.get("category"))
            if category_hint and disease_category:
                if category_hint in disease_category:
                    score += 0.03
                else:
                    score -= 0.02

            reasons: List[str] = [
                f"Semantic similarity: {semantic:.2f}",
                f"Symptom overlap: {len(matched_symptoms)} matched",
            ]
            if matched_symptoms:
                reasons.append("Matched symptoms: " + ", ".join(matched_symptoms[:4]))
            if species:
                reasons.append("Species compatibility: " + ("high" if species_ok else "low"))
            if category_hint:
                reasons.append(f"Category hint from complaint: {category_hint}")

            results.append(
                {
                    "name": disease.get("name", "Unknown"),
                    "score": float(score),
                    "confidence": 0.0,
                    "semantic_similarity": round(float(semantic), 3),
                    "matched_symptoms": matched_symptoms,
                    "severity": disease.get("severity", "unknown"),
                    "category": disease.get("category"),
                    "common_symptoms": symptoms,
                    "reasons": reasons,
                    "_species_match": species_ok,
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        if top_k > 0:
            results = results[:top_k]

        if results:
            max_score = max(results[0]["score"], 1e-6)
            for row in results:
                row["confidence"] = round(max(0.0, row["score"] / max_score), 3)
                row.pop("_species_match", None)

        meta = PredictionMeta(
            engine_mode=engine_mode,
            category_hint=category_hint,
            used_candidates=len(self._index),
        )
        if return_meta:
            return results, meta
        return results

    def generate_followup_question(
        self,
        predictions: List[Dict[str, Any]],
        symptom_text: str,
    ) -> Optional[Dict[str, Any]]:
        if len(predictions) < 2:
            return None

        gap = predictions[0]["confidence"] - predictions[1]["confidence"]
        if gap > 0.18:
            return None

        top1 = predictions[0]
        top2 = predictions[1]
        symptoms1 = {str(s).replace("_", " ").lower() for s in (top1.get("common_symptoms") or [])}
        symptoms2 = {str(s).replace("_", " ").lower() for s in (top2.get("common_symptoms") or [])}
        candidates = list((symptoms1 - symptoms2) | (symptoms2 - symptoms1))
        if not candidates:
            return None

        text_lc = _normalize_text(symptom_text)
        ranked: List[Tuple[float, str]] = []
        for phrase in candidates:
            phrase = phrase.strip()
            if not phrase or phrase in text_lc:
                continue
            score = len(phrase.split()) * 0.1
            if any(keyword in phrase for keyword in self.PRIORITY_KEYWORDS):
                score += 2.0
            if phrase in symptoms1 and phrase not in symptoms2:
                score += 0.25
            if phrase in symptoms2 and phrase not in symptoms1:
                score += 0.25
            ranked.append((score, phrase))

        if not ranked:
            return None
        ranked.sort(reverse=True)
        best_symptom = ranked[0][1]
        return {
            "symptom_phrase": best_symptom,
            "question": f"Has your pet shown {best_symptom}?",
            "reason": f"Helps distinguish {top1['name']} from {top2['name']}",
            "compared_conditions": [top1["name"], top2["name"]],
            "confidence_gap": round(gap, 3),
        }

    @staticmethod
    def _renormalize(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not predictions:
            return predictions
        predictions.sort(key=lambda item: item["score"], reverse=True)
        max_score = max(predictions[0]["score"], 1e-6)
        for row in predictions:
            row["confidence"] = round(max(0.0, row["score"] / max_score), 3)
        return predictions

    def apply_followup_answer(
        self,
        predictions: List[Dict[str, Any]],
        symptom_phrase: str,
        answer_yes: bool,
    ) -> List[Dict[str, Any]]:
        if not predictions:
            return predictions

        phrase = _normalize_text(symptom_phrase)
        updated: List[Dict[str, Any]] = []
        for row in predictions:
            symptoms = {str(s).replace("_", " ").lower() for s in (row.get("common_symptoms") or [])}
            has_symptom = phrase in symptoms
            score = float(row.get("score", 0.0))
            if answer_yes:
                score *= 1.14 if has_symptom else 0.96
            else:
                score *= 0.84 if has_symptom else 1.03

            row_copy = dict(row)
            row_copy["score"] = score
            reasoning = list(row_copy.get("reasons") or [])
            response_text = "yes" if answer_yes else "no"
            reasoning.append(
                f"Follow-up answer '{response_text}' for '{phrase}' {'supports' if has_symptom else 'weakens'} this condition"
            )
            row_copy["reasons"] = reasoning[-4:]
            updated.append(row_copy)

        return self._renormalize(updated)


class DiagnosticSession:
    """Stateful wrapper for iterative semantic differential diagnosis."""

    def __init__(self, predictor: DiseasePredictor, symptom_text: str, species: Optional[str]):
        self.predictor = predictor
        self.symptom_text = symptom_text
        self.species = species
        self.diseases, self.meta = predictor.predict_disease(
            symptom_text,
            species=species,
            return_meta=True,
        )
        self.asked_questions: List[Dict[str, Any]] = []

    def get_top_diseases(self, k: int = 3) -> List[Dict[str, Any]]:
        return self.diseases[:k]

    def get_confidence_gap(self) -> float:
        if len(self.diseases) < 2:
            return 1.0
        return float(self.diseases[0]["confidence"] - self.diseases[1]["confidence"])

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        return self.predictor.generate_followup_question(self.diseases, self.symptom_text)

    def update_scores(self, symptom_phrase: str, answer_yes: bool):
        self.diseases = self.predictor.apply_followup_answer(
            self.diseases,
            symptom_phrase=symptom_phrase,
            answer_yes=answer_yes,
        )
        self.asked_questions.append(
            {"symptom_phrase": symptom_phrase, "answer_yes": answer_yes}
        )

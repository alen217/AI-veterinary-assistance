"""Seed MongoDB with additional veterinary diseases and symptoms.

Adds (by default):
- 200 diseases (upsert by name)
- 500 symptoms (unique keys)
- default users (admin/user) with roles in `users` collection

Safe for repeated runs (idempotent upserts).

Usage:
  python seed_large_dataset.py
  python seed_large_dataset.py --diseases 200 --symptoms 500

Environment:
  MONGO_URL
  MONGO_DB_NAME
  ADMIN_USERNAME
  ADMIN_PASSWORD
  DEFAULT_USER_USERNAME
  DEFAULT_USER_PASSWORD
"""

from __future__ import annotations

import argparse
import random
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from veterinary_database import VeterinaryDatabase


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


SYSTEMS: List[str] = [
    "general",
    "gastrointestinal",
    "respiratory",
    "cardiovascular",
    "neurologic",
    "dermatologic",
    "musculoskeletal",
    "urologic",
    "reproductive",
    "endocrine",
    "ophthalmic",
    "otologic",
    "hematologic",
    "immune",
]

BASE_SYMPTOMS: List[Tuple[str, str]] = [
    ("vomiting", "gastrointestinal"),
    ("diarrhea", "gastrointestinal"),
    ("loss_of_appetite", "general"),
    ("increased_thirst", "endocrine"),
    ("increased_urination", "urologic"),
    ("lethargy", "general"),
    ("fever", "general"),
    ("cough", "respiratory"),
    ("nasal_discharge", "respiratory"),
    ("labored_breathing", "respiratory"),
    ("sneezing", "respiratory"),
    ("itching", "dermatologic"),
    ("hair_loss", "dermatologic"),
    ("rash", "dermatologic"),
    ("red_skin", "dermatologic"),
    ("lameness", "musculoskeletal"),
    ("joint_pain", "musculoskeletal"),
    ("stiffness", "musculoskeletal"),
    ("seizure", "neurologic"),
    ("tremor", "neurologic"),
    ("incoordination", "neurologic"),
    ("eye_redness", "ophthalmic"),
    ("eye_discharge", "ophthalmic"),
    ("ear_discharge", "otologic"),
    ("ear_itching", "otologic"),
    ("weight_loss", "general"),
    ("weight_gain", "general"),
    ("pale_gums", "hematologic"),
    ("swollen_lymph_nodes", "immune"),
]

SEVERITIES = ["mild", "moderate", "severe"]
SPECIES = ["dog", "cat", "rabbit", "bird", "cow", "goat", "horse"]


def generate_symptoms(target_count: int) -> List[Dict]:
    symptoms: Dict[str, Dict] = {}

    # Seed with known symptoms
    for key, system in BASE_SYMPTOMS:
        symptoms[key] = {
            "key": key,
            "label": key.replace("_", " ").title(),
            "system": system,
            "created_at": datetime.now(timezone.utc),
        }

    modifiers = [
        "mild",
        "moderate",
        "severe",
        "acute",
        "chronic",
        "intermittent",
        "persistent",
        "recurrent",
    ]
    patterns = [
        ("pain", "general"),
        ("swelling", "general"),
        ("discharge", "general"),
        ("redness", "general"),
        ("weakness", "general"),
        ("behavior_change", "neurologic"),
        ("gait_change", "musculoskeletal"),
        ("breathing_noise", "respiratory"),
        ("skin_lesion", "dermatologic"),
        ("urination_change", "urologic"),
        ("stool_change", "gastrointestinal"),
    ]

    rng = random.Random(1337)

    while len(symptoms) < target_count:
        base, default_system = rng.choice(patterns)
        system = rng.choice(SYSTEMS) if default_system == "general" else default_system
        modifier = rng.choice(modifiers)
        location = rng.choice(
            [
                "abdominal",
                "thoracic",
                "hind_limb",
                "fore_limb",
                "skin",
                "ear",
                "eye",
                "oral",
                "urinary",
            ]
        )
        key = slugify(f"{modifier}_{location}_{base}")
        if key in symptoms:
            continue
        symptoms[key] = {
            "key": key,
            "label": key.replace("_", " ").title(),
            "system": system,
            "created_at": datetime.now(timezone.utc),
        }

    return list(symptoms.values())[:target_count]


def generate_disease_names(target_count: int) -> List[str]:
    # A mix of common veterinary conditions + programmatic expansion.
    curated = [
        "Canine Distemper",
        "Rabies",
        "Leptospirosis",
        "Canine Infectious Hepatitis",
        "Canine Influenza",
        "Canine Coronavirus",
        "Feline Calicivirus Infection",
        "Feline Herpesvirus Infection",
        "Feline Panleukopenia",
        "Feline Infectious Peritonitis",
        "Heartworm Disease",
        "Hookworm Infection",
        "Roundworm Infection",
        "Tapeworm Infection",
        "Giardiasis",
        "Coccidiosis",
        "Lyme Disease",
        "Anaplasmosis",
        "Ehrlichiosis",
        "Babesiosis",
        "Otitis Externa",
        "Periodontal Disease",
        "Chronic Kidney Disease",
        "Acute Kidney Injury",
        "Cystitis",
        "Urolithiasis",
        "Pyometra",
        "Mastitis",
        "Hypothyroidism",
        "Hyperthyroidism",
        "Diabetes Mellitus",
        "Cushing's Disease",
        "Addison's Disease",
        "Pancreatitis",
        "Inflammatory Bowel Disease",
        "Gastric Dilatation-Volvulus",
        "Foreign Body Obstruction",
        "Parvovirus",
        "Kennel Cough",
        "Pneumonia",
        "Asthma (Feline)",
        "Allergic Dermatitis",
        "Atopic Dermatitis",
        "Flea Allergy Dermatitis",
        "Ringworm",
        "Sarcoptic Mange",
        "Demodectic Mange",
        "Osteoarthritis",
        "Hip Dysplasia",
        "Intervertebral Disc Disease",
        "Epilepsy",
        "Vestibular Disease",
        "Conjunctivitis",
        "Corneal Ulcer",
        "Glaucoma",
        "Uveitis",
    ]

    categories = [
        "Infectious",
        "Inflammatory",
        "Metabolic",
        "Degenerative",
        "Toxic",
        "Congenital",
        "Parasitic",
        "Neoplastic",
        "Immune-Mediated",
    ]
    systems = [
        "Respiratory",
        "Gastrointestinal",
        "Dermatologic",
        "Neurologic",
        "Cardiac",
        "Urinary",
        "Hepatic",
        "Ocular",
        "Otologic",
        "Musculoskeletal",
        "Reproductive",
    ]

    names: List[str] = []
    seen = set()

    def add(name: str):
        if name not in seen:
            seen.add(name)
            names.append(name)

    for n in curated:
        add(n)

    rng = random.Random(42)
    while len(names) < target_count:
        cat = rng.choice(categories)
        sys = rng.choice(systems)
        suffix = rng.choice(["Syndrome", "Disorder", "Disease", "Condition"])
        add(f"{sys} {cat} {suffix} {len(names)+1}")

    return names[:target_count]


def choose_symptoms(symptom_keys: List[str], rng: random.Random) -> List[str]:
    k = rng.randint(6, 14)
    return rng.sample(symptom_keys, k=k)


def seed(db: VeterinaryDatabase, disease_count: int, symptom_count: int) -> None:
    db.ensure_default_users()

    # Symptoms
    symptoms = generate_symptoms(symptom_count)
    for s in symptoms:
        db.symptoms.update_one({"key": s["key"]}, {"$setOnInsert": s}, upsert=True)

    symptom_keys = [s["key"] for s in symptoms]

    # Diseases
    rng = random.Random(2025)
    names = generate_disease_names(disease_count)

    for name in names:
        common_symptoms = choose_symptoms(symptom_keys, rng)
        severity = rng.choices(SEVERITIES, weights=[0.55, 0.35, 0.10], k=1)[0]
        species = rng.sample(SPECIES, k=rng.randint(1, 3))
        scientific_name = name  # kept simple to avoid incorrect mappings

        # Keep treatment/prevention cautious and generic
        treatment = (
            "Supportive care as indicated; maintain hydration and nutrition; "
            "consider diagnostics and targeted therapy per veterinarian guidance."
        )
        prevention = (
            "Routine veterinary checkups, vaccination/parasite prevention as appropriate, "
            "and good husbandry (diet, hygiene, stress reduction)."
        )

        doc = {
            "name": name,
            "scientific_name": scientific_name,
            "description": f"Seeded condition: {name}. This entry is generated for database expansion/testing.",
            "common_symptoms": common_symptoms,
            "causes": ["multifactorial", "requires_veterinary_evaluation"],
            "treatment": treatment,
            "prevention": prevention,
            "severity": severity,
            "affected_species": species,
            "seeded": True,
            "seeded_at": datetime.now(timezone.utc),
        }

        db.diseases.update_one({"name": name}, {"$setOnInsert": doc}, upsert=True)

        # Add 1 generic treatment option per disease (optional)
        disease_doc = db.diseases.find_one({"name": name}, {"_id": 1})
        if disease_doc:
            db.treatments.update_one(
                {"disease_id": str(disease_doc["_id"]), "name": "General Supportive Care"},
                {
                    "$setOnInsert": {
                        "disease_id": str(disease_doc["_id"]),
                        "name": "General Supportive Care",
                        "description": "General supportive care and monitoring; veterinarian-directed diagnostics and therapy.",
                        "medication": "As prescribed by veterinarian",
                        "dosage": "N/A",
                        "duration": "Varies",
                        "effectiveness": 0.6,
                    }
                },
                upsert=True,
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diseases", type=int, default=200, help="Number of diseases to seed")
    parser.add_argument("--symptoms", type=int, default=500, help="Number of symptoms to seed")
    args = parser.parse_args()

    db = VeterinaryDatabase()
    seed(db, disease_count=args.diseases, symptom_count=args.symptoms)
    disease_total = db.diseases.count_documents({})
    symptom_total = db.symptoms.count_documents({})
    user_total = db.users.count_documents({})
    db.close()

    print(f"Seed complete. diseases={disease_total}, symptoms={symptom_total}, users={user_total}")


if __name__ == "__main__":
    main()

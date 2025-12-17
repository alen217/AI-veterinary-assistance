"""
Add Custom Diseases to MongoDB Database
Demonstrates how to add new diseases and treatments to the veterinary database
"""

import os
from dotenv import load_dotenv
from veterinary_database import VeterinaryDatabase, Disease, TreatmentOption

# Load environment variables
load_dotenv()

mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
mongo_db_name = os.getenv("MONGO_DB_NAME", "veterinary_ai_db")

print("Connecting to MongoDB...")
db = VeterinaryDatabase(mongo_url=mongo_url, db_name=mongo_db_name)
print("✓ Connected!\n")

# Example 1: Add a new disease
print("="*80)
print("Adding New Diseases")
print("="*80 + "\n")

new_diseases = [
    Disease(
        id="",  # Will be auto-generated
        name="Kennel Cough",
        scientific_name="Canine Infectious Tracheobronchitis",
        description="Highly contagious respiratory disease in dogs characterized by a persistent dry, hacking cough.",
        common_symptoms=["cough", "sneezing", "nasal_discharge", "mild_fever", "loss_of_appetite"],
        causes=["viral infection", "bacterial infection", "environmental stress", "poor ventilation"],
        treatment="Rest, humidity, cough suppressants, antibiotics if bacterial component present",
        prevention="Bordetella vaccination, avoid overcrowding, good ventilation, stress reduction",
        severity="mild",
        affected_species=["dog"]
    ),
    Disease(
        id="",
        name="Feline Panleukopenia",
        scientific_name="Feline Distemper",
        description="Highly contagious viral disease in cats affecting rapidly dividing cells, especially in the intestines and bone marrow.",
        common_symptoms=["vomiting", "diarrhea", "lethargy", "loss_of_appetite", "fever", "dehydration"],
        causes=["viral infection", "contact with infected cats", "contaminated environment"],
        treatment="Supportive care, IV fluids, antibiotics for secondary infections, anti-nausea medication",
        prevention="FVRCP vaccination, isolation of infected cats, disinfection",
        severity="severe",
        affected_species=["cat"]
    ),
    Disease(
        id="",
        name="Hip Dysplasia",
        scientific_name="Canine Hip Dysplasia",
        description="Genetic condition causing abnormal development of the hip joint, leading to arthritis and pain.",
        common_symptoms=["lameness", "difficulty_standing", "reduced_activity", "pain", "stiffness"],
        causes=["genetic factors", "rapid growth", "obesity", "improper exercise"],
        treatment="Weight management, pain medication, physical therapy, surgery in severe cases",
        prevention="Screening breeding stock, controlled growth rate, maintaining healthy weight",
        severity="moderate",
        affected_species=["dog"]
    ),
    Disease(
        id="",
        name="Feline Lower Urinary Tract Disease",
        scientific_name="FLUTD",
        description="Group of conditions affecting the bladder and urethra in cats, causing painful urination.",
        common_symptoms=["frequent_urination", "blood_in_urine", "straining", "licking_genital_area", "urinating_outside_litter_box"],
        causes=["bladder stones", "urinary tract infection", "stress", "diet"],
        treatment="Increased water intake, dietary changes, pain medication, antibiotics if infection present",
        prevention="Adequate hydration, stress reduction, appropriate diet, regular vet checkups",
        severity="moderate",
        affected_species=["cat"]
    ),
    Disease(
        id="",
        name="Heartworm Disease",
        scientific_name="Dirofilariasis",
        description="Serious parasitic disease transmitted by mosquitoes, causing damage to the heart and lungs.",
        common_symptoms=["cough", "lethargy", "weight_loss", "labored_breathing", "reduced_activity"],
        causes=["mosquito bite", "infected animals in area", "lack of prevention"],
        treatment="Heartworm treatment protocol with medication, rest, supportive care",
        prevention="Monthly heartworm preventive medication, mosquito control",
        severity="severe",
        affected_species=["dog", "cat"]
    ),
    Disease(
        id="",
        name="Dental Disease",
        scientific_name="Periodontal Disease",
        description="Progressive inflammatory condition affecting the gums and supporting structures of teeth.",
        common_symptoms=["bad_breath", "swollen_gums", "difficulty_eating", "drooling", "tooth_loss"],
        causes=["plaque buildup", "tartar accumulation", "poor oral hygiene", "diet"],
        treatment="Professional dental cleaning, tooth extraction if needed, antibiotics, pain management",
        prevention="Regular teeth brushing, dental treats, professional cleanings, appropriate diet",
        severity="mild",
        affected_species=["dog", "cat"]
    ),
    Disease(
        id="",
        name="Ringworm",
        scientific_name="Dermatophytosis",
        description="Fungal infection affecting the skin, hair, and nails, highly contagious to other animals and humans.",
        common_symptoms=["circular_hair_loss", "scaly_skin", "itching", "redness", "crusting"],
        causes=["fungal infection", "contact with infected animals", "contaminated environment"],
        treatment="Antifungal medication (topical and/or oral), environmental decontamination, isolation",
        prevention="Good hygiene, avoid contact with infected animals, environmental cleaning",
        severity="mild",
        affected_species=["dog", "cat", "rabbit"]
    ),
    Disease(
        id="",
        name="Lyme Disease",
        scientific_name="Borreliosis",
        description="Bacterial infection transmitted by ticks, causing joint inflammation and other complications.",
        common_symptoms=["lameness", "fever", "loss_of_appetite", "lethargy", "swollen_lymph_nodes"],
        causes=["tick bite", "infected deer ticks", "endemic areas"],
        treatment="Antibiotics (doxycycline), pain management, supportive care",
        prevention="Tick prevention medication, tick checks, vaccination, avoid tick-infested areas",
        severity="moderate",
        affected_species=["dog"]
    )
]

# Add each disease
added_count = 0
for disease in new_diseases:
    # Check if already exists
    existing = db.search_by_name(disease.name)
    if existing:
        print(f"⊙ {disease.name} already exists, skipping...")
    else:
        disease_id = db.add_disease(disease)
        print(f"✓ Added: {disease.name}")
        print(f"  ID: {disease_id}")
        print(f"  Severity: {disease.severity}")
        print(f"  Species: {', '.join(disease.affected_species)}")
        print()
        added_count += 1

print(f"\n✓ Added {added_count} new disease(s)\n")

# Example 2: Add treatments for a disease
print("="*80)
print("Adding Treatments")
print("="*80 + "\n")

# Find Kennel Cough to add treatments
kennel_cough = db.search_by_name("Kennel Cough")
if kennel_cough:
    treatments = [
        TreatmentOption(
            id="",
            disease_id=kennel_cough.id,
            name="Supportive Care",
            description="Rest, humidity, and monitoring for 7-10 days",
            medication="None (self-limiting in mild cases)",
            dosage="N/A",
            duration="7-10 days",
            effectiveness=0.7
        ),
        TreatmentOption(
            id="",
            disease_id=kennel_cough.id,
            name="Antibiotic Therapy",
            description="For cases with bacterial component or secondary infection",
            medication="Doxycycline or Amoxicillin-Clavulanate",
            dosage="5-10 mg/kg twice daily",
            duration="10-14 days",
            effectiveness=0.85
        ),
        TreatmentOption(
            id="",
            disease_id=kennel_cough.id,
            name="Cough Suppressants",
            description="For severe, persistent coughing affecting quality of life",
            medication="Hydrocodone or Butorphanol",
            dosage="As prescribed by veterinarian",
            duration="5-7 days",
            effectiveness=0.75
        )
    ]
    
    for treatment in treatments:
        treatment_id = db.add_treatment(kennel_cough.id, treatment)
        print(f"✓ Added treatment: {treatment.name}")
        print(f"  Medication: {treatment.medication}")
        print(f"  Effectiveness: {treatment.effectiveness * 100}%")
        print()

# Show current database stats
print("="*80)
print("Database Statistics")
print("="*80 + "\n")

all_diseases = db.get_all_diseases()
print(f"Total diseases in database: {len(all_diseases)}\n")

# Count by severity
severity_counts = {}
species_counts = {}

for disease in all_diseases:
    severity_counts[disease.severity] = severity_counts.get(disease.severity, 0) + 1
    for species in disease.affected_species:
        species_counts[species] = species_counts.get(species, 0) + 1

print("By Severity:")
for severity, count in sorted(severity_counts.items()):
    print(f"  {severity.title()}: {count}")

print("\nBy Species:")
for species, count in sorted(species_counts.items()):
    print(f"  {species.title()}: {count}")

print("\nAll Diseases:")
for i, disease in enumerate(sorted(all_diseases, key=lambda x: x.name), 1):
    print(f"  {i}. {disease.name} ({disease.severity})")

db.close()
print("\n✓ Database updated successfully!")

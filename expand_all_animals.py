"""
Comprehensive Pet Animal Disease Database Expander
Adds diseases for ALL common pet animals
"""

from datetime import datetime
import random
from user_database import get_db

# Comprehensive list of ALL pet animals
ALL_PET_ANIMALS = [
    # Mammals - Common
    "dog", "cat", "rabbit", "hamster", "guinea_pig", "ferret", "rat", "mouse", 
    "gerbil", "chinchilla", "hedgehog",
    
    # Large Animals
    "horse", "pony", "donkey", "cow", "goat", "sheep", "pig", "alpaca", "llama",
    
    # Birds
    "parrot", "parakeet", "cockatiel", "canary", "finch", "lovebird", "macaw", 
    "budgie", "cockatoo", "conure",
    
    # Reptiles
    "turtle", "tortoise", "lizard", "gecko", "bearded_dragon", "snake", "iguana",
    "chameleon", "ball_python", "corn_snake",
    
    # Aquatic
    "fish", "goldfish", "betta", "koi",
    
    # Other Exotic
    "sugar_glider", "prairie_dog", "skunk", "monkey", "miniature_pig"
]

# Species-specific common diseases
SPECIES_SPECIFIC_DISEASES = {
    # Small Mammals
    "hamster": [
        ("Wet Tail", "severe", ["diarrhea", "lethargy", "loss_of_appetite", "dehydration", "hunched_posture"]),
        ("Hamster Polyomavirus", "severe", ["hair_loss", "skin_lesions", "weight_loss", "lethargy"]),
        ("Proliferative Ileitis", "severe", ["diarrhea", "weight_loss", "lethargy", "abdominal_distension"]),
    ],
    
    "guinea_pig": [
        ("Scurvy", "moderate", ["lethargy", "weight_loss", "rough_coat", "joint_pain", "bleeding_gums"]),
        ("Guinea Pig Pneumonia", "severe", ["labored_breathing", "nasal_discharge", "lethargy", "loss_of_appetite"]),
        ("Malocclusion", "moderate", ["drooling", "difficulty_eating", "weight_loss", "overgrown_teeth"]),
    ],
    
    "ferret": [
        ("Adrenal Disease", "severe", ["hair_loss", "itching", "muscle_loss", "lethargy"]),
        ("Insulinoma", "severe", ["weakness", "seizures", "lethargy", "drooling"]),
        ("Ferret Distemper", "severe", ["fever", "eye_discharge", "skin_rash", "neurological_signs"]),
    ],
    
    "chinchilla": [
        ("Fur Ring", "mild", ["difficulty_breeding", "swelling", "discomfort"]),
        ("Chinchilla Heat Stroke", "severe", ["panting", "drooling", "weakness", "seizures"]),
        ("Dental Disease", "moderate", ["drooling", "difficulty_eating", "weight_loss"]),
    ],
    
    "hedgehog": [
        ("Wobbly Hedgehog Syndrome", "severe", ["paralysis", "muscle_weakness", "incoordination", "weight_loss"]),
        ("Hedgehog Mites", "moderate", ["itching", "hair_loss", "skin_lesions", "scabbing"]),
        ("Hibernation Attempt", "severe", ["lethargy", "cold_body", "weakness", "loss_of_appetite"]),
    ],
    
    "gerbil": [
        ("Tyzzer's Disease", "severe", ["diarrhea", "lethargy", "hunched_posture", "death"]),
        ("Nasal Dermatitis", "mild", ["nose_rubbing", "hair_loss_on_nose", "redness"]),
        ("Seizures", "moderate", ["convulsions", "loss_of_consciousness", "muscle_twitching"]),
    ],
    
    # Birds
    "parrot": [
        ("Psittacine Beak and Feather Disease", "severe", ["feather_loss", "beak_abnormalities", "lethargy"]),
        ("Aspergillosis", "severe", ["respiratory_distress", "lethargy", "loss_of_appetite"]),
        ("Feather Plucking", "moderate", ["bald_patches", "damaged_feathers", "skin_irritation"]),
    ],
    
    "parakeet": [
        ("Budgie Scaly Face", "mild", ["crusty_beak", "crusty_feet", "deformed_beak"]),
        ("Air Sac Mites", "moderate", ["difficulty_breathing", "tail_bobbing", "voice_change"]),
        ("French Molt", "moderate", ["feather_loss", "inability_to_fly", "stunted_feathers"]),
    ],
    
    "cockatiel": [
        ("Cockatiel Wasting Syndrome", "severe", ["weight_loss", "regurgitation", "diarrhea", "depression"]),
        ("Night Frights", "mild", ["thrashing", "injury", "bleeding", "stress"]),
        ("Egg Binding", "severe", ["straining", "lethargy", "swollen_abdomen", "distress"]),
    ],
    
    # Reptiles
    "bearded_dragon": [
        ("Metabolic Bone Disease", "severe", ["soft_bones", "deformities", "paralysis", "seizures"]),
        ("Impaction", "severe", ["loss_of_appetite", "no_defecation", "lethargy", "paralysis"]),
        ("Yellow Fungus Disease", "severe", ["yellow_patches", "skin_lesions", "lethargy", "loss_of_appetite"]),
    ],
    
    "gecko": [
        ("Dysecdysis", "moderate", ["retained_skin", "toes_constricted", "eye_problems"]),
        ("Crypto", "severe", ["weight_loss", "regurgitation", "diarrhea", "tail_loss"]),
        ("Mouth Rot", "moderate", ["swollen_gums", "discharge", "loss_of_appetite", "drooling"]),
    ],
    
    "turtle": [
        ("Shell Rot", "moderate", ["soft_shell", "discolored_shell", "foul_odor", "shell_damage"]),
        ("Respiratory Infection", "severe", ["open_mouth_breathing", "nasal_discharge", "lethargy", "loss_of_appetite"]),
        ("Vitamin A Deficiency", "moderate", ["swollen_eyes", "ear_abscesses", "loss_of_appetite"]),
    ],
    
    "snake": [
        ("Inclusion Body Disease", "severe", ["regurgitation", "incoordination", "head_tremors", "death"]),
        ("Scale Rot", "moderate", ["discolored_scales", "blisters", "skin_lesions"]),
        ("Respiratory Infection", "severe", ["open_mouth_breathing", "mucus_discharge", "wheezing", "lethargy"]),
    ],
    
    # Aquatic
    "fish": [
        ("Ich", "moderate", ["white_spots", "scratching", "clamped_fins", "loss_of_appetite"]),
        ("Fin Rot", "mild", ["frayed_fins", "discoloration", "fin_loss"]),
        ("Swim Bladder Disease", "moderate", ["floating", "sinking", "difficulty_swimming", "loss_of_balance"]),
    ],
    
    # Exotic
    "sugar_glider": [
        ("Metabolic Bone Disease", "severe", ["paralysis", "fractures", "seizures", "tremors"]),
        ("Self-Mutilation", "moderate", ["open_wounds", "hair_loss", "infection", "stress"]),
        ("Obesity", "moderate", ["weight_gain", "lethargy", "difficulty_moving"]),
    ],
    
    "pig": [
        ("Swine Flu", "severe", ["fever", "cough", "nasal_discharge", "lethargy", "loss_of_appetite"]),
        ("Mange", "moderate", ["itching", "hair_loss", "skin_lesions", "crusting"]),
        ("Erysipelas", "severe", ["fever", "skin_lesions", "lameness", "death"]),
    ],
    
    "sheep": [
        ("Foot Rot", "moderate", ["lameness", "foul_odor", "swelling", "separation_of_hoof"]),
        ("Bloat", "severe", ["abdominal_distension", "difficulty_breathing", "death"]),
        ("Scrapie", "severe", ["itching", "behavioral_changes", "weight_loss", "death"]),
    ],
    
    "goat": [
        ("Caprine Arthritis Encephalitis", "severe", ["swollen_joints", "weight_loss", "difficulty_walking"]),
        ("Caseous Lymphadenitis", "moderate", ["swollen_lymph_nodes", "abscesses", "weight_loss"]),
        ("Listeriosis", "severe", ["circling", "head_tilt", "paralysis", "death"]),
    ],
}

# Common symptoms that apply across species
UNIVERSAL_SYMPTOMS = [
    "lethargy", "loss_of_appetite", "weight_loss", "fever", "dehydration",
    "diarrhea", "vomiting", "difficulty_breathing", "weakness", "pain"
]

def add_species_specific_diseases(db):
    """Add species-specific diseases to database"""
    
    added = 0
    
    for species, disease_list in SPECIES_SPECIFIC_DISEASES.items():
        for disease_name, severity, symptoms in disease_list:
            disease = {
                "name": disease_name,
                "scientific_name": f"{disease_name} ({species.replace('_', ' ').title()})",
                "description": f"{disease_name} is a common condition affecting {species.replace('_', ' ')}s, requiring veterinary attention.",
                "common_symptoms": symptoms,
                "treatment": f"Veterinary treatment for {disease_name} includes supportive care, medication, and environmental management as needed.",
                "prevention": f"Proper husbandry, diet, and regular veterinary checkups can help prevent {disease_name}.",
                "severity": severity,
                "affected_species": [species],
                "category": "species_specific",
                "created_at": datetime.now()
            }
            
            db.diseases.update_one(
                {"name": disease_name},
                {"$set": disease},
                upsert=True
            )
            added += 1
    
    return added

def add_universal_diseases(db):
    """Add diseases that can affect multiple species"""
    
    universal_diseases = [
        ("Dehydration", "moderate", ["lethargy", "dry_gums", "sunken_eyes", "weakness"]),
        ("Obesity", "mild", ["weight_gain", "difficulty_moving", "lethargy", "breathing_difficulty"]),
        ("Parasitic Infection", "moderate", ["weight_loss", "diarrhea", "poor_coat", "lethargy"]),
        ("Bacterial Infection", "moderate", ["fever", "lethargy", "loss_of_appetite", "weakness"]),
        ("Viral Infection", "severe", ["fever", "lethargy", "loss_of_appetite", "weakness", "vomiting"]),
        ("Fungal Infection", "moderate", ["skin_lesions", "itching", "hair_loss", "discharge"]),
        ("Trauma", "severe", ["wounds", "bleeding", "pain", "shock", "lameness"]),
        ("Poisoning", "severe", ["vomiting", "diarrhea", "seizures", "weakness", "death"]),
        ("Stress", "mild", ["lethargy", "loss_of_appetite", "behavioral_changes", "hiding"]),
        ("Old Age Complications", "moderate", ["weakness", "weight_loss", "organ_failure", "arthritis"]),
    ]
    
    added = 0
    
    for disease_name, severity, symptoms in universal_diseases:
        # Add for all species
        disease = {
            "name": disease_name,
            "scientific_name": f"{disease_name} (Multi-species)",
            "description": f"{disease_name} can affect various animal species and requires appropriate veterinary care.",
            "common_symptoms": symptoms,
            "treatment": f"Treatment varies by species but generally includes supportive care and addressing underlying causes.",
            "prevention": f"Proper care, diet, environment, and regular veterinary monitoring help prevent {disease_name}.",
            "severity": severity,
            "affected_species": ALL_PET_ANIMALS,
            "category": "universal",
            "created_at": datetime.now()
        }
        
        # Check if exists first
        existing = db.diseases.find_one({"name": disease_name})
        if existing:
            # Update to add more species
            db.diseases.update_one(
                {"name": disease_name},
                {"$set": {"affected_species": ALL_PET_ANIMALS, "category": "universal"}}
            )
        else:
            db.diseases.insert_one(disease)
        added += 1
    
    return added

def update_existing_diseases_with_more_species(db):
    """Update existing diseases to include more species where applicable"""
    
    # Respiratory diseases can affect most mammals and birds
    respiratory_species = ["dog", "cat", "rabbit", "hamster", "guinea_pig", "ferret", 
                          "rat", "mouse", "horse", "cow", "goat", "sheep", "pig",
                          "parrot", "parakeet", "cockatiel", "budgie"]
    
    db.diseases.update_many(
        {"category": "respiratory"},
        {"$addToSet": {"affected_species": {"$each": respiratory_species}}}
    )
    
    # Digestive issues affect most animals
    digestive_species = ALL_PET_ANIMALS
    
    db.diseases.update_many(
        {"category": "digestive"},
        {"$addToSet": {"affected_species": {"$each": digestive_species}}}
    )
    
    # Skin diseases affect most mammals
    skin_species = ["dog", "cat", "rabbit", "hamster", "guinea_pig", "ferret",
                   "rat", "mouse", "chinchilla", "hedgehog", "gerbil",
                   "horse", "cow", "goat", "sheep", "pig"]
    
    db.diseases.update_many(
        {"category": "skin"},
        {"$addToSet": {"affected_species": {"$each": skin_species}}}
    )
    
    print("✅ Updated existing diseases with additional species")

if __name__ == "__main__":
    db = get_db()
    
    print("="*70)
    print("EXPANDING DATABASE WITH ALL PET ANIMALS")
    print("="*70)
    
    # Add species-specific diseases
    print("\n1️⃣ Adding species-specific diseases...")
    added_specific = add_species_specific_diseases(db)
    print(f"   ✅ Added {added_specific} species-specific diseases")
    
    # Add universal diseases
    print("\n2️⃣ Adding universal diseases...")
    added_universal = add_universal_diseases(db)
    print(f"   ✅ Added {added_universal} universal diseases")
    
    # Update existing diseases
    print("\n3️⃣ Updating existing diseases with more species...")
    update_existing_diseases_with_more_species(db)
    
    # Show final stats
    print("\n" + "="*70)
    print("FINAL DATABASE STATISTICS")
    print("="*70)
    
    total_diseases = db.diseases.count_documents({})
    print(f"\n📊 Total Diseases: {total_diseases}")
    
    print("\n🐾 Diseases by Species:")
    for species in sorted(ALL_PET_ANIMALS):
        count = db.diseases.count_documents({"affected_species": species})
        print(f"   {species.replace('_', ' ').title()}: {count} diseases")
    
    print("\n" + "="*70)
    print("✅ DATABASE EXPANSION COMPLETE")
    print("="*70)

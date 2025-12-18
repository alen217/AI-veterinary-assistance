from veterinary_database import VeterinaryDatabase, Disease

def batch_insert_common_diseases():
    db = VeterinaryDatabase("veterinary_database.db")

    diseases = [

        Disease(
            id=0,
            name="Worm Infestation",
            scientific_name="Helminthiasis",
            description="Parasitic worm infection commonly affecting digestive tract.",
            common_symptoms=[
                "weight_loss",
                "pot_belly",
                "diarrhea",
                "poor_appetite"
            ],
            causes=["parasitic infection"],
            treatment="Deworming medication and nutritional support",
            prevention="Regular deworming and hygiene",
            severity="mild",
            affected_species=["dog", "cat", "cow", "goat"]
        ),

        Disease(
            id=0,
            name="Tick Fever",
            scientific_name="Babesiosis",
            description="Tick-borne disease causing fever and anemia.",
            common_symptoms=[
                "fever",
                "lethargy",
                "anemia",
                "loss_of_appetite"
            ],
            causes=["tick infestation"],
            treatment="Antiprotozoal drugs and supportive therapy",
            prevention="Tick control and hygiene",
            severity="moderate",
            affected_species=["dog", "cow"]
        ),

        Disease(
            id=0,
            name="Kennel Cough",
            scientific_name="Infectious Tracheobronchitis",
            description="Contagious respiratory disease in dogs.",
            common_symptoms=[
                "dry_cough",
                "gagging",
                "nasal_discharge",
                "lethargy"
            ],
            causes=["viral infection", "bacterial infection"],
            treatment="Cough suppressants and antibiotics if required",
            prevention="Vaccination and isolation",
            severity="mild",
            affected_species=["dog"]
        ),

        Disease(
            id=0,
            name="Urinary Tract Infection",
            scientific_name="Urinary Infection",
            description="Bacterial infection affecting urinary system.",
            common_symptoms=[
                "frequent_urination",
                "painful_urination",
                "blood_in_urine",
                "lethargy"
            ],
            causes=["bacterial infection"],
            treatment="Antibiotics and increased fluid intake",
            prevention="Proper hydration and hygiene",
            severity="mild",
            affected_species=["dog", "cat"]
        ),

        Disease(
            id=0,
            name="Arthritis",
            scientific_name="Degenerative Joint Disease",
            description="Chronic joint inflammation common in older animals.",
            common_symptoms=[
                "joint_pain",
                "stiffness",
                "difficulty_walking",
                "lameness"
            ],
            causes=["aging", "joint wear"],
            treatment="Pain management and joint supplements",
            prevention="Weight management and exercise",
            severity="moderate",
            affected_species=["dog", "cow"]
        ),

        Disease(
            id=0,
            name="Indigestion",
            scientific_name="Ruminal Acidosis",
            description="Digestive disorder caused by improper feeding.",
            common_symptoms=[
                "reduced_feed_intake",
                "bloating",
                "diarrhea",
                "lethargy"
            ],
            causes=["diet imbalance"],
            treatment="Diet correction and supportive care",
            prevention="Balanced feeding practices",
            severity="mild",
            affected_species=["cow", "goat"]
        ),

        Disease(
            id=0,
            name="Eye Injury",
            scientific_name="Corneal Ulcer",
            description="Eye injury leading to irritation and pain.",
            common_symptoms=[
                "excessive_tearing",
                "eye_redness",
                "squinting",
                "discharge_eye"
            ],
            causes=["trauma", "foreign body"],
            treatment="Antibiotic eye drops and protection",
            prevention="Avoid eye trauma and maintain hygiene",
            severity="mild",
            affected_species=["dog", "cat", "cow"]
        ),

        Disease(
            id=0,
            name="Nutritional Deficiency",
            scientific_name="Malnutrition",
            description="Deficiency of essential nutrients affecting growth and health.",
            common_symptoms=[
                "poor_growth",
                "weakness",
                "dull_coat",
                "weight_loss"
            ],
            causes=["improper diet"],
            treatment="Nutritional supplementation",
            prevention="Balanced diet",
            severity="mild",
            affected_species=["dog", "cow", "goat"]
        )
    ]

    for d in diseases:
        try:
            db.add_disease(d)
            print(f"Added: {d.name}")
        except Exception as e:
            print(f"Skipped {d.name}: {e}")

    db.close()
    print("Common disease batch insert completed.")


if __name__ == "__main__":
    batch_insert_common_diseases()

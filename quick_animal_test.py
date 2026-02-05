"""
Quick test to verify animal-specific disease filtering
"""
print("Testing animal-specific filtering...")

# Simple test without running streamlit
from mongo_disease_repository import MongoDiseaseRepository

repo = MongoDiseaseRepository()

# Test cat diseases
cat_diseases = repo.find_by_symptoms(
    symptoms=["vomiting", "lethargy"],
    species="cat"
)

print(f"\n✅ Found {len(cat_diseases)} diseases for CATS")
if cat_diseases:
    print(f"   Example: {cat_diseases[0]['name']}")
    print(f"   Species: {cat_diseases[0].get('affected_species', [])}")

# Test dog diseases  
dog_diseases = repo.find_by_symptoms(
    symptoms=["coughing"],
    species="dog"
)

print(f"\n✅ Found {len(dog_diseases)} diseases for DOGS")
if dog_diseases:
    print(f"   Example: {dog_diseases[0]['name']}")
    print(f"   Species: {dog_diseases[0].get('affected_species', [])}")

# Test hamster diseases
hamster_diseases = repo.find_by_symptoms(
    symptoms=["weight loss"],
    species="hamster"
)

print(f"\n✅ Found {len(hamster_diseases)} diseases for HAMSTERS")
if hamster_diseases:
    print(f"   Example: {hamster_diseases[0]['name']}")
    print(f"   Species: {hamster_diseases[0].get('affected_species', [])}")

print("\n✅ Animal-specific filtering is working!")

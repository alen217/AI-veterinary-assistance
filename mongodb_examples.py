"""
MongoDB Example - Simple Usage Demo
Demonstrates how to use the MongoDB-based Veterinary AI Assistant
"""

from veterinary_database import VeterinaryDatabase, Disease
from main import VeterinaryAIAssistant


def example_1_basic_database_operations():
    """Example 1: Basic database operations"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Database Operations")
    print("="*80 + "\n")
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    db = VeterinaryDatabase()
    print("✓ Connected!\n")
    
    # Get all diseases
    diseases = db.get_all_diseases()
    print(f"Total diseases in database: {len(diseases)}\n")
    
    # Display first 3 diseases
    print("First 3 diseases:")
    for i, disease in enumerate(diseases[:3], 1):
        print(f"{i}. {disease.name}")
        print(f"   Severity: {disease.severity}")
        print(f"   Species: {', '.join(disease.affected_species)}")
        print()
    
    db.close()
    print("✓ Connection closed")


def example_2_symptom_search():
    """Example 2: Search by symptoms"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Search by Symptoms")
    print("="*80 + "\n")
    
    db = VeterinaryDatabase()
    
    # Search for diseases with specific symptoms
    symptoms = ['vomiting', 'diarrhea', 'lethargy']
    print(f"Searching for diseases with symptoms: {', '.join(symptoms)}\n")
    
    results = db.search_by_symptoms(symptoms)
    
    print(f"Found {len(results)} matching disease(s):\n")
    
    for disease, match_count in results[:5]:
        print(f"• {disease.name}")
        print(f"  Matched {match_count} of {len(symptoms)} symptoms")
        print(f"  Severity: {disease.severity}")
        print(f"  Treatment: {disease.treatment[:80]}...")
        print()
    
    db.close()


def example_3_search_by_name():
    """Example 3: Search specific disease"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Search Specific Disease")
    print("="*80 + "\n")
    
    db = VeterinaryDatabase()
    
    disease_name = "Parvovirus"
    print(f"Searching for: {disease_name}\n")
    
    disease = db.search_by_name(disease_name)
    
    if disease:
        print(f"✓ Found: {disease.name}")
        print(f"  Scientific Name: {disease.scientific_name}")
        print(f"  Description: {disease.description}")
        print(f"  Common Symptoms: {', '.join(disease.common_symptoms)}")
        print(f"  Severity: {disease.severity}")
        print(f"  Treatment: {disease.treatment}")
        print(f"  Prevention: {disease.prevention}")
    else:
        print("✗ Disease not found")
    
    db.close()


def example_4_complete_analysis():
    """Example 4: Complete patient analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Complete Patient Analysis")
    print("="*80 + "\n")
    
    # Sample patient description
    patient_text = """
    My 3-year-old male golden retriever named Max has been having some issues.
    He weighs about 70 lbs. For the past 2 days, he's been vomiting several times
    a day and has watery diarrhea. He seems very tired and doesn't want to eat.
    His stomach appears to be causing him pain when I touch it.
    """
    
    print("Patient Description:")
    print("-" * 80)
    print(patient_text)
    print("-" * 80 + "\n")
    
    # Analyze with AI Assistant
    with VeterinaryAIAssistant() as assistant:
        print("Analyzing patient...")
        result = assistant.analyze_patient_text(patient_text)
        
        # Generate and print report
        report = assistant.generate_report(result)
        print(report)


def example_5_add_new_disease():
    """Example 5: Add a new disease to database"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Add New Disease")
    print("="*80 + "\n")
    
    db = VeterinaryDatabase()
    
    # Check if disease already exists
    existing = db.search_by_name("Kennel Cough")
    
    if existing:
        print("Disease 'Kennel Cough' already exists in database")
        print(f"ID: {existing.id}")
    else:
        # Create new disease
        new_disease = Disease(
            id="",  # Will be auto-generated
            name="Kennel Cough",
            scientific_name="Canine Infectious Tracheobronchitis",
            description="Highly contagious respiratory disease affecting dogs, characterized by a persistent dry cough.",
            common_symptoms=["cough", "sneezing", "nasal_discharge", "mild_fever"],
            causes=["viral infection", "bacterial infection", "environmental stress"],
            treatment="Rest, humidity, cough suppressants; antibiotics if bacterial",
            prevention="Vaccination (Bordetella), avoid overcrowding, good ventilation",
            severity="mild",
            affected_species=["dog"]
        )
        
        # Add to database
        disease_id = db.add_disease(new_disease)
        print(f"✓ Added new disease: {new_disease.name}")
        print(f"  MongoDB ID: {disease_id}")
    
    db.close()


def example_6_keyword_search():
    """Example 6: Keyword search"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Keyword Search")
    print("="*80 + "\n")
    
    db = VeterinaryDatabase()
    
    keyword = "infection"
    print(f"Searching for keyword: '{keyword}'\n")
    
    results = db.search_by_keyword(keyword)
    
    print(f"Found {len(results)} disease(s) containing '{keyword}':\n")
    
    for disease in results[:5]:
        print(f"• {disease.name}")
        print(f"  {disease.description[:100]}...")
        print()
    
    db.close()


def example_7_mongodb_connection_options():
    """Example 7: Different MongoDB connection options"""
    print("\n" + "="*80)
    print("EXAMPLE 7: MongoDB Connection Options")
    print("="*80 + "\n")
    
    # Option 1: Default local connection
    print("Option 1: Default local MongoDB")
    print("  db = VeterinaryDatabase()")
    print()
    
    # Option 2: Custom local connection
    print("Option 2: Custom local MongoDB")
    print('  db = VeterinaryDatabase(')
    print('      mongo_url="mongodb://localhost:27017/",')
    print('      db_name="custom_vet_db"')
    print('  )')
    print()
    
    # Option 3: MongoDB Atlas
    print("Option 3: MongoDB Atlas (Cloud)")
    print('  db = VeterinaryDatabase(')
    print('      mongo_url="mongodb+srv://user:pass@cluster.mongodb.net/",')
    print('      db_name="veterinary_ai_db"')
    print('  )')
    print()
    
    # Option 4: With authentication
    print("Option 4: With authentication")
    print('  db = VeterinaryDatabase(')
    print('      mongo_url="mongodb://username:password@localhost:27017/"')
    print('  )')
    print()


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("#" * 80)
    print("VETERINARY AI - MongoDB Examples".center(80))
    print("#" * 80)
    
    try:
        example_1_basic_database_operations()
        example_2_symptom_search()
        example_3_search_by_name()
        example_6_keyword_search()
        example_7_mongodb_connection_options()
        
        # These examples modify data or are more complex
        print("\n" + "="*80)
        print("Advanced Examples (optional):")
        print("="*80)
        print("Run these separately if needed:")
        print("  - example_4_complete_analysis()")
        print("  - example_5_add_new_disease()")
        
        print("\n" + "#" * 80)
        print("Examples completed successfully!".center(80))
        print("#" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific example
        example_num = sys.argv[1]
        
        examples = {
            "1": example_1_basic_database_operations,
            "2": example_2_symptom_search,
            "3": example_3_search_by_name,
            "4": example_4_complete_analysis,
            "5": example_5_add_new_disease,
            "6": example_6_keyword_search,
            "7": example_7_mongodb_connection_options,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Available examples: 1-7")
    else:
        # Run all basic examples
        run_all_examples()

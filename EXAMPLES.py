"""
Complete Examples - Veterinary AI Assistant
Demonstrates various usage patterns and capabilities
"""

# ============================================================================
# EXAMPLE 1: Simple Interactive Analysis
# ============================================================================

def example_1_simple_analysis():
    """Run a simple analysis from command line"""
    from main import VeterinaryAIAssistant
    
    patient_text = """
    My 3-year-old golden retriever has been coughing for a week.
    He seems lethargic and has a fever. His breathing sounds labored sometimes.
    He has been fully vaccinated.
    """
    
    with VeterinaryAIAssistant() as assistant:
        result = assistant.analyze_patient_text(patient_text)
        print(assistant.generate_report(result))


# ============================================================================
# EXAMPLE 2: Using Individual Components
# ============================================================================

def example_2_component_usage():
    """Demonstrate using individual components"""
    from nlp_patient_analyzer import VeterinaryNLPAnalyzer
    from veterinary_database import VeterinaryDatabase
    from follow_up_questions import FollowUpQuestionGenerator
    
    # Step 1: Analyze text
    analyzer = VeterinaryNLPAnalyzer()
    text = "My cat has been scratching excessively for 2 weeks and has hair loss."
    result = analyzer.analyze(text)
    
    print("=== Patient Analysis ===")
    print(f"Animal: {result.patient_info.animal_type}")
    print(f"Symptoms found: {len(result.symptoms)}")
    for symptom in result.symptoms:
        print(f"  - {symptom.symptom}")
    
    # Step 2: Search database
    db = VeterinaryDatabase()
    symptom_keys = [s.symptom for s in result.symptoms]
    db_matches = db.search_by_symptoms(symptom_keys)
    
    print("\n=== Database Matches ===")
    for disease, match_count in db_matches[:3]:
        print(f"- {disease.name} ({match_count} matches)")
    
    # Step 3: Generate questions
    generator = FollowUpQuestionGenerator(db)
    questions = generator.generate_questions(
        result.patient_info,
        result.symptoms,
        result.suspected_diseases
    )
    
    print("\n=== Follow-up Questions ===")
    for i, q in enumerate(questions[:3], 1):
        print(f"{i}. {q.question}")
    
    db.close()


# ============================================================================
# EXAMPLE 3: Gastrointestinal Issue Analysis
# ============================================================================

def example_3_gastrointestinal_issue():
    """Analyze a gastrointestinal issue"""
    from main import VeterinaryAIAssistant
    
    patient_text = """
    I have a 4-year-old male Labrador Retriever weighing 75 lbs.
    He has been vomiting 3-4 times daily for 2 days.
    He also has diarrhea and seems to have abdominal pain.
    He's not eating and acts lethargic.
    He had a fever yesterday but it seems to be improving.
    We're not sure what he got into - he may have eaten something bad.
    """
    
    with VeterinaryAIAssistant() as assistant:
        result = assistant.analyze_patient_text(patient_text)
        
        # Extract specific information
        analysis = result["patient_analysis"]
        recommendations = result["recommendations"]
        
        print("=== GASTROINTESTINAL CASE ===\n")
        print(f"Patient: {analysis.patient_info.breed} ({analysis.patient_info.weight})")
        print(f"Symptoms: {len(analysis.symptoms)} identified")
        print(f"Suspected Conditions: {len(result['database_matches'])} found")
        print(f"\nUrgency: {recommendations['urgency']}")
        print("\nRecommended Actions:")
        for action in recommendations['recommended_actions'][:4]:
            print(f"  {action}")


# ============================================================================
# EXAMPLE 4: Skin Issue Analysis
# ============================================================================

def example_4_skin_issue():
    """Analyze a dermatological issue"""
    from main import VeterinaryAIAssistant
    
    patient_text = """
    My Persian cat has been having skin problems for 3 weeks.
    She's scratching constantly, especially her ears and back legs.
    There's significant hair loss in those areas.
    Her skin looks red and irritated, with some flaking.
    She seems stressed by the itching and has been less playful.
    She doesn't have any fever and is eating normally.
    """
    
    with VeterinaryAIAssistant() as assistant:
        result = assistant.analyze_patient_text(patient_text)
        
        print("=== DERMATOLOGICAL CASE ===\n")
        
        # Patient info
        patient = result["patient_analysis"].patient_info
        print(f"Patient: {patient.animal_type} - {patient.breed}")
        
        # Symptoms with details
        print("\nSymptoms with Details:")
        for symptom in result["patient_analysis"].symptoms:
            details = []
            if symptom.severity:
                details.append(f"severity: {symptom.severity}")
            if symptom.duration:
                details.append(f"duration: {symptom.duration}")
            detail_str = f" ({', '.join(details)})" if details else ""
            print(f"  • {symptom.symptom}{detail_str}")
        
        # Top 3 conditions
        print("\nTop Suspected Conditions:")
        for disease in result['database_matches'][:3]:
            print(f"  • {disease['name']} - {disease['severity']}")
            print(f"    Treatment: {disease['treatment'][:60]}...")


# ============================================================================
# EXAMPLE 5: Respiratory Issue Analysis
# ============================================================================

def example_5_respiratory_issue():
    """Analyze a respiratory issue"""
    from main import VeterinaryAIAssistant
    
    patient_text = """
    I have a 5-year-old male beagle named Max.
    He's been coughing for 10 days - sometimes it's just a few coughs,
    sometimes it's persistent.
    He has nasal discharge and his breathing seems labored at times.
    He has a low fever and isn't his usual energetic self.
    He's up to date on vaccinations.
    """
    
    with VeterinaryAIAssistant() as assistant:
        result = assistant.analyze_patient_text(patient_text)
        
        print("=== RESPIRATORY CASE ===\n")
        print("Analysis Summary:")
        print(f"  Total Symptoms: {len(result['patient_analysis'].symptoms)}")
        print(f"  Possible Conditions: {len(result['database_matches'])}")
        print(f"  Follow-up Questions: {len(result['follow_up_questions'])}")
        
        print("\nClinical Assessment:")
        print(f"  Urgency: {result['recommendations']['urgency']}")
        
        print("\nTop Questions for Patient:")
        for i, q in enumerate(result['follow_up_questions'][:3], 1):
            print(f"  {i}. {q.question}")


# ============================================================================
# EXAMPLE 6: Exporting Analysis Results
# ============================================================================

def example_6_export_results():
    """Export analysis results to JSON"""
    from main import VeterinaryAIAssistant
    
    patient_text = """
    My rabbit has been having digestive issues.
    He's not eating as much as usual and seems lethargic.
    His stool looks slightly loose.
    He's a 2-year-old male, weighs about 5 lbs.
    """
    
    with VeterinaryAIAssistant() as assistant:
        result = assistant.analyze_patient_text(patient_text)
        
        # Save analysis
        filename = "rabbit_analysis.json"
        assistant.save_analysis(result, filename)
        
        # Generate report
        report = assistant.generate_report(result)
        
        # Save report to text file
        with open("rabbit_analysis.txt", "w") as f:
            f.write(report)
        
        print(f"✓ Analysis saved to {filename}")
        print(f"✓ Report saved to rabbit_analysis.txt")


# ============================================================================
# EXAMPLE 7: Custom Analysis with Direct Component Access
# ============================================================================

def example_7_custom_analysis():
    """Custom analysis with direct component access"""
    from nlp_patient_analyzer import VeterinaryNLPAnalyzer
    from veterinary_database import VeterinaryDatabase
    
    # Your custom text
    text = """
    5-year-old dog with conjunctivitis symptoms.
    Both eyes are red and watery.
    Eyelids slightly swollen.
    Discharged started 3 days ago.
    """
    
    # Step 1: Run NLP analysis
    analyzer = VeterinaryNLPAnalyzer()
    nlp_result = analyzer.analyze(text)
    
    # Step 2: Get database matches
    db = VeterinaryDatabase()
    symptoms = [s.symptom for s in nlp_result.symptoms]
    db_matches = db.search_by_symptoms(symptoms)
    
    # Step 3: Find best match
    if db_matches:
        best_disease, match_count = db_matches[0]
        print(f"Best Match: {best_disease.name}")
        print(f"Description: {best_disease.description}")
        print(f"Treatment: {best_disease.treatment}")
        print(f"Prevention: {best_disease.prevention}")
    
    db.close()


# ============================================================================
# EXAMPLE 8: Analyzing Multiple Patients
# ============================================================================

def example_8_batch_analysis():
    """Analyze multiple patients"""
    from main import VeterinaryAIAssistant
    
    patients = [
        {
            "id": 1,
            "name": "Buddy",
            "description": "3-year-old dog with vomiting and diarrhea for 2 days. Not eating."
        },
        {
            "id": 2,
            "name": "Whiskers",
            "description": "5-year-old cat scratching excessively. Hair loss visible."
        },
        {
            "id": 3,
            "name": "Tweety",
            "description": "Bird with cough and difficulty breathing. Lethargic."
        }
    ]
    
    with VeterinaryAIAssistant() as assistant:
        for patient in patients:
            print(f"\n{'='*60}")
            print(f"Patient {patient['id']}: {patient['name']}")
            print(f"{'='*60}")
            
            result = assistant.analyze_patient_text(patient['description'])
            
            # Quick summary
            print(f"Symptoms Found: {len(result['patient_analysis'].symptoms)}")
            print(f"Possible Conditions: {len(result['database_matches'])}")
            print(f"Urgency: {result['recommendations']['urgency']}")
            
            # Save each analysis
            filename = f"patient_{patient['id']}_analysis.json"
            assistant.save_analysis(result, filename)
            print(f"Saved to: {filename}")


# ============================================================================
# EXAMPLE 9: Database Exploration
# ============================================================================

def example_9_database_exploration():
    """Explore the veterinary database"""
    from veterinary_database import VeterinaryDatabase
    
    db = VeterinaryDatabase()
    
    print("=== VETERINARY DATABASE EXPLORATION ===\n")
    
    # Get all diseases
    all_diseases = db.get_all_diseases()
    print(f"Total Diseases in Database: {len(all_diseases)}\n")
    
    # Show each disease
    for disease in all_diseases:
        print(f"Disease: {disease.name}")
        print(f"  Scientific: {disease.scientific_name}")
        print(f"  Severity: {disease.severity}")
        print(f"  Affected Species: {', '.join(disease.affected_species)}")
        print(f"  Common Symptoms: {len(disease.common_symptoms)}")
        print()
    
    # Search examples
    print("\n=== SEARCH EXAMPLES ===\n")
    
    # By name
    print("1. Search by name ('Pneumonia'):")
    disease = db.search_by_name("Pneumonia")
    if disease:
        print(f"   Found: {disease.name}")
        print(f"   Treatment: {disease.treatment[:50]}...")
    
    # By keyword
    print("\n2. Search by keyword ('infection'):")
    results = db.search_by_keyword("infection")
    print(f"   Found {len(results)} diseases")
    for disease in results:
        print(f"   • {disease.name}")
    
    # By symptoms
    print("\n3. Search by symptoms (['cough', 'fever']):")
    results = db.search_by_symptoms(['cough', 'fever'])
    print(f"   Found {len(results)} diseases")
    for disease, match_count in results[:3]:
        print(f"   • {disease.name} ({match_count} symptoms match)")
    
    db.close()


# ============================================================================
# EXAMPLE 10: Advanced Question Analysis
# ============================================================================

def example_10_advanced_questions():
    """Advanced follow-up question analysis"""
    from nlp_patient_analyzer import PatientInfo, SymptomExtraction, DiseaseExtraction
    from follow_up_questions import FollowUpQuestionGenerator
    from veterinary_database import VeterinaryDatabase
    
    db = VeterinaryDatabase()
    generator = FollowUpQuestionGenerator(db)
    
    # Create detailed patient scenario
    patient_info = PatientInfo(
        animal_type="dog",
        age="7 years old",
        breed="german shepherd",
        gender="male",
        weight="80 lbs"
    )
    
    symptoms = [
        SymptomExtraction(
            symptom="lethargy",
            duration="1 week",
            severity="moderate",
            frequency="constant",
            context="Decreased activity, sleeping more"
        ),
        SymptomExtraction(
            symptom="loss_of_appetite",
            duration="1 week",
            severity="moderate",
            frequency=None,
            context="Eating less than usual"
        ),
        SymptomExtraction(
            symptom="weight_loss",
            duration=None,
            severity=None,
            frequency=None,
            context="Owner noticed clothes not fitting well"
        )
    ]
    
    diseases = [
        DiseaseExtraction(
            disease_name="diabetes_mellitus",
            confidence=0.7,
            related_symptoms=["lethargy", "loss_of_appetite", "weight_loss"]
        )
    ]
    
    # Generate questions
    questions = generator.generate_questions(patient_info, symptoms, diseases, max_questions=10)
    
    print("=== ADVANCED QUESTION ANALYSIS ===\n")
    print(f"Patient: {patient_info.breed} ({patient_info.age})")
    print(f"Symptoms: {len(symptoms)}")
    print(f"Generated Questions: {len(questions)}\n")
    
    # Display by category
    by_category = {}
    for q in questions:
        if q.category not in by_category:
            by_category[q.category] = []
        by_category[q.category].append(q)
    
    for category, category_questions in by_category.items():
        print(f"\n[{category.replace('_', ' ').upper()}]")
        for q in category_questions:
            print(f"  • {q.question}")
            print(f"    Priority: {q.priority}/5")
    
    db.close()


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("VETERINARY AI ASSISTANT - EXAMPLES".center(70))
    print("="*70)
    
    examples = {
        "1": ("Simple Analysis", example_1_simple_analysis),
        "2": ("Component Usage", example_2_component_usage),
        "3": ("Gastrointestinal Issue", example_3_gastrointestinal_issue),
        "4": ("Skin Issue", example_4_skin_issue),
        "5": ("Respiratory Issue", example_5_respiratory_issue),
        "6": ("Export Results", example_6_export_results),
        "7": ("Custom Analysis", example_7_custom_analysis),
        "8": ("Batch Analysis", example_8_batch_analysis),
        "9": ("Database Exploration", example_9_database_exploration),
        "10": ("Advanced Questions", example_10_advanced_questions),
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}: {name}")
    print("  0: Run All Examples")
    print("  q: Quit")
    
    while True:
        choice = input("\nSelect example (0-10, q): ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
        elif choice == '0':
            for key, (name, func) in examples.items():
                print(f"\n{'='*70}\nRunning Example {key}: {name}\n{'='*70}")
                try:
                    func()
                except Exception as e:
                    print(f"Error: {e}")
        elif choice in examples:
            print(f"\n{'='*70}")
            print(f"Example {choice}: {examples[choice][0]}")
            print(f"{'='*70}\n")
            try:
                examples[choice][1]()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice")

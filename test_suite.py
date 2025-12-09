"""
Test suite and examples for the Veterinary AI Assistant
Demonstrates functionality of each component
"""

import json
from nlp_patient_analyzer import VeterinaryNLPAnalyzer
from veterinary_database import VeterinaryDatabase
from follow_up_questions import FollowUpQuestionGenerator
from main import VeterinaryAIAssistant


def test_nlp_analyzer():
    """Test the NLP patient analyzer"""
    print("\n" + "="*80)
    print("TEST 1: NLP PATIENT ANALYZER")
    print("="*80)
    
    analyzer = VeterinaryNLPAnalyzer()
    
    test_cases = [
        {
            "name": "Gastrointestinal Issue",
            "text": """
            I have a 5 year old golden retriever male weighing about 65 lbs.
            He has been vomiting and has diarrhea for the past 3 days.
            He seems lethargic and is not eating well. He appears to have stomach pain.
            He also has a slight fever.
            """
        },
        {
            "name": "Skin Issue",
            "text": """
            My 3-year-old female cat has been scratching excessively for 2 weeks.
            She has hair loss around her ears and neck, and her skin appears red.
            She weighs about 10 lbs.
            """
        },
        {
            "name": "Respiratory Issue",
            "text": """
            I have a 2-year-old male beagle. He's been coughing constantly for a week.
            He seems lethargic and has a fever. He's also having difficulty breathing sometimes.
            """
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        result = analyzer.analyze(test_case['text'])
        print(analyzer.format_analysis_report(result))


def test_database():
    """Test the veterinary database"""
    print("\n" + "="*80)
    print("TEST 2: VETERINARY DATABASE (MongoDB)")
    print("="*80)
    
    db = VeterinaryDatabase()  # Uses default MongoDB connection
    
    # Test 1: Search by symptoms
    print("\n[Search by Symptoms: 'vomiting' and 'diarrhea']")
    results = db.search_by_symptoms(['vomiting', 'diarrhea'])
    for disease, match_count in results[:3]:
        print(f"  • {disease.name} ({match_count} symptoms match)")
        print(f"    Severity: {disease.severity}")
    
    # Test 2: Search by name
    print("\n[Search by Name: 'Parvovirus']")
    disease = db.search_by_name("Parvovirus")
    if disease:
        print(f"  Found: {disease.name}")
        print(f"  Scientific Name: {disease.scientific_name}")
        print(f"  Severity: {disease.severity}")
        print(f"  Treatment: {disease.treatment}")
    
    # Test 3: Keyword search
    print("\n[Keyword Search: 'infection']")
    results = db.search_by_keyword("infection")
    print(f"  Found {len(results)} diseases:")
    for disease in results[:3]:
        print(f"    • {disease.name}")
    
    # Test 4: Get all diseases
    print("\n[All Diseases in Database]")
    all_diseases = db.get_all_diseases()
    print(f"  Total diseases: {len(all_diseases)}")
    for disease in all_diseases[:5]:
        print(f"    • {disease.name} (Severity: {disease.severity})")
    
    db.close()


def test_follow_up_questions():
    """Test follow-up question generation"""
    print("\n" + "="*80)
    print("TEST 3: FOLLOW-UP QUESTION GENERATOR")
    print("="*80)
    
    from nlp_patient_analyzer import PatientInfo, SymptomExtraction, DiseaseExtraction
    
    patient_info = PatientInfo(
        animal_type="dog",
        age="5 years old",
        breed="labrador",
        gender="male",
        weight="65 lbs"
    )
    
    symptoms = [
        SymptomExtraction(
            symptom="vomiting",
            duration="3 days",
            severity="moderate",
            frequency=None,
            context="Vomiting once per day"
        ),
        SymptomExtraction(
            symptom="diarrhea",
            duration="3 days",
            severity=None,
            frequency="intermittent",
            context="Loose stools throughout the day"
        ),
        SymptomExtraction(
            symptom="lethargy",
            duration=None,
            severity="moderate",
            frequency=None,
            context="Not his usual self"
        )
    ]
    
    diseases = [
        DiseaseExtraction(
            disease_name="gastroenteritis",
            confidence=0.85,
            related_symptoms=["vomiting", "diarrhea"]
        ),
        DiseaseExtraction(
            disease_name="pancreatitis",
            confidence=0.65,
            related_symptoms=["vomiting", "abdominal_pain"]
        )
    ]
    
    db = VeterinaryDatabase()
    generator = FollowUpQuestionGenerator(db)
    questions = generator.generate_questions(patient_info, symptoms, diseases, max_questions=8)
    
    print(generator.format_questions_for_display(questions))
    
    db.close()


def test_complete_workflow():
    """Test complete analysis workflow"""
    print("\n" + "="*80)
    print("TEST 4: COMPLETE ANALYSIS WORKFLOW")
    print("="*80)
    
    sample_texts = [
        """
        I have a 7-year-old female Persian cat named Bella. She weighs about 8 lbs.
        For the past week, she's been having difficulty eating and seems to have lost weight.
        She's not her usual active self - just lying around most of the day.
        She also has some watery discharge from her eyes.
        """,
        """
        My 2-year-old male German Shepherd has been having issues for about 5 days.
        He's been coughing a lot, especially at night. Sometimes his breathing seems labored.
        He has a fever and doesn't seem interested in his usual activities.
        He weighs about 75 lbs and is fully vaccinated.
        """
    ]
    
    with VeterinaryAIAssistant() as assistant:
        for i, patient_text in enumerate(sample_texts, 1):
            print(f"\n{'='*80}")
            print(f"CASE {i}")
            print(f"{'='*80}")
            
            result = assistant.analyze_patient_text(patient_text)
            report = assistant.generate_report(result)
            print(report)
            
            # Save to JSON
            filename = f"analysis_case_{i}.json"
            assistant.save_analysis(result, filename)


def test_symptom_extraction():
    """Test detailed symptom extraction"""
    print("\n" + "="*80)
    print("TEST 5: DETAILED SYMPTOM EXTRACTION")
    print("="*80)
    
    analyzer = VeterinaryNLPAnalyzer()
    
    text = """
    The patient presented with severe vomiting for 2 days, occurring 3-4 times daily.
    Additionally, the patient has diarrhea that appears to be getting worse.
    The animal has moderate fever and abdominal pain.
    Loss of appetite was noted. The patient seems moderately lethargic.
    """
    
    result = analyzer.analyze(text)
    
    print("\nExtracted Symptoms with Details:")
    print("-" * 80)
    for symptom in result.symptoms:
        print(f"\nSymptom: {symptom.symptom.replace('_', ' ').title()}")
        if symptom.duration:
            print(f"  Duration: {symptom.duration}")
        if symptom.severity:
            print(f"  Severity: {symptom.severity}")
        if symptom.frequency:
            print(f"  Frequency: {symptom.frequency}")
        if symptom.context:
            print(f"  Context: {symptom.context[:100]}...")


def test_disease_matching():
    """Test disease matching algorithm"""
    print("\n" + "="*80)
    print("TEST 6: DISEASE MATCHING ALGORITHM")
    print("="*80)
    
    analyzer = VeterinaryNLPAnalyzer()
    
    test_texts = [
        "Severe vomiting, diarrhea, lethargy, and loss of appetite in an unvaccinated puppy",
        "Chronic itching, hair loss, and red skin especially on paws",
        "Hacking cough, labored breathing, fever, and nasal discharge"
    ]
    
    for text in test_texts:
        print(f"\nInput: {text}")
        result = analyzer.analyze(text)
        
        print("Suspected Diseases:")
        for disease in result.suspected_diseases[:3]:
            confidence = disease.confidence * 100
            print(f"  • {disease.disease_name.title()} ({confidence:.1f}% confidence)")
            if disease.related_symptoms:
                print(f"    Related symptoms: {', '.join(disease.related_symptoms)}")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("#" * 80)
    print("VETERINARY AI ASSISTANT - COMPREHENSIVE TEST SUITE".center(80))
    print("#" * 80)
    
    try:
        test_nlp_analyzer()
        test_database()
        test_follow_up_questions()
        test_symptom_extraction()
        test_disease_matching()
        test_complete_workflow()
        
        print("\n" + "#" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY".center(80))
        print("#" * 80)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

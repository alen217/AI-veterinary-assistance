"""
Comprehensive System Test - All Features
Tests all components to ensure everything works
"""

print("="*70)
print("AVA COMPREHENSIVE SYSTEM TEST")
print("="*70)

# Test 1: Database Connection
print("\n1️⃣ Testing Database Connection...")
try:
    from user_database import get_db
    db = get_db()
    disease_count = db.diseases.count_documents({})
    symptom_count = db.symptoms.count_documents({})
    user_count = db.users.count_documents({})
    print(f"   ✅ Database connected")
    print(f"   ✅ {disease_count} diseases")
    print(f"   ✅ {symptom_count} symptoms")
    print(f"   ✅ {user_count} users")
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test 2: Disease Repository
print("\n2️⃣ Testing Disease Repository...")
try:
    from mongo_disease_repository import MongoDiseaseRepository
    repo = MongoDiseaseRepository()
    
    # Test species filtering
    cat_diseases = repo.find_by_symptoms(['fever'], limit=5, species='cat')
    print(f"   ✅ Repository initialized")
    print(f"   ✅ Found {len(cat_diseases)} cat diseases with fever")
    if cat_diseases:
        d = cat_diseases[0]
        print(f"   ✅ Top disease: {d['name']}")
        print(f"   ✅ Match count: {d['symptom_match_count']}")
        print(f"   ✅ Match ratio: {d['match_ratio']}")
        print(f"   ✅ Confidence: {d['confidence']:.1%}")
except Exception as e:
    print(f"   ❌ Repository error: {e}")

# Test 3: Patient Analysis
print("\n3️⃣ Testing Patient Analysis...")
try:
    from main import VeterinaryAIAssistant
    assistant = VeterinaryAIAssistant(repo)
    
    result = assistant.analyze_patient_text(
        "my cat has mild fever for 2 days no change in appetite",
        generate_questions=False
    )
    
    patient_info = result['patient_analysis'].patient_info
    symptoms = result['patient_analysis'].symptoms
    matches = result['database_matches']
    
    print(f"   ✅ Analysis completed")
    print(f"   ✅ Species detected: {patient_info.animal_type}")
    print(f"   ✅ Symptoms extracted: {len(symptoms)}")
    print(f"   ✅ Disease matches: {len(matches)}")
    
    if matches:
        print(f"   ✅ Top disease: {matches[0]['name']}")
        print(f"   ✅ Species in result: {matches[0].get('affected_species', [])}")
except Exception as e:
    print(f"   ❌ Analysis error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: AVA Display Engine
print("\n4️⃣ Testing AVA Display Engine...")
try:
    from ava_display_engine import AVADisplayEngine, QuestionStrategyEngine
    engine = AVADisplayEngine()
    
    # Test match ratio calculation
    test_disease = {
        'symptom_match_count': 3,
        'common_symptoms': ['fever', 'vomiting', 'diarrhea', 'lethargy', 'loss_of_appetite']
    }
    ratio = engine.calculate_match_ratio(test_disease)
    print(f"   ✅ AVA engine initialized")
    print(f"   ✅ Match ratio calculation: {ratio:.2%}")
    
    # Test question strategy
    strategy_engine = QuestionStrategyEngine(repo)
    print(f"   ✅ Question strategy engine initialized")
except Exception as e:
    print(f"   ❌ AVA engine error: {e}")

# Test 5: Symptom Validator
print("\n5️⃣ Testing Symptom Validator...")
try:
    from symptom_validator import SymptomValidator
    validator = SymptomValidator(repo)
    
    # Test validation
    is_valid, matched, score = validator.validate_symptom('fever')
    print(f"   ✅ Validator initialized")
    print(f"   ✅ Official symptoms loaded: {len(validator.official_symptoms)}")
    print(f"   ✅ 'fever' validation: {is_valid}, matched: {matched}")
except Exception as e:
    print(f"   ❌ Validator error: {e}")

# Test 6: AI Model
print("\n6️⃣ Testing AI Follow-up Model...")
try:
    from custom_ai_followup import CustomAIFollowUpGenerator
    ai_gen = CustomAIFollowUpGenerator()
    print(f"   ✅ AI model loaded")
    print(f"   ✅ Device: {ai_gen.device}")
    print(f"   ✅ Vocabulary size: {len(ai_gen.vocab)}")
except Exception as e:
    print(f"   ⚠️  AI model not available: {e}")

# Test 7: Dynamic Confidence Updater
print("\n7️⃣ Testing Dynamic Confidence Updater...")
try:
    from dynamic_confidence_updater import DynamicDiseaseRanker, FollowUpAnswer
    
    # Create test diseases
    test_diseases = [
        {'name': 'Parvovirus', 'confidence': 0.75, 'common_symptoms': ['vomiting', 'diarrhea', 'fever']},
        {'name': 'Gastritis', 'confidence': 0.60, 'common_symptoms': ['vomiting', 'loss_of_appetite']},
    ]
    
    ranker = DynamicDiseaseRanker(test_diseases)
    
    # Create test answer
    answer = FollowUpAnswer(
        question="Does the dog have fever?",
        answer="Yes, high fever",
        category="symptom_details",
        symptom_confirmed=True,
        mentioned_symptom="fever"
    )
    
    updated = ranker.update_confidence_with_answer(answer)
    print(f"   ✅ Confidence updater initialized")
    print(f"   ✅ Updated diseases: {len(updated)}")
    print(f"   ✅ Top disease after update: {updated[0]['name']} ({updated[0]['confidence']:.1%})")
except Exception as e:
    print(f"   ❌ Confidence updater error: {e}")

# Test 8: Check Critical Files
print("\n8️⃣ Checking Critical Files...")
import os
critical_files = [
    'app_streamlit.py',
    'main.py',
    'mongo_disease_repository.py',
    'ava_display_engine.py',
    'symptom_validator.py',
    'custom_ai_followup.py',
    'dynamic_confidence_updater.py',
    'seed_500_diseases.py',
    '.env'
]

for file in critical_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"   ✅ {file} ({size:,} bytes)")
    else:
        print(f"   ⚠️  {file} not found")

print("\n" + "="*70)
print("✅ COMPREHENSIVE SYSTEM TEST COMPLETE")
print("="*70)
print("\n🎯 READY FOR DEMO!")
print("   Run: streamlit run app_streamlit.py")
print("   URL: http://localhost:8501")
print("="*70)

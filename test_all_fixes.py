"""
Test script to verify all fixes are working correctly
Tests both disease priority scoring and AI question generation
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_disease_priority():
    """Test the fixed disease priority scoring"""
    print("="*70)
    print("TEST 1: DISEASE PRIORITY SCORING")
    print("="*70 + "\n")
    
    from mongo_disease_repository import MongoDiseaseRepository
    
    try:
        repo = MongoDiseaseRepository()
        
        # Test with common symptoms
        test_symptoms = ["vomiting", "diarrhea", "lethargy"]
        
        print(f"🔍 Searching for diseases matching: {test_symptoms}\n")
        results = repo.find_by_symptoms(test_symptoms, limit=5)
        
        if results:
            print("✅ Disease matches found with confidence scores:\n")
            for i, disease in enumerate(results, 1):
                name = disease.get('name', 'Unknown')
                confidence = disease.get('confidence', 0.0)
                match_count = disease.get('symptom_match_count', 0)
                severity = disease.get('severity', 'unknown')
                
                print(f"{i}. {name}")
                print(f"   Confidence: {confidence:.1%} ({confidence:.3f})")
                print(f"   Matched Symptoms: {match_count}/{len(test_symptoms)}")
                print(f"   Severity: {severity}")
                print()
            
            # Verify scoring is working
            if results[0]['confidence'] > 0:
                print("✅ Disease priority scoring is working correctly!")
                return True
            else:
                print("❌ Disease confidence scores are 0 - check scoring algorithm")
                return False
        else:
            print("⚠️  No diseases found in database")
            print("   Make sure your MongoDB is populated with disease data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing disease priority: {e}")
        return False


def test_ai_model_exists():
    """Check if AI model is trained"""
    print("\n" + "="*70)
    print("TEST 2: CUSTOM AI MODEL STATUS")
    print("="*70 + "\n")
    
    model_paths = [
        "ml_training/vet_followup_qa/vet_followup_model.pth",
        "vet_followup_model.pth"
    ]
    
    model_found = False
    for path in model_paths:
        if os.path.exists(path):
            model_found = True
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"✅ Model found: {path}")
            print(f"   Size: {size_mb:.1f} MB")
            break
    
    if not model_found:
        print("⚠️  Model not found. You need to train it first:")
        print("   cd ml_training/vet_followup_qa")
        print("   python train.py")
        return False
    
    return True


def test_ai_question_generation():
    """Test AI question generation if model is available"""
    print("\n" + "="*70)
    print("TEST 3: AI QUESTION GENERATION")
    print("="*70 + "\n")
    
    try:
        from custom_ai_followup import CustomAIFollowUpGenerator
        
        # Initialize generator
        print("🤖 Initializing custom AI generator...")
        generator = CustomAIFollowUpGenerator()
        
        # Test data
        patient_info = {
            "animal_type": "dog",
            "age": "5 years",
            "weight": "70 lbs"
        }
        
        symptoms = [
            {
                "symptom": "vomiting",
                "duration": "2 days",
                "severity": "moderate",
                "frequency": None
            },
            {
                "symptom": "lethargy",
                "duration": None,
                "severity": None,
                "frequency": None
            }
        ]
        
        database_matches = [
            {
                "name": "Gastroenteritis",
                "confidence": 0.78
            }
        ]
        
        print("📝 Generating questions for test case...")
        print(f"   Animal: {patient_info['animal_type']}, {patient_info['age']}")
        print(f"   Symptoms: vomiting (2 days, moderate), lethargy\n")
        
        questions = generator.generate_questions(
            patient_info=patient_info,
            symptoms=symptoms,
            suspected_diseases=[],
            database_matches=database_matches,
            max_questions=5
        )
        
        if questions:
            print(f"✅ Generated {len(questions)} questions:\n")
            for i, q in enumerate(questions, 1):
                priority_str = "⚠️ CRITICAL" if q.priority >= 5 else "⭐ HIGH" if q.priority >= 4 else "○ MODERATE"
                print(f"{i}. {q.question}")
                print(f"   {priority_str} | {q.reasoning}")
                print()
            
            print("✅ AI question generation is working correctly!")
            return True
        else:
            print("❌ No questions generated")
            return False
            
    except FileNotFoundError as e:
        print(f"⚠️  Model not trained yet: {e}")
        print("\nTo train the model:")
        print("   cd ml_training/vet_followup_qa")
        print("   python train.py")
        return False
    except Exception as e:
        print(f"❌ Error testing AI generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_integration():
    """Test full integration with VeterinaryAIAssistant"""
    print("\n" + "="*70)
    print("TEST 4: FULL SYSTEM INTEGRATION")
    print("="*70 + "\n")
    
    try:
        from main import VeterinaryAIAssistant
        
        print("🏥 Initializing VeterinaryAIAssistant...")
        assistant = VeterinaryAIAssistant()
        
        # Test case
        patient_text = "My 5 year old Golden Retriever has been vomiting for 2 days and seems very tired"
        
        print(f"\n📋 Test Case:")
        print(f'   "{patient_text}"\n')
        
        print("🔄 Analyzing patient...")
        result = assistant.analyze_patient_text(patient_text)
        
        # Check results
        print("\n✅ Analysis Complete!\n")
        
        # Disease matches
        if result['database_matches']:
            print("🔬 Top Disease Matches:")
            for disease in result['database_matches'][:3]:
                print(f"   - {disease['name']}: {disease['confidence']:.1%} confidence")
        
        # Questions
        print(f"\n❓ Follow-up Questions ({result['question_source']}):")
        for i, q in enumerate(result['follow_up_questions'][:3], 1):
            if hasattr(q, 'question'):
                print(f"   {i}. {q.question}")
            else:
                print(f"   {i}. {q}")
        
        print("\n✅ Full system integration is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error in full integration test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 " * 35)
    print("COMPREHENSIVE SYSTEM TEST")
    print("Testing Disease Priority & AI Question Generation")
    print("🧪 " * 35 + "\n")
    
    results = {
        "Disease Priority Scoring": test_disease_priority(),
        "AI Model Status": test_ai_model_exists(),
        "AI Question Generation": test_ai_question_generation(),
        "Full Integration": test_full_integration()
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your system is ready to use!")
    elif passed >= 2:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("   The system will work but may fall back to template questions.")
    else:
        print("❌ Multiple tests failed. Please check:")
        print("   1. MongoDB connection (for disease data)")
        print("   2. Train AI model: cd ml_training/vet_followup_qa && python train.py")
    
    print()


if __name__ == "__main__":
    main()

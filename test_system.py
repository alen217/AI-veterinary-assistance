"""
Complete System Test - Check All Components
"""
import sys
import os

def test_dependencies():
    """Test all required dependencies"""
    print("\n" + "="*60)
    print("1. TESTING DEPENDENCIES")
    print("="*60)
    
    results = []
    
    # Python
    try:
        print(f"✅ Python: {sys.version.split()[0]}")
        results.append(("Python", True))
    except Exception as e:
        print(f"❌ Python: {e}")
        results.append(("Python", False))
    
    # PyTorch
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        results.append(("PyTorch", True))
    except Exception as e:
        print(f"❌ PyTorch: {e}")
        results.append(("PyTorch", False))
    
    # Whisper
    try:
        import whisper
        print(f"✅ OpenAI Whisper: Installed")
        results.append(("Whisper", True))
    except Exception as e:
        print(f"❌ Whisper: {e}")
        results.append(("Whisper", False))
    
    # MongoDB
    try:
        import pymongo
        print(f"✅ PyMongo: {pymongo.version}")
        results.append(("PyMongo", True))
    except Exception as e:
        print(f"❌ PyMongo: {e}")
        results.append(("PyMongo", False))
    
    # Streamlit
    try:
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
        results.append(("Streamlit", True))
    except Exception as e:
        print(f"❌ Streamlit: {e}")
        results.append(("Streamlit", False))
    
    # spaCy (optional)
    try:
        import spacy
        print(f"✅ spaCy: {spacy.__version__}")
        results.append(("spaCy", True))
    except Exception as e:
        print(f"⚠️  spaCy: Not installed (optional)")
        results.append(("spaCy", False))
    
    return results

def test_models():
    """Test AI models are loadable"""
    print("\n" + "="*60)
    print("2. TESTING AI MODELS")
    print("="*60)
    
    results = []
    
    # Custom Follow-Up Model
    try:
        from custom_ai_followup import CustomAIFollowUpGenerator, MODEL_AVAILABLE
        if MODEL_AVAILABLE:
            print("✅ Custom Follow-Up Model: Available")
            results.append(("Custom Model", True))
        else:
            print("❌ Custom Follow-Up Model: Not found")
            results.append(("Custom Model", False))
    except Exception as e:
        print(f"❌ Custom Follow-Up Model: {e}")
        results.append(("Custom Model", False))
    
    # Whisper Medium Model
    try:
        import whisper
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Loading Whisper medium model on {device}...")
        model = whisper.load_model("medium", device=device)
        print(f"✅ Whisper Medium Model: Loaded successfully")
        print(f"   Parameters: {sum(p.numel() for p in model.parameters())/1e6:.0f}M")
        results.append(("Whisper Medium", True))
    except Exception as e:
        print(f"❌ Whisper Medium Model: {e}")
        results.append(("Whisper Medium", False))
    
    return results

def test_database():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("3. TESTING DATABASE CONNECTION")
    print("="*60)
    
    results = []
    
    try:
        from user_database import get_db
        db = get_db()
        
        # Test connection
        disease_count = db.diseases.count_documents({})
        user_count = db.users.count_documents({})
        
        print(f"✅ MongoDB: Connected")
        print(f"   Database: veterinary_ai_db")
        print(f"   Diseases: {disease_count}")
        print(f"   Users: {user_count}")
        results.append(("MongoDB", True))
    except Exception as e:
        print(f"❌ MongoDB: {e}")
        results.append(("MongoDB", False))
    
    return results

def test_core_modules():
    """Test core module imports"""
    print("\n" + "="*60)
    print("4. TESTING CORE MODULES")
    print("="*60)
    
    results = []
    
    modules = [
        ("voice_input", "Voice Input Handler"),
        ("custom_ai_followup", "AI Follow-Up Generator"),
        ("nlp_patient_analyzer", "NLP Patient Analyzer"),
        ("mongo_disease_repository", "Disease Repository"),
        ("dynamic_confidence_updater", "Confidence Updater"),
        ("ava_display_engine", "AVA Display Engine"),
        ("symptom_validator", "Symptom Validator"),
    ]
    
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}: OK")
            results.append((display_name, True))
        except Exception as e:
            print(f"❌ {display_name}: {e}")
            results.append((display_name, False))
    
    return results

def test_algorithms():
    """Quick algorithm verification"""
    print("\n" + "="*60)
    print("5. TESTING ALGORITHMS")
    print("="*60)
    
    results = []
    
    try:
        from mongo_disease_repository import MongoDiseaseRepository
        
        # Test symptom matching
        repo = MongoDiseaseRepository()
        # Use simple symptom list (strings)
        symptoms = ["vomiting", "diarrhea", "lethargy"]
        
        matches = repo.find_by_symptoms(symptoms, species="dog", limit=5)
        
        if len(matches) > 0:
            print(f"✅ Symptom Matching: Working")
            print(f"   Found {len(matches)} diseases")
            print(f"   Top disease: {matches[0].get('name', 'Unknown')}")
            print(f"   Confidence: {matches[0].get('confidence', 0):.1%}")
            results.append(("Symptom Matching", True))
        else:
            print(f"⚠️  Symptom Matching: No results (database may be empty)")
            results.append(("Symptom Matching", False))
            
    except Exception as e:
        print(f"❌ Symptom Matching: {e}")
        results.append(("Symptom Matching", False))
    
    return results

def test_voice_input():
    """Test voice input availability"""
    print("\n" + "="*60)
    print("6. TESTING VOICE INPUT")
    print("="*60)
    
    results = []
    
    try:
        from voice_input import WHISPER_AVAILABLE, AUDIO_RECORDER_AVAILABLE
        
        if WHISPER_AVAILABLE:
            print("✅ Whisper: Available")
            results.append(("Whisper", True))
        else:
            print("❌ Whisper: Not available")
            results.append(("Whisper", False))
        
        if AUDIO_RECORDER_AVAILABLE:
            print("✅ Audio Recorder: Available")
            results.append(("Audio Recorder", True))
        else:
            print("⚠️  Audio Recorder: Not available (install audio-recorder-streamlit)")
            results.append(("Audio Recorder", False))
            
    except Exception as e:
        print(f"❌ Voice Input: {e}")
        results.append(("Voice Input", False))
    
    return results

def main():
    print("\n" + "🔍 AVA SYSTEM TEST - COMPREHENSIVE CHECK")
    print("="*60)
    
    all_results = []
    
    # Run all tests
    all_results.extend(test_dependencies())
    all_results.extend(test_models())
    all_results.extend(test_database())
    all_results.extend(test_core_modules())
    all_results.extend(test_algorithms())
    all_results.extend(test_voice_input())
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, status in all_results if status)
    total = len(all_results)
    
    print(f"\n✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - SYSTEM READY! ✅")
        return 0
    elif passed >= total * 0.8:
        print(f"\n⚠️  MOSTLY WORKING - {total - passed} issues found")
        return 1
    else:
        print(f"\n❌ CRITICAL ISSUES - {total - passed} tests failed")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

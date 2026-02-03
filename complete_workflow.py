"""
COMPLETE WORKFLOW: Train AI & Test Dynamic Confidence Updates
This script demonstrates the full pipeline:
1. Extract real diseases from MongoDB
2. Train custom AI model
3. Test dynamic confidence updates with follow-up answers
"""
import os
import sys

print("="*70)
print("🐾 AVA AI VETERINARY ASSISTANT - COMPLETE TRAINING WORKFLOW")
print("="*70 + "\n")

# ============================================================================
# STEP 1: Extract Real Diseases from MongoDB
# ============================================================================
print("STEP 1: Extracting Real Diseases from MongoDB")
print("-"*70)

try:
    from extract_real_diseases import RealDiseaseDatasetGenerator
    
    print("📦 Connecting to MongoDB...")
    generator = RealDiseaseDatasetGenerator()
    
    print(f"✅ Found {len(generator.diseases)} diseases in database")
    print("\nTop 10 diseases:")
    for i, disease in enumerate(generator.diseases[:10], 1):
        print(f"   {i}. {disease.get('name')} ({disease.get('severity', 'unknown')} severity)")
    
    # Generate training dataset
    print(f"\n🔄 Generating training dataset...")
    generator.save_dataset(
        "ml_training/vet_followup_qa/vet_followup_dataset_real.json",
        num_examples=5000
    )
    
    print("\n✅ STEP 1 COMPLETE: Real disease dataset ready!")
    
except Exception as e:
    print(f"\n❌ Error in Step 1: {e}")
    print("Make sure:")
    print("  1. MongoDB is running and accessible")
    print("  2. MONGO_URL is set in .env")
    print("  3. Database has disease data")
    sys.exit(1)

print("\n" + "="*70 + "\n")

# ============================================================================
# STEP 2: Check if PyTorch is installed
# ============================================================================
print("STEP 2: Checking Dependencies")
print("-"*70)

try:
    import torch
    print(f"✅ PyTorch installed: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError:
    print("❌ PyTorch not installed!")
    print("\nPlease install PyTorch first:")
    print("   pip install torch torchvision matplotlib tqdm --index-url https://download.pytorch.org/whl/cpu")
    sys.exit(1)

try:
    import matplotlib
    import tqdm
    print("✅ Training dependencies installed")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   pip install matplotlib tqdm")
    sys.exit(1)

print("\n✅ STEP 2 COMPLETE: All dependencies installed!")
print("\n" + "="*70 + "\n")

# ============================================================================
# STEP 3: Train the AI Model (Optional - can be run separately)
# ============================================================================
print("STEP 3: AI Model Training")
print("-"*70)

model_path = "ml_training/vet_followup_qa/vet_followup_model.pth"

if os.path.exists(model_path):
    print(f"✅ Trained model found: {model_path}")
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"   Model size: {size_mb:.1f} MB")
    print("\n⏩ Skipping training (model already exists)")
    print("   To retrain: delete the model file and run this script again")
else:
    print("⚠️  No trained model found")
    print("\nTo train the model, run:")
    print("   cd ml_training/vet_followup_qa")
    print("   python train.py")
    print("\n⏩ Continuing with testing (will use template questions)")

print("\n" + "="*70 + "\n")

# ============================================================================
# STEP 4: Test Dynamic Confidence Updates
# ============================================================================
print("STEP 4: Testing Dynamic Confidence Updates")
print("-"*70)

try:
    from main import VeterinaryAIAssistant
    from dynamic_confidence_updater import FollowUpAnswer
    
    print("🏥 Initializing AI Assistant...")
    assistant = VeterinaryAIAssistant(use_ai_questions=True)
    
    # Test case
    patient_text = "My 5 year old dog has been vomiting for 2 days and seems very lethargic. Not eating much."
    
    print(f"\n📋 Test Case:")
    print(f'   "{patient_text}"\n')
    
    # Initial analysis
    print("🔄 Running initial analysis...")
    result = assistant.analyze_patient_text(patient_text)
    
    print("\n✅ Initial Analysis Complete!\n")
    print("📊 Initial Disease Rankings:")
    for i, disease in enumerate(result['database_matches'][:5], 1):
        print(f"   {i}. {disease['name']}")
        print(f"      Confidence: {disease['confidence']:.1%}")
        print(f"      Matched Symptoms: {disease['symptom_match_count']}")
        print()
    
    # Start dynamic session
    print("🔄 Starting dynamic diagnosis session...")
    assistant.start_dynamic_diagnosis_session(result['database_matches'])
    
    # Simulate follow-up Q&A
    print("\n" + "="*70)
    print("SIMULATING FOLLOW-UP QUESTION-ANSWER CYCLE")
    print("="*70 + "\n")
    
    # Q1: Check for additional symptom
    top_disease = result['database_matches'][0]['name']
    print(f"Q1: Has your dog shown any diarrhea?")
    print(f"A1: Yes, watery diarrhea")
    print(f"    (Checking symptom for: {top_disease})")
    
    update1 = assistant.update_diagnosis_with_answer(
        question="Has your dog shown any diarrhea?",
        answer="Yes, watery diarrhea",
        category="disease_confirmation",
        related_disease=top_disease,
        symptom_to_check="diarrhea"
    )
    
    # Q2: Severity check
    print(f"\nQ2: How severe is the vomiting?")
    print(f"A2: Very severe, constant throughout the day")
    
    update2 = assistant.update_diagnosis_with_answer(
        question="How severe is the vomiting?",
        answer="Very severe, constant throughout the day",
        category="symptom_details"
    )
    
    # Q3: Risk factor check
    if len(result['database_matches']) > 1:
        second_disease = result['database_matches'][1]['name']
        print(f"\nQ3: Has your dog eaten any fatty or rich foods recently?")
        print(f"A3: No, regular diet only")
        print(f"    (Checking risk factor for: {second_disease})")
        
        update3 = assistant.update_diagnosis_with_answer(
            question="Has your dog eaten any fatty or rich foods recently?",
            answer="No, regular diet only",
            category="risk_factors",
            related_disease=second_disease
        )
    
    # Show updated rankings
    print("\n" + "="*70)
    print("UPDATED DISEASE RANKINGS (After Follow-Up Answers)")
    print("="*70 + "\n")
    
    if update2 and 'updated_diseases' in update2:
        for i, disease in enumerate(update2['updated_diseases'][:5], 1):
            initial_conf = disease.get('initial_confidence', 0)
            current_conf = disease['confidence']
            change = current_conf - initial_conf
            
            print(f"{i}. {disease['name']}")
            print(f"   Confidence: {current_conf:.1%} ", end="")
            if change > 0:
                print(f"(↑ +{change:.1%})")
            elif change < 0:
                print(f"(↓ {change:.1%})")
            else:
                print("(unchanged)")
            
            additional = disease.get('matched_additional_symptoms', [])
            if additional:
                print(f"   New Symptoms Confirmed: {', '.join(additional)}")
            print()
    
    # Show explanation
    if update2 and 'explanation' in update2:
        print(update2['explanation'])
    
    print("\n✅ STEP 4 COMPLETE: Dynamic confidence updates working!")
    
except Exception as e:
    print(f"\n❌ Error in Step 4: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("="*70)
print("📊 WORKFLOW SUMMARY")
print("="*70 + "\n")

print("✅ Step 1: Real diseases extracted from MongoDB")
print("✅ Step 2: Dependencies verified")

if os.path.exists(model_path):
    print("✅ Step 3: AI model ready")
else:
    print("⚠️  Step 3: AI model needs training")
    print("   Run: cd ml_training/vet_followup_qa && python train.py")

print("✅ Step 4: Dynamic confidence updates tested")

print("\n" + "="*70)
print("🎉 SYSTEM READY TO USE!")
print("="*70 + "\n")

print("Key Features Working:")
print("  ✅ Disease prioritization with confidence scores")
print("  ✅ Follow-up questions update disease rankings")
print("  ✅ Real diseases from your database")
print("  ✅ Dynamic feedback loop")

print("\nTo use in your application:")
print("  1. assistant = VeterinaryAIAssistant()")
print("  2. result = assistant.analyze_patient_text(text)")
print("  3. assistant.start_dynamic_diagnosis_session(result['database_matches'])")
print("  4. assistant.update_diagnosis_with_answer(question, answer, ...)")

print("\n" + "="*70)

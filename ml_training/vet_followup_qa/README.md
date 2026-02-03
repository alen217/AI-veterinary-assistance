# Custom AI Follow-Up Question Generator

## Overview
This system uses a **custom-trained transformer neural network** to generate intelligent, contextual follow-up questions for veterinary cases. NO external APIs required - everything runs locally!

## Architecture

### Model Components
1. **Context Encoder** (Bidirectional LSTM)
   - Encodes patient information and symptoms
   - Captures semantic relationships in veterinary context
   
2. **Question Decoder** (LSTM with Attention)
   - Generates natural language questions
   - Attention mechanism focuses on relevant context
   
3. **Vocabulary Builder**
   - Custom veterinary vocabulary (5000+ words)
   - Special tokens for start/end/padding

### Training Data
- **5000+ synthetic veterinary cases**
- Covers 8 major symptom categories
- 5 common disease patterns
- Multiple animal types (dogs, cats, rabbits, etc.)

## Training the Model

### Prerequisites
```bash
cd AI-veterinary-assistance
pip install -r requirements.txt
```

### Generate Training Data & Train Model
```bash
cd ml_training/vet_followup_qa
python train.py
```

This will:
1. Generate 5000 training examples
2. Build vocabulary from data
3. Train transformer model for 50 epochs
4. Save best model as `vet_followup_model.pth`
5. Create training curve visualization

**Training Time:** ~30-60 minutes on CPU, ~10 minutes on GPU

### Model Parameters
- **Vocabulary Size:** ~3000-5000 words
- **Embedding Dimension:** 256
- **Hidden Dimension:** 512
- **Parameters:** ~8-10 million
- **Model Size:** ~80-100 MB

## Usage

### In Main Application
```python
from custom_ai_followup import CustomAIFollowUpGenerator

# Initialize (automatically loads trained model)
generator = CustomAIFollowUpGenerator()

# Generate questions
questions = generator.generate_questions(
    patient_info={"animal_type": "dog", "age": "5 years"},
    symptoms=[{"symptom": "vomiting", "duration": "2 days"}],
    suspected_diseases=[],
    database_matches=[],
    max_questions=5
)

# Display
print(generator.format_questions_for_display(questions))
```

### Integration with VeterinaryAIAssistant
The system automatically uses the custom AI if the model is trained:

```python
# In main.py
assistant = VeterinaryAIAssistant(use_ai_questions=True)  # Uses custom AI
result = assistant.analyze_patient_text("My dog has been vomiting...")
```

## Features

### Intelligent Question Generation
- ✅ **Context-aware:** Questions adapt to patient symptoms
- ✅ **Priority-based:** Critical questions asked first
- ✅ **Missing info detection:** Identifies gaps in patient history
- ✅ **Disease-specific:** Asks relevant questions for suspected conditions
- ✅ **Natural language:** Human-readable, professional questions

### Priority System
- **Priority 5 (CRITICAL):** Duration, blood presence, breathing
- **Priority 4 (HIGH):** Severity, frequency, appetite
- **Priority 3 (MODERATE):** Additional symptoms, history
- **Priority 2 (LOW):** Environmental factors

## Model Performance

### Metrics (After Training)
- Train Loss: < 2.0
- Validation Loss: < 2.5
- Generated questions are grammatically correct
- High contextual relevance

### Quality Checks
1. **Grammar:** Natural, professional language
2. **Relevance:** Questions match patient context
3. **Diversity:** No duplicate questions
4. **Coverage:** Addresses missing information

## File Structure
```
AI-veterinary-assistance/
├── custom_ai_followup.py           # Main generator (replaces Groq)
├── ml_training/
│   └── vet_followup_qa/
│       ├── model.py                # Neural network architecture
│       ├── train.py                # Training script
│       ├── training_data.py        # Dataset generator
│       ├── vet_followup_model.pth  # Trained model (after training)
│       └── vet_followup_dataset.json  # Training data (auto-generated)
```

## Advantages Over External APIs

| Feature | Custom AI | External API (Groq/OpenAI) |
|---------|-----------|----------------------------|
| **Cost** | FREE | Paid (after limits) |
| **Privacy** | 100% local | Data sent to servers |
| **Speed** | Fast (~100ms) | Network dependent |
| **Offline** | Works offline | Requires internet |
| **Customization** | Fully customizable | Limited |
| **Control** | Complete control | Vendor dependent |

## Troubleshooting

### Error: "Model not found"
**Solution:** Train the model first
```bash
cd ml_training/vet_followup_qa
python train.py
```

### Error: "CUDA out of memory"
**Solution:** Train on CPU or reduce batch size
```python
# In train.py
train_model(batch_size=16)  # Reduce from 32
```

### Low Quality Questions
**Solution:** Train for more epochs or with more data
```python
# In train.py
train_model(num_epochs=100)  # Increase from 50
```

## Future Improvements
1. **Larger dataset** (10,000+ examples)
2. **More disease patterns** (20+ conditions)
3. **Fine-tuning** on real veterinary case data
4. **Multi-question generation** (ask follow-ups to follow-ups)
5. **Confidence scoring** for generated questions

## Testing
```bash
# Test the generator
python custom_ai_followup.py

# Test full integration
python main.py
```

## Support
For issues or questions:
1. Check training logs for errors
2. Verify model file exists: `ml_training/vet_followup_qa/vet_followup_model.pth`
3. Ensure all dependencies installed
4. Check CUDA availability if using GPU

---

**Built with PyTorch | 100% Local | No API Keys Needed**

# 🚀 Installation Instructions

## ✅ What's Working Now
- **Disease Priority Scoring** - Fixed and working perfectly!
- **MongoDB Integration** - Connected and retrieving data

## 📦 What You Need to Install

### Step 1: Install PyTorch
```bash
# For CPU (faster install, works on any machine)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# OR for GPU (if you have NVIDIA GPU with CUDA)
pip install torch torchvision
```

### Step 2: Install Additional Dependencies
```bash
pip install matplotlib tqdm
```

### Step 3: Train Your Custom AI Model
```bash
cd ml_training/vet_followup_qa
python train.py
```

**This will:**
- Generate 5000 training examples automatically
- Train a transformer neural network
- Save the trained model as `vet_followup_model.pth`
- Take approximately 30-60 minutes on CPU (10 minutes on GPU)

You'll see output like:
```
🔄 Generating 5000 training examples...
✅ Dataset saved
🔤 Building vocabulary... (3500+ words)
🚀 Starting training for 50 epochs...
Epoch 1/50: Train Loss: 4.23 | Val Loss: 3.98
Epoch 2/50: Train Loss: 3.51 | Val Loss: 3.25
...
✅ Saved best model (val_loss: 1.82)
✅ TRAINING COMPLETE!
```

### Step 4: Verify Everything Works
```bash
cd ../..  # Back to project root
python test_all_fixes.py
```

You should see:
```
✅ PASS  Disease Priority Scoring
✅ PASS  AI Model Status
✅ PASS  AI Question Generation
✅ PASS  Full Integration

Results: 4/4 tests passed
🎉 ALL TESTS PASSED! Your system is ready to use!
```

---

## 📝 Quick Command Summary

```bash
# 1. Install PyTorch (CPU version - recommended for most users)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 2. Install other dependencies
pip install matplotlib tqdm

# 3. Train the model
cd ml_training/vet_followup_qa
python train.py

# 4. Test everything
cd ../..
python test_all_fixes.py

# 5. Run your application
python main.py
# or
streamlit run app_streamlit.py
```

---

## 🎯 What You Get

### 1. Fixed Disease Priority System ✅
- Accurate confidence scores (0-100%)
- Proper symptom matching algorithm
- Severity weighting
- Example: "Parvovirus: 100% confidence" instead of just "3 symptoms matched"

### 2. Custom AI Follow-Up Questions ✅ (after training)
- Intelligent, context-aware questions
- Adapts to each patient case
- No external API costs
- 100% local and private
- Example questions:
  - "How many times has your dog vomited in the last 24 hours?"
  - "What color is the vomit?"
  - "Is your dog able to keep water down?"

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Install PyTorch | 2-5 minutes |
| Install other deps | 1 minute |
| Train AI model | 30-60 minutes (CPU) / 10 minutes (GPU) |
| Total | ~35-65 minutes |

**Note:** You can use the system with template questions while the model trains in the background!

---

## 💡 Tips

### If PyTorch Install is Slow
```bash
# Use the CPU-only version (smaller, faster download)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### If Training Seems Stuck
- It's normal! Training takes time
- You'll see progress bars and epoch updates
- Each epoch takes 1-2 minutes
- 50 epochs = 50-100 minutes total

### Using the System Before Training
The system works with template questions until you train the model:
```python
# This will use template questions (still works!)
assistant = VeterinaryAIAssistant(use_ai_questions=True)
```

---

## 🆘 Troubleshooting

### "No module named 'torch'"
**Solution:** Install PyTorch
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Training Crashes with "Out of Memory"
**Solution:** Reduce batch size in `train.py` line 215:
```python
train_model(batch_size=16)  # Change from 32 to 16
```

### Want to Skip Training for Now?
The system will fall back to template-based questions:
- Still generates good follow-up questions
- Just not AI-powered yet
- Disease priority scoring still works perfectly!

---

## 📊 Current Test Results

```
✅ Disease Priority Scoring - WORKING PERFECTLY
⏳ AI Model - Needs training (one-time setup)
⏳ AI Questions - Needs training (one-time setup)
⏳ Full Integration - Needs training (one-time setup)
```

After training:
```
✅ Disease Priority Scoring - WORKING
✅ AI Model - READY
✅ AI Questions - GENERATING
✅ Full Integration - COMPLETE
```

---

## 🎉 You're Almost There!

Just run these commands and you're done:
```bash
pip install torch torchvision matplotlib tqdm --index-url https://download.pytorch.org/whl/cpu
cd ml_training/vet_followup_qa && python train.py
```

Then grab a coffee ☕ and let it train for 30-60 minutes!

**Questions? Check:** [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md) or [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)

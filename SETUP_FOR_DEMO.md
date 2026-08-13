# 🚀 Quick Setup Guide - AI Veterinary Assistant

## Prerequisites
- Python 3.8 or higher
- Git installed

## Setup Steps (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/alen217/AI-veterinary-assistance.git
cd AI-veterinary-assistance
git checkout ai-followup-training
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get AI Model
**The AI model file is 173MB and not in GitHub. See `MODEL_DOWNLOAD.md` for options.**

**Quick Option - Copy from your PC:**
If sharing via USB/network, the model is already included in the folder!

**Or train yourself (30-60 min):**
```bash
cd ml_training/vet_followup_qa
python train.py
cd ../..
```



### 4. Run Application
```bash
streamlit run app_streamlit.py
```

The app will open at: http://localhost:8501

## 🎯 Demo Workflow

### Login
- Username: `admin` or `user`  


### Test the AI System
1. **Go to Diagnosis page**
2. **Enter patient symptoms:**
   ```
   My 3-year-old golden retriever has been vomiting for 2 days. 
   He also has diarrhea and seems very lethargic. 
   He's not eating his food and appears dehydrated.
   ```
3. **Click "Analyze Patient"**
4. **Watch the AI work:**
   - See initial disease matches
   - AI asks contextual follow-up questions (up to 8)
   - Answer each question
   - Watch confidence scores update in real-time
   - System stops at 85% confidence or 8 questions

### Example Follow-Up Flow:
**Q1:** "How many times has your dog vomited in the last 24 hours?"  
**A1:** "About 6 times"  
→ AI updates Parvovirus: 70% → 80%

**Q2:** "Has your dog shown any fever or high temperature?"  
**A2:** "Yes, he feels very hot"  
→ AI updates Parvovirus: 80% → 88% ✅ **DIAGNOSIS COMPLETE**

## 🎨 Key Features to Show

### AI-Powered Intelligence
- ✅ Neural network generates contextual questions
- ✅ Real-time disease confidence updates
- ✅ Automatic stopping at 85% confidence
- ✅ Smart narrowing (max 8 questions)

### Visual Feedback
- Progress metrics (Questions Asked, Confidence Level)
- AI reasoning display for each question
- Severity badges for diseases
- Beautiful completion screen with balloons

### History Tracking
- All consultations saved to database
- View past diagnoses in History page
- Per-user analysis tracking

## 📊 Expected Results

```
Initial Analysis: 3-5 diseases (50-75% confidence)
After Q1-2: 2-3 diseases (60-80% confidence)
After Q3-5: 1-2 diseases (75-90% confidence)
Final: Top disease >85% confidence = DIAGNOSIS COMPLETE
```

## ⚠️ Troubleshooting

### If AI model fails:
- System automatically falls back to template questions
- Still works, just less contextual

### If MongoDB connection fails:
- Check internet connection
- Verify .env file credentials

### If dependencies fail:
```bash
# Install PyTorch separately first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Then install rest
pip install -r requirements.txt
```

## 🎓 For Your Teacher

**Project Highlights:**
1. Custom trained neural network (not using external APIs)
2. Real-time AI-driven disease narrowing
3. Intelligent stopping conditions
4. Complete full-stack application
5. Production-ready authentication & database

**Technical Stack:**
- Frontend: Streamlit
- Backend: Python, PyTorch
- Database: MongoDB Atlas
- AI Model: Custom Transformer (Encoder-Decoder with Attention)
- Training: 5000+ synthetic veterinary cases

---
**Ready for demo! All features tested and working.** 🎉

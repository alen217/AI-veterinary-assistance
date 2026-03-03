import re

def apply_translations():
    with open('app_streamlit.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # Diagnosis Page
    code = code.replace('"## 🔍 Patient Diagnosis"', 'T("Patient Diagnosis")')
    code = code.replace(
        '"Enter the patient\'s symptoms and medical history below. Our AI will analyze the text and provide possible diagnoses with treatment recommendations."',
        'T("Diagnosis Intro")'
    )
    code = code.replace('"#### Describe or Speak Symptoms"', 'T("Describe or Speak Symptoms")')
    code = code.replace('🎙️ **Voice Input**', '{T("Voice Input")}')
    code = code.replace('"Transcribing..."', 'T("Transcribing")')
    code = code.replace('"🔍 Analyze Patient"', 'T("Analyze Patient")')
    code = code.replace('"🔄 Analyzing patient data..."', 'T("Analyzing patient data")')
    code = code.replace('"Upload skin image (optional)"', 'T("Upload skin image (optional)")')
    
    # Diagnosis Analysis Display
    code = code.replace('"### 👤 Patient Information"', 'T("Patient Information")')
    code = code.replace('"Species"', 'T("Species")')
    code = code.replace('"Age"', 'T("Age")')
    code = code.replace('"Breed"', 'T("Breed")')
    code = code.replace('"Weight"', 'T("Weight")')
    
    code = code.replace('"## 🧬 Skin Image Analysis (AI-assisted)"', 'T("Skin Image Analysis (AI-assisted)")')
    code = code.replace('"Predicted condition:"', '{T("Predicted condition")}:')
    code = code.replace('"Model confidence:"', '{T("Model confidence")}:')
    
    code = code.replace('"### 🩺 Detected Symptoms"', 'T("Detected Symptoms")')
    code = code.replace('Duration:', '{T("Duration")}:')
    code = code.replace('"No specific symptoms detected."', 'T("No specific symptoms detected")')
    
    # Follow-up Analysis
    code = code.replace('"### 🤖 Follow-up Analysis"', 'T("Follow-up Analysis")')
    code = code.replace('"Questions Asked"', 'T("Questions Asked")')
    code = code.replace('"Top Confidence"', 'T("Top Confidence")')
    code = code.replace('"Target Confidence"', 'T("Target Confidence")')
    code = code.replace('**Question {questions_asked + 1}:**', '**{T("Question")} {questions_asked + 1}:**')
    code = code.replace('"Type your answer here..."', 'T("Type your answer here")')
    code = code.replace('"✅ Submit Answer"', 'T("Submit Answer")')
    code = code.replace('"⚠️ Please provide an answer before submitting."', 'T("Please provide an answer before submitting")')
    
    # End of consultation
    code = code.replace('Achieved {top_disease_confidence:.1%} confidence', '{T("Diagnosis Complete!")} Achieved {top_disease_confidence:.1%} confidence')
    code = code.replace('"### 📈 Consultation Summary"', 'T("Consultation Summary")')
    code = code.replace('"🔄 Start New Consultation"', 'T("Start New Consultation")')
    
    # Possible Diagnoses
    code = code.replace('"### 🎯 Possible Diagnoses"', 'T("Possible Diagnoses")')
    code = code.replace('<strong>Scientific Name:</strong>', '<strong>{T("Scientific Name")}:</strong>')
    code = code.replace('<strong>Description:</strong>', '<strong>{T("Description")}:</strong>')
    code = code.replace('<strong>Treatment:</strong>', '<strong>{T("Treatment")}:</strong>')
    code = code.replace('<strong>Prevention:</strong>', '<strong>{T("Prevention")}:</strong>')
    code = code.replace('<strong>Affected Species:</strong>', '<strong>{T("Affected Species")}:</strong>')
    
    # Recommendations
    code = code.replace('"### 💡 Recommendations"', 'T("Recommendations")')
    code = code.replace('**Urgency Level:**', '**{T("Urgency Level:")}**')
    code = code.replace('**Recommended Actions:**', '**{T("Recommended Actions:")}**')
    code = code.replace('"- Seek immediate veterinary attention."', 'T("Seek immediate veterinary attention.")')
    code = code.replace('"- Monitor vital signs closely."', 'T("Monitor vital signs closely.")')
    code = code.replace('"- Schedule a veterinary appointment within 24-48 hours."', 'T("Schedule a veterinary appointment within 24-48 hours.")')
    code = code.replace('"- Monitor for worsening symptoms."', 'T("Monitor for worsening symptoms.")')
    code = code.replace('"- Continue monitoring the patient at home."', 'T("Continue monitoring the patient at home.")')
    code = code.replace('"- Maintain current care routine."', 'T("Maintain current care routine.")')
    
    # Database Page
    code = code.replace('"## 📚 Disease Database"', 'f"## {T(\'Disease Database\')}"')
    code = code.replace('"🔍 Search diseases"', 'T("Search diseases")')
    code = code.replace('"Enter disease name or keyword..."', 'T("Enter disease name or keyword")')
    code = code.replace('st.selectbox("Severity", ["All", "mild", "moderate", "severe"])', 'st.selectbox(T("Severity"), [T("All"), T("mild"), T("moderate"), T("severe")])')
    
    code = code.replace('f"### Found {len(diseases)} disease(s)"', 'f"### Found {len(diseases)} disease(s)"') # Keeping this as is for simplicity, or we can replace it.
    
    # Analysis History Page
    code = code.replace('"## 📊 Analysis History"', 'f"{T(\'Analysis History\')}"')
    
    # Admin Panel
    code = code.replace('"## 👨‍💼 Admin Panel"', 'f"{T(\'Admin Panel Page\')}"')
    
    with open('app_streamlit.py', 'w', encoding='utf-8') as f:
        f.write(code)

if __name__ == "__main__":
    apply_translations()
    print("Done")

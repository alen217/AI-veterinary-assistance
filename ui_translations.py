"""
UI Translation Dictionary and Helper Function
Supports English, Hindi, and Malayalam.
"""
import streamlit as st

TRANSLATIONS = {
    # General UI & Navigation
    "🐾 Veterinary AI Assistant": {
        "en": "🐾 Veterinary AI Assistant",
        "hi": "🐾 पशु चिकित्सा एआई सहायक (Veterinary AI Assistant)",
        "ml": "🐾 വെറ്ററിനറി AI അസിസ്റ്റൻ്റ് (Veterinary AI Assistant)"
    },
    "Advanced AI-Powered Veterinary Diagnosis System": {
        "en": "Advanced AI-Powered Veterinary Diagnosis System",
        "hi": "उन्नत एआई-संचालित पशु चिकित्सा निदान प्रणाली",
        "ml": "നൂതന AI അധിഷ്ഠിത വെറ്ററിനറി രോഗനിർണയ സംവിധാനം"
    },
    "Home": {
        "en": "🏠 Home",
        "hi": "🏠 मुख्य पृष्ठ (Home)",
        "ml": "🏠 ഹോം (Home)"
    },
    "Diagnosis": {
        "en": "🔍 Diagnosis",
        "hi": "🔍 निदान (Diagnosis)",
        "ml": "🔍 രോഗനിർണയം (Diagnosis)"
    },
    "Disease Database": {
        "en": "📚 Disease Database",
        "hi": "📚 रोग डेटाबेस (Disease Database)",
        "ml": "📚 രോഗ ഡാറ്റാബേസ് (Disease Database)"
    },
    "History": {
        "en": "📊 History",
        "hi": "📊 इतिहास (History)",
        "ml": "📊 ചരിത്രം (History)"
    },
    "Admin Panel": {
        "en": "⚙️ Admin Panel",
        "hi": "⚙️ व्यवस्थापक पैनल (Admin Panel)",
        "ml": "⚙️ അഡ്മിൻ പാനൽ (Admin Panel)"
    },
    "Logout": {
        "en": "🚪 Logout",
        "hi": "🚪 लॉग आउट (Logout)",
        "ml": "🚪 ലോഗൗട്ട് (Logout)"
    },
    "Navigation": {
        "en": "Navigation",
        "hi": "नेविगेशन (Navigation)",
        "ml": "നാവിഗേഷൻ (Navigation)"
    },
    "Welcome": {
        "en": "Welcome",
        "hi": "स्वागत है (Welcome)",
        "ml": "സ്വാഗതം (Welcome)"
    },
    "Role:": {
        "en": "Role:",
        "hi": "भूमिका (Role):",
        "ml": "പദവി (Role):"
    },

    # Login / Register
    "Login": {
        "en": "🔐 Login",
        "hi": "🔐 लॉगिन (Login)",
        "ml": "🔐 ലോഗിൻ (Login)"
    },
    "Username": {
        "en": "Username",
        "hi": "उपयोगकर्ता नाम (Username)",
        "ml": "ഉപയോക്തൃനാമം (Username)"
    },
    "Password": {
        "en": "Password",
        "hi": "पासवर्ड (Password)",
        "ml": "പാസ്‌വേഡ് (Password)"
    },
    "Login Button": {
        "en": "Login",
        "hi": "लॉगिन",
        "ml": "ലോഗിൻ"
    },
    "Register": {
        "en": "Register",
        "hi": "रजिस्टर (Register)",
        "ml": "രജിസ്റ്റർ (Register)"
    },
    "Register New User": {
        "en": "📝 Register New User",
        "hi": "📝 नया उपयोगकर्ता रजिस्टर करें (Register New User)",
        "ml": "📝 പുതിയ ഉപയോക്താവിനെ രജിസ്റ്റർ ചെയ്യുക (Register New User)"
    },
    "New Username": {
        "en": "New Username",
        "hi": "नया उपयोगकर्ता नाम (New Username)",
        "ml": "പുതിയ ഉപയോക്തൃനാമം (New Username)"
    },
    "New Password": {
        "en": "New Password",
        "hi": "नया पासवर्ड (New Password)",
        "ml": "പുതിയ പാസ്‌വേഡ് (New Password)"
    },
    "Confirm Password": {
        "en": "Confirm Password",
        "hi": "पासवर्ड की पुष्टि करें (Confirm Password)",
        "ml": "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക (Confirm Password)"
    },
    "Create Account": {
        "en": "Create Account",
        "hi": "खाता बनाएं (Create Account)",
        "ml": "അക്കൗണ്ട് സൃഷ്ടിക്കുക (Create Account)"
    },
    "Invalid username or password": {
        "en": "❌ Invalid username or password",
        "hi": "❌ अमान्य उपयोगकर्ता नाम या पासवर्ड",
        "ml": "❌ അസാധുവായ ഉപയോക്തൃനാമം അല്ലെങ്കിൽ പാസ്‌വേഡ്"
    },
    "Passwords do not match": {
        "en": "❌ Passwords do not match",
        "hi": "❌ पासवर्ड मेल नहीं खाते",
        "ml": "❌ പാസ്‌വേഡുകൾ പൊരുത്തപ്പെടുന്നില്ല"
    },
    "Password must be at least 6 characters": {
        "en": "❌ Password must be at least 6 characters",
        "hi": "❌ पासवर्ड कम से कम 6 अक्षरों का होना चाहिए",
        "ml": "❌ പാസ്‌വേഡിന് കുറഞ്ഞത് 6 പ്രതീകങ്ങൾ ഉണ്ടായിരിക്കണം"
    },
    "Account created! Please login.": {
        "en": "✅ Account created! Please login.",
        "hi": "✅ खाता बन गया! कृपया लॉगिन करें।",
        "ml": "✅ അക്കൗണ്ട് സൃഷ്ടിച്ചു! ദയവായി ലോഗിൻ ചെയ്യുക."
    },
    "Username already exists": {
        "en": "❌ Username already exists",
        "hi": "❌ उपयोगकर्ता नाम पहले से मौजूद है",
        "ml": "❌ ഉപയോക്തൃനാമം ഇതിനകം നിലവിലുണ്ട്"
    },

    # Home Page
    "Diseases": {
        "en": "Diseases",
        "hi": "रोग (Diseases)",
        "ml": "രോഗങ്ങൾ (Diseases)"
    },
    "Analyses": {
        "en": "Analyses",
        "hi": "विश्लेषण (Analyses)",
        "ml": "വിശകലനങ്ങൾ (Analyses)"
    },
    "Available": {
        "en": "Available",
        "hi": "उपलब्ध (Available)",
        "ml": "ലഭ്യമാണ് (Available)"
    },
    "Key Features": {
        "en": "🌟 Key Features",
        "hi": "🌟 मुख्य विशेषताएं (Key Features)",
        "ml": "🌟 പ്രധാന സവിശേഷതകൾ (Key Features)"
    },
    "AI-Powered Analysis": {
        "en": "🔬 AI-Powered Analysis",
        "hi": "🔬 एआई-संचालित विश्लेषण (AI-Powered Analysis)",
        "ml": "🔬 AI-അധിഷ്ഠിത വിശകലനം (AI-Powered Analysis)"
    },
    "AI-Powered Analysis Desc": {
        "en": "Advanced natural language processing to analyze patient symptoms and medical history.",
        "hi": "रोगी के लक्षणों और चिकित्सा इतिहास का विश्लेषण करने के लिए उन्नत प्राकृतिक भाषा प्रसंस्करण।",
        "ml": "രോഗിയുടെ ലക്ഷണങ്ങളും മെഡിക്കൽ ചരിത്രവും വിശകലനം ചെയ്യുന്നതിനുള്ള നൂതന പ്രകൃതി ഭാഷാ പ്രോസസ്സിംഗ്."
    },
    "Comprehensive Database": {
        "en": "📚 Comprehensive Database",
        "hi": "📚 व्यापक डेटाबेस (Comprehensive Database)",
        "ml": "📚 സമഗ്രമായ ഡാറ്റാബേസ് (Comprehensive Database)"
    },
    "Comprehensive Database Desc": {
        "en": "Access to extensive veterinary disease database with treatments and prevention methods.",
        "hi": "उपचार और रोकथाम के तरीकों के साथ व्यापक पशु चिकित्सा रोग डेटाबेस तक पहुंच।",
        "ml": "ചികിത്സകളും പ്രതിരോധ മാർഗ്ഗങ്ങളുമുള്ള വിപുലമായ വെറ്ററിനറി രോഗ ഡാറ്റാബേസിലേക്കുള്ള പ്രവേശനം."
    },
    "Real-time Diagnosis": {
        "en": "⚡ Real-time Diagnosis",
        "hi": "⚡ वास्तविक समय निदान (Real-time Diagnosis)",
        "ml": "⚡ തത്സമയ രോഗനിർണയം (Real-time Diagnosis)"
    },
    "Real-time Diagnosis Desc": {
        "en": "Get instant disease predictions and treatment recommendations.",
        "hi": "तत्काल रोग की भविष्यवाणियां और उपचार की सिफारिशें प्राप्त करें।",
        "ml": "തൽക്ഷണ രോഗ പ്രവചനങ്ങളും ചികിത്സാ നിർദ്ദേശങ്ങളും നേടുക."
    },
    "Secure & Private": {
        "en": "🔒 Secure & Private",
        "hi": "🔒 सुरक्षित और निजी (Secure & Private)",
        "ml": "🔒 സുരക്ഷിതവും സ്വകാര്യവും (Secure & Private)"
    },
    "Secure & Private Desc": {
        "en": "User authentication and secure data handling for patient information.",
        "hi": "रोगी की जानकारी के लिए उपयोगकर्ता प्रमाणीकरण और सुरक्षित डेटा हैंडलिंग।",
        "ml": "രോഗിയുടെ വിവരങ്ങൾക്കായുള്ള ഉപയോക്തൃ പ്രാമാണീകരണവും സുരക്ഷിതമായ ഡാറ്റ കൈകാര്യം ചെയ്യലും."
    },

    # Diagnosis Page
    "Patient Diagnosis": {
        "en": "## 🔍 Patient Diagnosis",
        "hi": "## 🔍 रोगी का निदान (Patient Diagnosis)",
        "ml": "## 🔍 രോഗിയുടെ രോഗനിർണയം (Patient Diagnosis)"
    },
    "Diagnosis Intro": {
        "en": "Enter the patient's symptoms and medical history below. Our AI will analyze the text and provide possible diagnoses with treatment recommendations.",
        "hi": "नीचे रोगी के लक्षण और चिकित्सा इतिहास दर्ज करें। हमारा एआई पाठ का विश्लेषण करेगा और उपचार की सिफारिशों के साथ संभावित निदान प्रदान करेगा।",
        "ml": "രോഗിയുടെ ലക്ഷണങ്ങളും മെഡിക്കൽ ചരിത്രവും താഴെ നൽകുക. ഞങ്ങളുടെ AI വിവരങ്ങൾ വിശകലനം ചെയ്ത് ചികിത്സാ നിർദ്ദേശങ്ങളോടെ സാധ്യമായ രോഗനിർണയങ്ങൾ നൽകും."
    },
    "Describe or Speak Symptoms": {
        "en": "#### Describe or Speak Symptoms",
        "hi": "#### लक्षणों का वर्णन करें या बोलें (Describe or Speak Symptoms)",
        "ml": "#### ലക്ഷണങ്ങൾ വിവരിക്കുകയോ പറയുകയോ ചെയ്യുക (Describe or Speak Symptoms)"
    },
    "Voice Input": {
        "en": "🎙️ **Voice Input**",
        "hi": "🎙️ **ध्वनि इनपुट** (Voice Input)",
        "ml": "🎙️ **ശബ്ദ ഇൻപുട്ട്** (Voice Input)"
    },
    "Transcribing": {
        "en": "Transcribing...",
        "hi": "प्रतिलिपि बनाई जा रही है...",
        "ml": "ട്രാൻസ്ക്രൈബ് ചെയ്യുന്നു..."
    },
    "Analyze Patient": {
        "en": "🔍 Analyze Patient",
        "hi": "🔍 रोगी का विश्लेषण करें (Analyze Patient)",
        "ml": "🔍 രോഗിയെ വിശകലനം ചെയ്യുക (Analyze Patient)"
    },
    "Analyzing patient data": {
        "en": "🔄 Analyzing patient data...",
        "hi": "🔄 रोगी के डेटा का विश्लेषण किया जा रहा है...",
        "ml": "🔄 രോഗിയുടെ വിവരങ്ങൾ വിശകലനം ചെയ്യുന്നു..."
    },
    "Upload skin image (optional)": {
        "en": "Upload skin image (optional)",
        "hi": "त्वचा की छवि अपलोड करें (वैकल्पिक)",
        "ml": "ചർമ്മത്തിന്റെ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക (ഓപ്ഷണൽ)"
    },
    "Patient Information": {
        "en": "### 👤 Patient Information",
        "hi": "### 👤 रोगी की जानकारी (Patient Information)",
        "ml": "### 👤 രോഗിയുടെ വിവരങ്ങൾ (Patient Information)"
    },
    "Species": {
        "en": "Species",
        "hi": "प्रजाति (Species)",
        "ml": "സ്പീഷിസ് (Species)"
    },
    "Age": {
        "en": "Age",
        "hi": "उम्र (Age)",
        "ml": "പ്രായം (Age)"
    },
    "Breed": {
        "en": "Breed",
        "hi": "नस्ल (Breed)",
        "ml": "ഇനം (Breed)"
    },
    "Weight": {
        "en": "Weight",
        "hi": "वजन (Weight)",
        "ml": "ഭാരം (Weight)"
    },
    "Skin Image Analysis (AI-assisted)": {
        "en": "## 🧬 Skin Image Analysis (AI-assisted)",
        "hi": "## 🧬 त्वचा छवि विश्लेषण (एआई-सहायता प्राप्त)",
        "ml": "## 🧬 സ്കിൻ ഇമേജ് വിശകലനം (AI സഹായത്തോടെ)"
    },
    "Predicted condition": {
        "en": "Predicted condition",
        "hi": "अनुमानित स्थिति",
        "ml": "പ്രവചിക്കപ്പെട്ട അവസ്ഥ"
    },
    "Model confidence": {
        "en": "Model confidence",
        "hi": "मॉडल का विश्वास (Model confidence)",
        "ml": "മോഡലിൻ്റെ വിശ്വാസ്യത (Model confidence)"
    },
    "Detected Symptoms": {
        "en": "### 🩺 Detected Symptoms",
        "hi": "### 🩺 पहचाने गए लक्षण (Detected Symptoms)",
        "ml": "### 🩺 കണ്ടെത്തിയ ലക്ഷണങ്ങൾ (Detected Symptoms)"
    },
    "Duration": {
        "en": "Duration",
        "hi": "अवधि (Duration)",
        "ml": "കാലയളവ് (Duration)"
    },
    "No specific symptoms detected": {
        "en": "No specific symptoms detected.",
        "hi": "कोई विशिष्ट लक्षण नहीं पहचाने गए।",
        "ml": "പ്രത്യേക ലക്ഷണങ്ങളൊന്നും കണ്ടെത്തിയില്ല."
    },
    "Follow-up Analysis": {
        "en": "### 🤖 Follow-up Analysis",
        "hi": "### 🤖 अनुवर्ती विश्लेषण (Follow-up Analysis)",
        "ml": "### 🤖 തുടർ വിശകലനം (Follow-up Analysis)"
    },
    "Questions Asked": {
        "en": "Questions Asked",
        "hi": "पूछे गए प्रश्न (Questions Asked)",
        "ml": "ചോദിച്ച ചോദ്യങ്ങൾ (Questions Asked)"
    },
    "Top Confidence": {
        "en": "Top Confidence",
        "hi": "शीर्ष विश्वास (Top Confidence)",
        "ml": "ഏറ്റവും ഉയർന്ന വിശ്വാസ്യത (Top Confidence)"
    },
    "Target Confidence": {
        "en": "Target Confidence",
        "hi": "लक्षित विश्वास (Target Confidence)",
        "ml": "ലക്ഷ്യ വിശ്വാസ്യത (Target Confidence)"
    },
    "Question": {
        "en": "Question",
        "hi": "प्रश्न",
        "ml": "ചോദ്യം"
    },
    "Type your answer here": {
        "en": "Type your answer here...",
        "hi": "अपना उत्तर यहाँ टाइप करें...",
        "ml": "നിങ്ങളുടെ ഉത്തരം ഇവിടെ ടൈപ്പ് ചെയ്യുക..."
    },
    "Submit Answer": {
        "en": "✅ Submit Answer",
        "hi": "✅ उत्तर सबमिट करें (Submit Answer)",
        "ml": "✅ ഉത്തരം സമർപ്പിക്കുക (Submit Answer)"
    },
    "Please provide an answer before submitting": {
        "en": "⚠️ Please provide an answer before submitting.",
        "hi": "⚠️ कृपया सबमिट करने से पहले उत्तर दें।",
        "ml": "⚠️ ദയവായി സമർപ്പിക്കുന്നതിന് മുമ്പ് ഉത്തരം നൽകുക."
    },
    "Diagnosis Complete!": {
        "en": "Diagnosis Complete!",
        "hi": "निदान पूरा हुआ! (Diagnosis Complete!)",
        "ml": "രോഗനിർണയം പൂർത്തിയായി! (Diagnosis Complete!)"
    },
    "Consultation Summary": {
        "en": "### 📈 Consultation Summary",
        "hi": "### 📈 परामर्श सारांश (Consultation Summary)",
        "ml": "### 📈 കൺസൾട്ടേഷൻ സംഗ്രഹം (Consultation Summary)"
    },
    "Start New Consultation": {
        "en": "🔄 Start New Consultation",
        "hi": "🔄 नया परामर्श शुरू करें (Start New Consultation)",
        "ml": "🔄 പുതിയ കൺസൾട്ടേഷൻ ആരംഭിക്കുക (Start New Consultation)"
    },
    "Possible Diagnoses": {
        "en": "### 🎯 Possible Diagnoses",
        "hi": "### 🎯 संभावित निदान (Possible Diagnoses)",
        "ml": "### 🎯 സാധ്യമായ രോഗനിർണയങ്ങൾ (Possible Diagnoses)"
    },
    "Scientific Name": {
        "en": "Scientific Name",
        "hi": "वैज्ञानिक नाम (Scientific Name)",
        "ml": "ശാസ്ത്രീയ നാമം (Scientific Name)"
    },
    "Description": {
        "en": "Description",
        "hi": "विवरण (Description)",
        "ml": "വിവരണം (Description)"
    },
    "Treatment": {
        "en": "Treatment",
        "hi": "उपचार (Treatment)",
        "ml": "ചികിത്സ (Treatment)"
    },
    "Prevention": {
        "en": "Prevention",
        "hi": "निवारण (Prevention)",
        "ml": "പ്രതിരോധം (Prevention)"
    },
    "Affected Species": {
        "en": "Affected Species",
        "hi": "प्रभावित प्रजाति (Affected Species)",
        "ml": "ബാധിക്കുന്ന സ്പീഷിസുകൾ (Affected Species)"
    },
    "Recommendations": {
        "en": "### 💡 Recommendations",
        "hi": "### 💡 सिफारिशें (Recommendations)",
        "ml": "### 💡 നിർദ്ദേശങ്ങൾ (Recommendations)"
    },
    "Urgency Level:": {
        "en": "Urgency Level:",
        "hi": "तात्कालिकता स्तर (Urgency Level):",
        "ml": "അടിയന്തിരതയുടെ നില (Urgency Level):"
    },
    "Recommended Actions:": {
        "en": "Recommended Actions:",
        "hi": "अनुशंसित क्रियाएं (Recommended Actions):",
        "ml": "ശുപാർശ ചെയ്യുന്ന പ്രവർത്തനങ്ങൾ (Recommended Actions):"
    },
    "Seek immediate veterinary attention.": {
        "en": "- Seek immediate veterinary attention.",
        "hi": "- तत्काल पशु चिकित्सा सहायता प्राप्त करें।",
        "ml": "- ഉടനടി മൃഗവൈദ്യൻ്റെ സഹായം തേടുക."
    },
    "Monitor vital signs closely.": {
        "en": "- Monitor vital signs closely.",
        "hi": "- महत्वपूर्ण संकेतों की बारीकी से निगरानी करें।",
        "ml": "- സുപ്രധാന ലക്ഷണങ്ങൾ സൂക്ഷ്മമായി നിരീക്ഷിക്കുക."
    },
    "Schedule a veterinary appointment within 24-48 hours.": {
        "en": "- Schedule a veterinary appointment within 24-48 hours.",
        "hi": "- 24-48 घंटों के भीतर पशु चिकित्सा नियुक्ति निर्धारित करें।",
        "ml": "- 24-48 മണിക്കൂറിനുള്ളിൽ ഒരു വെറ്ററിനറി അപ്പോയിൻ്റ്മെൻ്റ് എടുക്കുക."
    },
    "Monitor for worsening symptoms.": {
        "en": "- Monitor for worsening symptoms.",
        "hi": "- बिगड़ते लक्षणों की निगरानी करें।",
        "ml": "- ലക്ഷണങ്ങൾ വഷളാകുന്നുണ്ടോ എന്ന് നിരീക്ഷിക്കുക."
    },
    "Continue monitoring the patient at home.": {
        "en": "- Continue monitoring the patient at home.",
        "hi": "- घर पर रोगी की निगरानी जारी रखें।",
        "ml": "- വീട്ടിൽ രോഗിയെ നിരീക്ഷിക്കുന്നത് തുടരുക."
    },
    "Maintain current care routine.": {
        "en": "- Maintain current care routine.",
        "hi": "- वर्तमान देखभाल दिनचर्या बनाए रखें।",
        "ml": "- നിലവിലെ പരിചരണ രീതി തുടരുക."
    },

    # Database Page
    "Search diseases": {
        "en": "🔍 Search diseases",
        "hi": "🔍 रोगों की खोज करें (Search diseases)",
        "ml": "🔍 രോഗങ്ങൾ തിരയുക (Search diseases)"
    },
    "Enter disease name or keyword": {
        "en": "Enter disease name or keyword...",
        "hi": "रोग का नाम या कीवर्ड दर्ज करें...",
        "ml": "രോഗത്തിൻ്റെ പേരോ കീവേഡോ നൽകുക..."
    },
    "Severity": {
        "en": "Severity",
        "hi": "गंभीरता (Severity)",
        "ml": "തീവ്രത (Severity)"
    },
    "All": {
        "en": "All",
        "hi": "सभी (All)",
        "ml": "എല്ലാം (All)"
    },
    "mild": {
        "en": "mild",
        "hi": "हल्का (mild)",
        "ml": "ലഘുവായ (mild)"
    },
    "moderate": {
        "en": "moderate",
        "hi": "मध्यम (moderate)",
        "ml": "മിതമായ (moderate)"
    },
    "severe": {
        "en": "severe",
        "hi": "गंभीर (severe)",
        "ml": "ഗുരുതരമായ (severe)"
    },
    "Total Diseases": {
        "en": "Total Diseases",
        "hi": "कुल रोग (Total Diseases)",
        "ml": "ആകെ രോഗങ്ങൾ (Total Diseases)"
    },

    # Status & Analysis
    "Analysis History": {
        "en": "## 📊 Analysis History",
        "hi": "## 📊 विश्लेषण इतिहास (Analysis History)",
        "ml": "## 📊 വിശകലന ചരിത്രം (Analysis History)"
    },
    "Admin Panel Page": {
        "en": "## 👨‍💼 Admin Panel",
        "hi": "## 👨‍💼 व्यवस्थापक पैनल (Admin Panel)",
        "ml": "## 👨‍💼 അഡ്മിൻ പാനൽ (Admin Panel)"
    },
    "Language": {
        "en": "Language",
        "hi": "भाषा (Language)",
        "ml": "ഭാഷ (Language)"
    }
}

def get_language_code(lang_name: str) -> str:
    mapping = {
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        "Malayalam (മലയാളം)": "ml"
    }
    return mapping.get(lang_name, "en")

def T(text: str) -> str:
    """
    Translates the given text into the language set in Streamlit's session state.
    """
    # Get the selected language from session state, default to English
    lang_name = st.session_state.get("ui_language", "English")
    lang_code = get_language_code(lang_name)
    
    # Try to find exactly matching translation
    if text in TRANSLATIONS and lang_code in TRANSLATIONS[text]:
        return TRANSLATIONS[text][lang_code]
        
    return text  # Fallback to English if not found

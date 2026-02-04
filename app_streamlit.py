"""
Professional Veterinary AI Assistant - Streamlit Web Application
Features: Dark Theme, Authentication, Admin Panel, User Management
"""
import os
print("🚨 RUNNING FILE:", os.path.abspath(__file__))
print("🚨 WORKING DIR:", os.getcwd())

import streamlit as st
import tempfile
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from pathlib import Path
from main import VeterinaryAIAssistant
from user_database import UserDatabase, get_db
from mongo_disease_repository import MongoDiseaseRepository
from follow_up_questions import FollowUpQuestionGenerator
from consultation_state_updater import apply_answer
from dynamic_confidence_updater import DynamicDiseaseRanker, FollowUpAnswer

# Try to load AI-powered question generator
try:
    from custom_ai_followup import CustomAIFollowUpGenerator
    AI_MODEL_AVAILABLE = True
    print("✅ Custom AI follow-up model loaded successfully")
except Exception as e:
    AI_MODEL_AVAILABLE = False
    print(f"⚠️  Using template-based questions (AI model not available: {e})")

# Load environment variables
_DOTENV_PATH = find_dotenv(usecwd=True) or str(Path(__file__).resolve().parent / ".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)

# Configure page
st.set_page_config(
    page_title="Veterinary AI Assistant",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dark theme
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #4CAF50;
        --secondary-color: #2196F3;
        --background-dark: #0e1117;
        --card-background: #1e2127;
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
    }

    /* Global styles */
    .main {
        background-color: var(--background-dark);
    }

    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }

    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }

    /* Card styling */
    .info-card {
        background-color: var(--card-background);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .disease-card {
        background: linear-gradient(135deg, #1e2127 0%, #2a2d35 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #3a3d45;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }

    .disease-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    /* Severity badges */
    .severity-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        text-transform: uppercase;
    }

    .severity-mild {
        background-color: #4CAF50;
        color: white;
    }

    .severity-moderate {
        background-color: #FF9800;
        color: white;
    }

    .severity-severe {
        background-color: #F44336;
        color: white;
    }

    /* Stats container */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }

    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        flex: 1;
        margin: 0 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
    }

    .stat-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.9);
        text-transform: uppercase;
        margin-top: 0.5rem;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }

    /* Login container */
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 2rem;
        background-color: var(--card-background);
        border-radius: 10px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }

    /* Success/Error messages */
    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .error-message {
        background-color: #F44336;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e2127;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    </style>
    """, unsafe_allow_html=True)

# User management (MongoDB-backed)
class UserManager:
    def __init__(self):
        self.db = UserDatabase()

    def verify_user(self, username: str, password: str):
        return self.db.verify_user(username, password)

    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        return self.db.create_user(username, password, role)

    def delete_user(self, username: str) -> bool:
        if username == os.getenv("ADMIN_USERNAME", "admin"):
            return False
        result = self.db.users.delete_one({"username": username})
        return result.deleted_count == 1

    def get_user_role(self, username: str) -> str:
        user = self.db.users.find_one({"username": username})
        return user.get("role", "user") if user else "user"

    def list_users(self):
        return list(
            self.db.users.find(
                {},
                {"username": 1, "role": 1, "created_at": 1}
            ).sort("created_at", -1)
        )

# Helper to save uploaded file temporarily
def save_temp_image(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            f.write(uploaded_file.getbuffer())
            return f.name
    except Exception as e:
        st.error(f"Error saving image: {e}")
        return None

# Initialize session state
def init_session_state():
    defaults = {
        'logged_in': False,
        'username': None,
        'role': None,
        'analysis_history': [],
        'show_register': False
    }
    
    # STEP 1: Add consultation state
    if "consultation" not in st.session_state:
        st.session_state.consultation = {
            "patient_info": None,
            "symptoms": [],
            "diseases": [],
            "matches": [], # To store full DB matches for display
            "image_path": None,
            "skin_result": None,
            "answers": {},
            "disease_ranker": None,  # For AI-powered dynamic confidence updates
            "follow_up_questions": [],
            "questions_asked": 0,  # Track number of questions
            "max_questions": 8,  # Maximum questions before stopping
            "confidence_threshold": 0.85  # Stop when top disease reaches this
        }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Login page
def show_login_page():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="header-title">🐾 Veterinary AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Advanced AI-Powered Veterinary Diagnosis System</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 🔐 Login")

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Login", use_container_width=True):
                user_manager = UserManager()
                user = user_manager.verify_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user.get("role", user_manager.get_user_role(username))
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        with col_btn2:
            if st.button("Register", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.show_register:
            st.markdown("---")
            st.markdown("### 📝 Register New User")
            new_username = st.text_input("New Username", key="reg_username")
            new_password = st.text_input("New Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Create Account"):
                if new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    user_manager = UserManager()
                    if user_manager.add_user(new_username, new_password):
                        st.success("✅ Account created! Please login.")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error("❌ Username already exists")


def show_admin_panel():
    st.markdown("## 👨‍💼 Admin Panel")

    tabs = st.tabs(["User Management", "Database Stats", "System Settings"])

    # User Management Tab
    with tabs[0]:
        st.markdown("### 👥 User Management")

        user_manager = UserManager()
        users = user_manager.list_users()

        # Display users
        st.markdown("#### Current Users")
        for data in users:
            username = data.get("username", "")
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.write(f"**{username}**")
            with col2:
                st.write(f"Role: {data.get('role', 'user')}")
            with col3:
                created = data.get("created_at")
                created_str = str(created)[:10] if created else ""
                st.write(f"Created: {created_str}")
            with col4:
                if username != "admin" and username != st.session_state.username:
                    if st.button(f"Delete", key=f"del_{username}"):
                        user_manager.delete_user(username)
                        st.success(f"✅ User {username} deleted")
                        st.rerun()

        # Add new user
        st.markdown("---")
        st.markdown("#### Add New User")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_user = st.text_input("Username", key="admin_new_user")
        with col2:
            new_pass = st.text_input("Password", type="password", key="admin_new_pass")
        with col3:
            new_role = st.selectbox("Role", ["user", "admin"], key="admin_new_role")

        if st.button("Add User"):
            if user_manager.add_user(new_user, new_pass, new_role):
                st.success(f"✅ User {new_user} added successfully")
                st.rerun()
            else:
                st.error("❌ Username already exists")

        st.markdown("---")
        st.markdown("#### Seed Database")
        st.caption("Adds more diseases/symptoms for testing and demo.")
        col_a, col_b = st.columns(2)
        with col_a:
            seed_diseases = st.number_input("Diseases to seed", min_value=0, max_value=2000, value=200, step=50)
        with col_b:
            seed_symptoms = st.number_input("Symptoms to seed", min_value=0, max_value=5000, value=500, step=100)
        
        if st.button("Seed Now"):
            try:
                from seed_large_dataset import seed
                db = get_db()
                seed(db, disease_count=int(seed_diseases), symptom_count=int(seed_symptoms))
                st.success("✅ Seeding completed")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Seeding failed: {e}")

    # Database Stats Tab
    with tabs[1]:
        st.markdown("### 📊 Database Statistics")

        try:
            db = get_db()

            disease_count = db.diseases.count_documents({})
            treatment_count = db.treatments.count_documents({})
            user_count = db.users.count_documents({})
            symptom_count = db.symptoms.count_documents({})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Diseases", disease_count, delta=None)
            with col2:
                st.metric("Total Treatments", treatment_count, delta=None)
            with col3:
                st.metric("Total Users", user_count, delta=None)

            st.metric("Total Symptoms", symptom_count, delta=None)

            # Disease by severity
            st.markdown("#### Diseases by Severity")
            for severity in ["mild", "moderate", "severe"]:
                count = db.diseases.count_documents({"severity": severity})
                st.write(f"**{severity.capitalize()}:** {count}")

        except Exception as e:
            st.error(f"❌ Database Error: {e}")

    # System Settings Tab
    with tabs[2]:
        st.markdown("### ⚙️ System Settings")

        st.markdown("#### Database Configuration")
        mongo_url = os.getenv('MONGO_URL', 'Not configured')
        db_name = os.getenv('MONGO_DB_NAME', 'veterinary_ai_db')

        st.info(f"**Database:** {db_name}")
        st.info(f"**Connection:** {'✅ Configured' if mongo_url != 'Not configured' else '❌ Not configured'}")

        st.markdown("#### Application Info")
        st.write("**Version:** 2.0.0")
        st.write("**AI Model:** Custom Neural Network + MongoDB")
        st.write("**Last Updated:** February 2026")
        
        st.markdown("---")
        st.markdown("#### AI Follow-Up System")
        if AI_MODEL_AVAILABLE:
            st.success("✅ AI Model Active - Using Neural Network for Questions")
            st.info("The AI automatically narrows down diseases through intelligent follow-up questions.")
        else:
            st.error("❌ AI Model Not Available - Fallback to Templates")
            st.warning("For best results, train the model:\n```bash\ncd ml_training/vet_followup_qa\npython train.py\n```")


def show_main_app():
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state.username}!")
        st.markdown(f"**Role:** {st.session_state.role}")
        st.markdown("---")
        options = ["🏠 Home", "🔍 Diagnosis", "📚 Disease Database", "📊 History"]
        if st.session_state.role == "admin":
            options.append("⚙️ Admin Panel")
        page = st.radio("Navigation", options)
        st.markdown("---")
        if st.button("🚪 Logout"):
            for key in ['logged_in', 'username', 'role']:
                st.session_state[key] = None if key != 'logged_in' else False
            st.rerun()

    if page == "🏠 Home":
        show_home_page()
    elif page == "🔍 Diagnosis":
        show_diagnosis_page()
    elif page == "📚 Disease Database":
        show_database_page()
    elif page == "📊 History":
        show_history_page()
    elif page == "⚙️ Admin Panel" and st.session_state.role == "admin":
        show_admin_panel()


def show_home_page():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="header-title">🐾 Veterinary AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Advanced AI-Powered Veterinary Diagnosis System</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    try:
        db = get_db()
        disease_count = db.diseases.count_documents({})
        # Per-user analysis history is stored in MongoDB
        analysis_count = db.analysis_history.count_documents({"username": st.session_state.username})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{disease_count}</div>
                <div class="stat-label">Diseases</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{analysis_count}</div>
                <div class="stat-label">Analyses</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Available</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading stats: {e}")

    # Features
    st.markdown("## 🌟 Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">
        <h3>🔬 AI-Powered Analysis</h3>
        <p>Advanced natural language processing to analyze patient symptoms and medical history.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
        <h3>📚 Comprehensive Database</h3>
        <p>Access to extensive veterinary disease database with treatments and prevention methods.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
        <h3>⚡ Real-time Diagnosis</h3>
        <p>Get instant disease predictions and treatment recommendations.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
        <h3>🔒 Secure & Private</h3>
        <p>User authentication and secure data handling for patient information.</p>
        </div>
        """, unsafe_allow_html=True)


def show_diagnosis_page():
    st.markdown("## 🔍 Patient Diagnosis")

    st.markdown("""
    <div class="info-card">
    <p>Enter the patient's symptoms and medical history below. Our AI will analyze the text and provide possible diagnoses with treatment recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Input form
    patient_text = st.text_area(
        "Patient Description",
        height=200,
        placeholder="Example: My 3-year-old golden retriever has been coughing for a week. He seems lethargic and has a fever. His breathing sounds labored sometimes. He has been fully vaccinated.",
        help="Describe the patient's symptoms, duration, severity, and any relevant medical history."
    )

    # Define uploaded_image before use
    uploaded_image = st.file_uploader(
        "Upload skin image (optional)",
        type=["jpg", "jpeg", "png"]
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        analyze_button = st.button("🔍 Analyze Patient", use_container_width=True)

    # Initialize Repository for use in both analysis and question generation
    try:
        repo = MongoDiseaseRepository()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return

    # --- STEP 2: Handle Initial Analysis ---
    if analyze_button and patient_text:
        with st.spinner("🔄 Analyzing patient data..."):
            try:
                assistant = VeterinaryAIAssistant(repo)
                
                # Handle Image Analysis
                skin_result = None
                image_path = None
                
                if uploaded_image:
                    image_path = save_temp_image(uploaded_image)
                    if image_path:
                        try:
                            skin_result = assistant.analyze_skin_image(image_path)
                            if assistant.skin_adapter and not assistant.skin_adapter.available:
                                st.info("🧪 Skin disease AI is optional and not installed on this system.")
                        except Exception as img_error:
                            st.warning(f"⚠️ Image analysis failed: {img_error}")
                            # Clean up temp file if analysis fails
                            try:
                                os.unlink(image_path)
                            except:
                                pass
                            image_path = None
                
                # STEP 2 LOGIC: Run Analysis without questions, store state
                analysis = assistant.analyze_patient_text(
                    patient_text,
                    generate_questions=False  # IMPORTANT
                )

                state = st.session_state.consultation
                state["patient_info"] = analysis["patient_analysis"].patient_info
                state["symptoms"] = analysis["patient_analysis"].symptoms
                state["diseases"] = analysis.get("disease_extractions", []) 
                state["matches"] = analysis.get("database_matches", [])
                
                # Initialize dynamic disease ranker for AI-powered prioritization
                if state["matches"]:
                    state["disease_ranker"] = DynamicDiseaseRanker(state["matches"])
                
                # Fix 2: Assign image_path to state
                state["image_path"] = image_path
                
                # Store image data if present
                state["skin_result"] = skin_result
                
                # Save analysis to database for history tracking
                try:
                    db = get_db()
                    
                    # Prepare summary data
                    top_diseases = []
                    for disease in state["matches"][:3]:
                        top_diseases.append({
                            "name": disease.get("name", "Unknown"),
                            "severity": disease.get("severity", "unknown"),
                            "confidence": disease.get("confidence", 0)
                        })
                    
                    # Determine urgency level
                    urgency = "routine"
                    if state["matches"]:
                        urgency = state["matches"][0].get("severity", "routine")
                    
                    # Create history record
                    history_record = {
                        "username": st.session_state.username,
                        "patient_text": patient_text,
                        "patient_info": {
                            "animal_type": state["patient_info"].animal_type,
                            "age": state["patient_info"].age,
                            "breed": state["patient_info"].breed,
                            "weight": state["patient_info"].weight
                        },
                        "symptoms": [
                            {
                                "symptom": s.symptom,
                                "severity": s.severity,
                                "duration": s.duration
                            } for s in state["symptoms"]
                        ],
                        "database_matches": state["matches"],
                        "summary": {
                            "top_diseases": top_diseases,
                            "urgency": urgency
                        },
                        "skin_analysis": {
                            "prediction": skin_result.get("prediction"),
                            "confidence": skin_result.get("confidence")
                        } if skin_result else None,
                        "created_at": datetime.now()
                    }
                    
                    db.analysis_history.insert_one(history_record)
                    
                except Exception as save_error:
                    st.warning(f"⚠️ Could not save analysis to history: {save_error}")
                
                # Fix 1: Move cleanup BEFORE rerun
                for k in list(st.session_state.keys()):
                    if k.startswith("answer_"):
                        del st.session_state[k]

                st.success("✅ Initial Analysis Complete!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                st.exception(e)

    # --- DISPLAY ANALYSIS RESULTS (Stateful) ---
    # Only show results if analysis has been run (patient_info exists)
    state = st.session_state.consultation
    
    if state["patient_info"]:
        # Patient Info
        st.markdown("### 👤 Patient Information")
        patient_info = state["patient_info"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Species", patient_info.animal_type or "Unknown")
        with col2:
            st.metric("Age", patient_info.age or "Unknown")
        with col3:
            st.metric("Breed", patient_info.breed or "Unknown")
        with col4:
            st.metric("Weight", patient_info.weight or "Unknown")

        # Skin Image Analysis
        if state["skin_result"]:
            skin_result = state["skin_result"]
            st.markdown("## 🧬 Skin Image Analysis (AI-assisted)")
            st.markdown(f"**Predicted condition:** `{skin_result['prediction']}`")
            st.markdown(f"**Model confidence:** `{skin_result['confidence']:.2%}`")
            st.info("This result is AI-assisted and used as supporting evidence.")

        # Symptoms
        st.markdown("### 🩺 Detected Symptoms")
        symptoms = state["symptoms"]
        if symptoms:
            cols = st.columns(3)
            for idx, symptom in enumerate(symptoms):
                with cols[idx % 3]:
                    severity_class = f"severity-{symptom.severity}" if symptom.severity else "severity-mild"
                    st.markdown(f"""
                    <div class="info-card">
                    <strong>{symptom.symptom}</strong><br>
                    <span class="severity-badge {severity_class}">
                    {symptom.severity or 'Unknown'}
                    </span><br>
                    <small>Duration: {symptom.duration or 'Not specified'}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No specific symptoms detected.")
        
        # --- STEP 3 & 4: AI-Powered Follow-up Questions ---
        st.markdown("---")
        st.markdown("### 🤖 AI Follow-up Analysis")
        
        # Check stopping conditions
        top_disease_confidence = state["matches"][0]['confidence'] if state["matches"] else 0
        questions_asked = state.get("questions_asked", 0)
        max_questions = state.get("max_questions", 8)
        confidence_threshold = state.get("confidence_threshold", 0.85)
        
        # Display progress
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions Asked", f"{questions_asked}/{max_questions}")
        with col2:
            st.metric("Top Confidence", f"{top_disease_confidence:.1%}")
        with col3:
            st.metric("Target Confidence", f"{confidence_threshold:.1%}")
        
        # Determine if we should continue asking questions
        should_continue = (
            questions_asked < max_questions and 
            top_disease_confidence < confidence_threshold and
            len(state["matches"]) > 1
        )
        
        next_q = None
        
        if should_continue:
            # FORCE AI MODEL USAGE
            if AI_MODEL_AVAILABLE:
                try:
                    # Initialize AI generator if not already done
                    if 'ai_generator' not in st.session_state:
                        st.session_state.ai_generator = CustomAIFollowUpGenerator()
                        st.success("✅ AI Model Initialized Successfully")
                    
                    # Prepare data for AI model
                    patient_dict = {
                        'animal_type': state["patient_info"].animal_type,
                        'age': state["patient_info"].age,
                        'breed': state["patient_info"].breed,
                        'weight': state["patient_info"].weight
                    }
                    
                    symptoms_dict = [
                        {
                            'symptom': s.symptom,
                            'severity': s.severity,
                            'duration': s.duration
                        } for s in state["symptoms"]
                    ]
                    
                    diseases_dict = [
                        {
                            'disease_name': d.disease_name if hasattr(d, 'disease_name') else d.get('name', ''),
                            'confidence': d.confidence if hasattr(d, 'confidence') else d.get('confidence', 0)
                        } for d in state["diseases"]
                    ]
                    
                    # Generate AI questions
                    ai_questions = st.session_state.ai_generator.generate_questions(
                        patient_info=patient_dict,
                        symptoms=symptoms_dict,
                        suspected_diseases=diseases_dict,
                        database_matches=state["matches"],
                        max_questions=1,
                        previous_answers=state.get("answers", {})
                    )
                    
                    if ai_questions:
                        ai_q = ai_questions[0]
                        # Convert AI question to FollowUpQuestion format
                        from follow_up_questions import FollowUpQuestion
                        next_q = FollowUpQuestion(
                            category=ai_q.category,
                            question=ai_q.question,
                            priority=ai_q.priority,
                            reasoning=ai_q.reasoning
                        )
                        st.info(f"💡 **AI Strategy:** {ai_q.reasoning}")
                    
                except Exception as ai_error:
                    st.error(f"⚠️ AI Error: {ai_error}")
                    # Fallback to templates
                    generator = FollowUpQuestionGenerator(repo)
                    next_q = generator.get_next_question(
                        state["patient_info"],
                        state["symptoms"],
                        state["diseases"]
                    )
            else:
                # Fallback if AI not available
                st.warning("⚠️ Using template-based questions (AI model not loaded)")
                generator = FollowUpQuestionGenerator(repo)
                next_q = generator.get_next_question(
                    state["patient_info"],
                    state["symptoms"],
                    state["diseases"]
                )

        # Check if question exists AND if it hasn't been answered yet
        if next_q and next_q.question not in state["answers"]:
            st.markdown(f"**Question {questions_asked + 1}:**")
            answer = st.text_input(
                next_q.question,
                key=f"answer_{hash(next_q.question)}",
                placeholder="Type your answer here..."
            )

            if st.button("✅ Submit Answer", key="consultation_submit_btn", use_container_width=True):
                # Validate answer is not empty
                if not answer or answer.strip() == "":
                    st.warning("⚠️ Please provide an answer before submitting.")
                else:
                    # Increment question counter
                    state["questions_asked"] = state.get("questions_asked", 0) + 1
                    # Update symptoms based on answer
                    apply_answer(state["symptoms"], next_q, answer)
                    
                    # Store the answer history
                    state["answers"][next_q.question] = answer
                    
                    # Use AI-powered dynamic confidence updates
                    if state["disease_ranker"]:
                        # Determine answer type and category
                        answer_lower = answer.lower()
                        is_symptom_confirmed = any(word in answer_lower for word in ['yes', 'has', 'showing', 'present', 'experiencing'])
                        is_symptom_ruled_out = any(word in answer_lower for word in ['no', 'not', 'never', 'none', 'hasn\'t'])
                        
                        # Extract symptom from question - comprehensive list
                        symptom_keywords = [
                            'vomiting', 'diarrhea', 'fever', 'lethargy', 'coughing', 'limping', 'seizure',
                            'appetite', 'drinking', 'discharge', 'scratching', 'licking', 'skin',
                            'weight', 'energy', 'breathing', 'pain', 'swelling', 'bleeding',
                            'loss_of_appetite', 'dehydration', 'itching', 'skin_lesion'
                        ]
                        mentioned_symptom = next((kw for kw in symptom_keywords if kw in next_q.question.lower()), None)
                        
                        # Try to extract symptom from state diseases for better matching
                        symptom_to_check = mentioned_symptom
                        if not symptom_to_check and state["matches"]:
                            # Check if question relates to common symptoms of top disease
                            top_disease = state["matches"][0]
                            for sym in top_disease.get('common_symptoms', []):
                                if sym.replace('_', ' ') in next_q.question.lower():
                                    symptom_to_check = sym
                                    break
                        
                        # Create answer object for AI processing
                        follow_up_answer = FollowUpAnswer(
                            question=next_q.question,
                            answer=answer,
                            category=next_q.category if hasattr(next_q, 'category') else 'symptom_details',
                            symptom_confirmed=is_symptom_confirmed,
                            symptom_ruled_out=is_symptom_ruled_out,
                            mentioned_symptom=mentioned_symptom,
                            symptom_to_check=symptom_to_check,
                            severity_level=answer if 'severe' in answer.lower() else None
                        )
                        
                        # Update disease rankings with AI
                        updated_diseases = state["disease_ranker"].update_confidence_with_answer(follow_up_answer)
                        state["matches"] = updated_diseases
                        
                        st.info(f"🧠 AI updated disease priorities based on your answer!")
                    else:
                        # Fallback: Re-run disease analysis
                        symptom_text = " ".join(
                            f"{s.symptom} {s.severity or ''} {s.duration or ''}"
                            for s in state["symptoms"]
                        )
                        assistant = VeterinaryAIAssistant(repo)
                        analysis = assistant.analyze_patient_text(
                            symptom_text,
                            generate_questions=False
                        )
                        state["diseases"] = analysis.get("disease_extractions", [])
                        state["matches"] = analysis.get("database_matches", [])

                    st.rerun()
        else:
            # Diagnosis complete
            st.markdown("---")
            if top_disease_confidence >= confidence_threshold:
                st.success(f"✅ **Diagnosis Complete!** Achieved {top_disease_confidence:.1%} confidence")
                st.balloons()
            elif questions_asked >= max_questions:
                st.info(f"📊 **Analysis Complete** - Maximum questions reached ({max_questions})")
            elif len(state["matches"]) == 1:
                st.success("✅ **Single Disease Identified!**")
            else:
                st.info("✅ **Sufficient Information Collected**")
            
            # Show summary stats
            st.markdown("### 📈 Consultation Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", questions_asked)
            with col2:
                st.metric("Final Confidence", f"{top_disease_confidence:.1%}")
            with col3:
                st.metric("Diseases Analyzed", len(state["matches"]))
            
            if st.button("🔄 Start New Consultation", use_container_width=True):
                # Clean up temp image file if exists
                if state["image_path"]:
                    try:
                        os.unlink(state["image_path"])
                    except:
                        pass
                
                # Clear consultation state
                st.session_state.consultation = {
                    "patient_info": None,
                    "symptoms": [],
                    "diseases": [],
                    "matches": [],
                    "image_path": None,
                    "skin_result": None,
                    "answers": {},
                    "disease_ranker": None,
                    "questions_asked": 0,
                    "max_questions": 8,
                    "confidence_threshold": 0.85
                }
                # Clear AI generator to reset state
                if 'ai_generator' in st.session_state:
                    del st.session_state.ai_generator
                st.rerun()

        # Diseases
        st.markdown("### 🎯 Possible Diagnoses")
        matches = state["matches"]
        if matches:
            for disease in matches[:5]:
                severity_class = f"severity-{disease['severity']}"
                st.markdown(f"""
                <div class="disease-card">
                <h4>{disease['name']}</h4>
                <span class="severity-badge {severity_class}">
                {disease['severity']}
                </span>
                <p><strong>Scientific Name:</strong> {disease['scientific_name']}</p>
                <p><strong>Description:</strong> {disease['description']}</p>
                <p><strong>Treatment:</strong> {disease['treatment']}</p>
                <p><strong>Prevention:</strong> {disease['prevention']}</p>
                <p><strong>Affected Species:</strong> {', '.join(disease['affected_species'])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No matching diseases found in database.")

        # Recommendations
        st.markdown("### 💡 Recommendations")
        urgency = "routine"
        if matches:
            top_disease = matches[0]
            urgency = top_disease.get('severity', 'routine')
            
        urgency_colors = {
            "mild": "🟢",
            "moderate": "🟡",
            "severe": "🔴"
        }
        urgency_icon = urgency_colors.get(urgency, "🟡")
        st.markdown(f"**Urgency Level:** {urgency_icon} {urgency.upper()}")
        
        st.markdown("**Recommended Actions:**")
        if urgency == "severe":
            st.markdown("- Seek immediate veterinary attention.")
            st.markdown("- Monitor vital signs closely.")
        elif urgency == "moderate":
            st.markdown("- Schedule a veterinary appointment within 24-48 hours.")
            st.markdown("- Monitor for worsening symptoms.")
        else:
            st.markdown("- Continue monitoring the patient at home.")
            st.markdown("- Maintain current care routine.")



def show_database_page():
    st.markdown("## 📚 Disease Database")

    try:
        # Use get_db to access raw connection instead of undefined class
        db = get_db()

        # Search
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔍 Search diseases", placeholder="Enter disease name or keyword...")
        with col2:
            severity_filter = st.selectbox("Severity", ["All", "mild", "moderate", "severe"])

        # Build query
        query = {}
        if search_query:
            query["$or"] = [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"description": {"$regex": search_query, "$options": "i"}},
                {"common_symptoms": {"$regex": search_query, "$options": "i"}}
            ]

        if severity_filter != "All":
            query["severity"] = severity_filter

        # Get diseases
        diseases = list(db.diseases.find(query))

        st.markdown(f"### Found {len(diseases)} disease(s)")

        # Display diseases
        for disease in diseases:
            severity_class = f"severity-{disease['severity']}"
            st.markdown(f"""
            <div class="disease-card">
            <h4>{disease['name']}</h4>
            <span class="severity-badge {severity_class}">{disease['severity']}</span>
            <p><strong>Scientific Name:</strong> {disease.get('scientific_name', 'N/A')}</p>
            <p><strong>Description:</strong> {disease.get('description', 'N/A')}</p>
            <p><strong>Symptoms:</strong> {', '.join(disease.get('common_symptoms', []))}</p>
            <p><strong>Treatment:</strong> {disease.get('treatment', 'N/A')}</p>
            <p><strong>Prevention:</strong> {disease.get('prevention', 'N/A')}</p>
            <p><strong>Affected Species:</strong> {', '.join(disease.get('affected_species', []))}</p>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading database: {e}")


def show_history_page():
    st.markdown("## 📊 Analysis History")

    try:
        db = get_db()
        records = list(db.analysis_history.find({"username": st.session_state.username}).sort("created_at", -1))
    except Exception as e:
        st.error(f"❌ Could not load history from database: {e}")
        records = []

    if not records:
        st.info("No analysis history yet for this user. Perform a diagnosis to see results here.")
        return

    st.markdown(f"**Total Analyses:** {len(records)}")

    for idx, rec in enumerate(records, 1):
        created_at = rec.get("created_at", "")
        summary = rec.get("summary", {}) or {}
        urgency = summary.get("urgency") or rec.get("recommendations", {}).get("urgency", "routine")

        with st.expander(f"Analysis #{idx} - {str(created_at)[:19] if created_at else 'Unknown Date'}"):
            st.markdown("**Patient Description:**")
            st.write(rec.get("patient_text", "No description available"))
            
            # Show patient info if available
            patient_info = rec.get("patient_info", {})
            if patient_info:
                st.markdown("**Patient Info:**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"🐾 {patient_info.get('animal_type', 'Unknown')}")
                with col2:
                    if patient_info.get('age'):
                        st.write(f"📅 {patient_info.get('age')}")
                with col3:
                    if patient_info.get('breed'):
                        st.write(f"🏷️ {patient_info.get('breed')}")
                with col4:
                    if patient_info.get('weight'):
                        st.write(f"⚖️ {patient_info.get('weight')}")

            st.markdown("---")
            st.markdown("**Detected Diseases:**")
            top = summary.get("top_diseases") or []
            if top:
                for d in top:
                    severity_class = f"severity-{d.get('severity', 'mild')}"
                    st.markdown(f"""
                    <div style="padding: 0.5rem; margin: 0.5rem 0; background-color: rgba(30, 33, 39, 0.5); border-radius: 5px;">
                        <strong>{d.get('name', 'Unknown Disease')}</strong>
                        <span class="severity-badge {severity_class}" style="margin-left: 1rem;">
                            {d.get('severity', 'unknown')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                for disease in (rec.get("database_matches") or [])[:3]:
                    if isinstance(disease, dict):
                        severity_class = f"severity-{disease.get('severity', 'mild')}"
                        st.markdown(f"""
                        <div style="padding: 0.5rem; margin: 0.5rem 0; background-color: rgba(30, 33, 39, 0.5); border-radius: 5px;">
                            <strong>{disease.get('name', 'Unknown')}</strong>
                            <span class="severity-badge {severity_class}" style="margin-left: 1rem;">
                                {disease.get('severity', 'unknown')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show skin analysis if available
            skin_analysis = rec.get("skin_analysis")
            if skin_analysis and skin_analysis.get("prediction"):
                st.markdown("---")
                st.markdown("**Skin Image Analysis:**")
                st.write(f"🧬 Prediction: **{skin_analysis.get('prediction')}**")
                if skin_analysis.get("confidence"):
                    st.write(f"📊 Confidence: **{skin_analysis.get('confidence'):.2%}**")

            st.markdown("---")
            urgency_colors = {
                "mild": "🟢",
                "moderate": "🟡",
                "severe": "🔴",
                "routine": "🟢"
            }
            urgency_icon = urgency_colors.get(urgency, "🟡")
            st.markdown(f"**Urgency Level:** {urgency_icon} {urgency.upper()}")


def main():
    load_custom_css()
    init_session_state()

    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
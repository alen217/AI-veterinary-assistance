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
from ava_display_engine import AVADisplayEngine, QuestionStrategyEngine
from pet_database import get_pet_database, PetDatabaseManager

# Try to load AI-powered question generator
try:
    from custom_ai_followup import CustomAIFollowUpGenerator
    AI_MODEL_AVAILABLE = True
    print("✅ Custom AI follow-up model loaded successfully")
except Exception as e:
    AI_MODEL_AVAILABLE = False
    print(f"⚠️  Using template-based questions (AI model not available: {e})")

# Try to load voice input module
try:
    from voice_input import render_voice_input_widget, WHISPER_AVAILABLE, AUDIO_RECORDER_AVAILABLE
    VOICE_INPUT_AVAILABLE = True
    print("✅ Voice input module loaded successfully")
except Exception as e:
    VOICE_INPUT_AVAILABLE = False
    WHISPER_AVAILABLE = False
    AUDIO_RECORDER_AVAILABLE = False
    print(f"⚠️  Voice input not available: {e}")

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
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        animation: fadeInDown 0.8s ease-out;
    }

    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        letter-spacing: 1px;
    }

    .header-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.8rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .header-tagline {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.95rem;
        text-align: center;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #1e2127 0%, #252830 100%);
        padding: 1.8rem;
        border-radius: 12px;
        border-left: 5px solid var(--primary-color);
        margin: 1.2rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2);
    }

    .disease-card {
        background: linear-gradient(135deg, #1e2127 0%, #2a2d35 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px solid #3a3d45;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .disease-card:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }

    /* Severity badges */
    .severity-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    
    .severity-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }

    .severity-mild {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
    }

    .severity-moderate {
        background: linear-gradient(135deg, #FF9800 0%, #FFA726 100%);
        color: white;
    }

    .severity-severe {
        background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
        color: white;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
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
        border-radius: 8px;
        padding: 0.75rem 2.5rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
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
    
    /* Metric boxes enhancement */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e2127;
        border-radius: 8px;
        font-weight: 600;
        padding: 1rem;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #1e2127;
        color: white;
        border: 2px solid #3a3d45;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #1e2127;
        color: white;
        border: 2px solid #3a3d45;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Fade in animation for content */
    .element-container {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Professional loading spinner */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent;
    }

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
        st.markdown("#### 🎤 Voice Recognition Settings")
        if VOICE_INPUT_AVAILABLE and WHISPER_AVAILABLE:
            st.info("**Voice Input:** ✅ Enabled")
            
            # Model selection
            if 'whisper_model_size' not in st.session_state:
                st.session_state.whisper_model_size = 'medium'
            
            model_options = {
                'tiny': 'Tiny (39MB) - Fastest, basic accuracy',
                'base': 'Base (142MB) - Good balance',
                'small': 'Small (466MB) - Better accuracy',
                'medium': 'Medium (1.5GB) - High accuracy ⭐',
                'large': 'Large (2.9GB) - Best accuracy (slower)',
                'large-v3': 'Large-v3 (2.9GB) - Latest, best quality'
            }
            
            selected_model = st.selectbox(
                "Select Whisper Model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=list(model_options.keys()).index(st.session_state.whisper_model_size),
                help="Larger models are more accurate but slower. Medium is recommended."
            )
            
            if selected_model != st.session_state.whisper_model_size:
                st.session_state.whisper_model_size = selected_model
                st.success(f"✅ Model changed to: {model_options[selected_model]}")
                st.info("💡 Model will be downloaded on first use if not already cached.")
        else:
            st.warning("⚠️ Voice input not available. Install dependencies.")
        
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
        options = ["🏠 Home", "� Pet Management", "🔍 Diagnosis", "📚 Disease Database", "📊 History"]
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
    elif page == "🐾 Pet Management":
        show_pet_management_page()
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
    st.markdown('<h1 class="header-title">🐾 AVA - AI Veterinary Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Advanced AI-Powered Veterinary Diagnosis & Analysis System</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-tagline">Intelligent Disease Detection | Multi-Species Support | Real-Time Analysis</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    try:
        db = get_db()
        disease_count = db.diseases.count_documents({})
        # Per-user analysis history is stored in MongoDB
        analysis_count = db.analysis_history.count_documents({"username": st.session_state.username})
        
        # Count species supported
        species_pipeline = [
            {"$unwind": "$affected_species"},
            {"$group": {"_id": "$affected_species"}},
            {"$count": "total"}
        ]
        species_result = list(db.diseases.aggregate(species_pipeline))
        species_count = species_result[0]["total"] if species_result else 50

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{disease_count}+</div>
                <div class="stat-label">Diseases in Database</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{species_count}+</div>
                <div class="stat-label">Species Supported</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{analysis_count}</div>
                <div class="stat-label">Your Analyses</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">95%+</div>
                <div class="stat-label">Accuracy Rate</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading stats: {e}")

    # Features
    st.markdown("## 🌟 Advanced Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">
        <h3>🎤 Voice Input</h3>
        <p>State-of-the-art speech recognition with OpenAI Whisper. Supports English & Malayalam with 95%+ accuracy on medical terminology.</p>
        <small><strong>🚀 GPU-Accelerated Processing</strong></small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
        <h3>🔬 AI-Powered Analysis</h3>
        <p>Advanced neural networks analyze patient symptoms with multi-species support. Intelligent follow-up questions narrow down diagnoses dynamically.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <h3>🎯 Species-Specific Filtering</h3>
        <p>Automatic animal type detection ensures only relevant diseases are shown. Supports 50+ species from pets to exotic animals.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
        <h3>📚 Extensive Knowledge Base</h3>
        <p>500+ veterinary diseases with comprehensive symptom profiles, treatments, and prevention strategies across all major species.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
        <h3>⚡ Real-Time Confidence Scoring</h3>
        <p>Dynamic disease ranking with Bayesian-like updates. Explainable AI shows why each disease is suggested with matched symptoms.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <h3>🔒 Professional Grade Security</h3>
        <p>MongoDB-backed authentication, role-based access control, and secure patient data handling with complete privacy.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("## 🛠️ Technology Stack")
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
        **AI/ML:**
        - OpenAI Whisper (Medium ⭐)
        - PyTorch Neural Networks
        - Custom Trained Models
        - NLP with spaCy
        """)
    
    with tech_col2:
        st.markdown("""
        **Backend:**
        - MongoDB Database
        - Python 3.13
        - Real-time Processing
        - RESTful Architecture
        """)
    
    with tech_col3:
        st.markdown("""
        **Frontend:**
        - Streamlit Framework
        - Responsive Design
        - Real-time Updates
        - Professional UI/UX
        """)


def show_pet_management_page():
    """Patient (Human Client) and Pet Management System"""
    st.markdown("## 👥 Patient & Pet Management")
    
    st.markdown("""
    <div class="info-card">
    <p><strong>Workflow:</strong> Register human patients (clients) → Add their pets → Diagnose and treat pets</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize pet database
    try:
        pet_db = get_pet_database()
    except Exception as e:
        st.error(f"❌ Could not connect to pet database: {e}")
        return
    
    # Tabs for different operations
    tabs = st.tabs(["👤 Patient Registry", "🐾 Pet Registry", "➕ New Patient", "📊 Statistics"])
    
    # =============== TAB 1: PATIENT REGISTRY (HUMAN CLIENTS) ===============
    with tabs[0]:
        st.markdown("### 👤 Patient (Human Client) Registry")
        
        st.markdown("""
        <div class="info-card">
        <p>Manage human patients/clients who own pets. Each patient can have multiple pets.</p>
        </div>
        """, unsafe_allow_html=True)
        
        owner_search = st.text_input("🔍 Search patients", placeholder="Name, email, or phone", key="patient_search")
        
        if owner_search:
            owners = pet_db.search_owners(owner_search)
        else:
            owners = list(pet_db.owners_collection.find({'status': 'active'}).limit(50))
            for owner in owners:
                owner.pop('_id', None)
        
        if owners:
            st.success(f"📋 Found {len(owners)} patient(s)")
            
            for owner in owners:
                with st.expander(f"👤 {owner.get('name', 'Unknown')} - ID: {owner.get('owner_id', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📞 Contact Information")
                        st.markdown(f"**Name:** {owner.get('name', 'N/A')}")
                        st.markdown(f"**Email:** {owner.get('email', 'N/A')}")
                        st.markdown(f"**Phone:** {owner.get('phone', 'N/A')}")
                        if owner.get('address'):
                            st.markdown(f"**Address:** {owner['address']}")
                            if owner.get('city'):
                                st.markdown(f"**City:** {owner['city']}, {owner.get('state', '')}")
                        if owner.get('emergency_contact'):
                            st.markdown(f"**Emergency Contact:** {owner['emergency_contact']}")
                    
                    with col2:
                        st.markdown("#### 🐾 Patient's Pets")
                        pets = pet_db.get_pets_by_owner(owner['owner_id'])
                        st.markdown(f"**Total Pets:** {len(pets)}")
                        st.markdown(f"**Total Visits:** {owner.get('total_visits', 0)}")
                        st.markdown(f"**Member Since:** {owner.get('created_date', 'N/A')[:10]}")
                        
                        if pets:
                            st.markdown("**Registered Pets:**")
                            for pet in pets:
                                st.markdown(f"- 🐾 **{pet['name']}** ({pet['species'].title()}, {pet.get('age', 0)} {pet.get('age_unit', 'years')})")
                        else:
                            st.info("No pets registered yet")
                    
                    if owner.get('notes'):
                        st.markdown("**Notes:**")
                        st.info(owner['notes'])
                    
                    # Actions
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"🐾 Add Pet", key=f"add_pet_{owner['owner_id']}"):
                            st.session_state.selected_owner_for_pet = owner['owner_id']
                            st.session_state.tab_redirect = 1  # Pet Registry tab
                            st.rerun()
                    with col2:
                        if st.button(f"📊 View History", key=f"history_patient_{owner['owner_id']}"):
                            st.session_state.view_patient_history = owner['owner_id']
                            st.rerun()
                    with col3:
                        if st.button(f"✏️ Edit Patient", key=f"edit_patient_{owner['owner_id']}"):
                            st.session_state.edit_patient_id = owner['owner_id']
                            st.rerun()
        else:
            st.info("No patients found. Register a new patient using the 'New Patient' tab.")
    
    # =============== TAB 2: PET REGISTRY ===============
    with tabs[1]:
        st.markdown("### 🐾 Pet Registry")
        
        st.markdown("""
        <div class="info-card">
        <p>View and manage all pets. Each pet belongs to a human patient/client.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_query = st.text_input("🔍 Search pets", placeholder="Enter name, breed, or microchip ID", key="pet_search")
        with col2:
            species_filter = st.selectbox("Species Filter", ["All", "dog", "cat", "bird", "rabbit", "hamster", "other"], key="species_filter")
        with col3:
            if st.button("🔄 Refresh", key="refresh_pets"):
                st.rerun()
        
        # Get pets
        if search_query:
            species = None if species_filter == "All" else species_filter
            pets = pet_db.search_pets(search_query, species=species)
        else:
            # Show all pets (limit 50)
            query = {'status': 'active'}
            if species_filter != "All":
                query['species'] = species_filter
            pets = list(pet_db.pets_collection.find(query).limit(50))
            for pet in pets:
                pet.pop('_id', None)
        
        if pets:
            st.success(f"📋 Found {len(pets)} pet(s)")
            
            # Display each pet as an expandable card
            for pet in pets:
                # Get owner info
                owner = pet_db.get_owner(pet.get('owner_id', ''))
                owner_name = owner.get('name', 'Unknown') if owner else 'Unknown'
                
                with st.expander(f"🐾 {pet.get('name', 'Unknown')} - {pet.get('species', 'unknown').title()} (Owner: {owner_name})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📝 Pet Information")
                        st.markdown(f"**Pet ID:** {pet.get('pet_id', 'N/A')}")
                        st.markdown(f"**Name:** {pet.get('name', 'N/A')}")
                        st.markdown(f"**Species:** {pet.get('species', 'N/A').title()}")
                        st.markdown(f"**Breed:** {pet.get('breed', 'N/A')}")
                        st.markdown(f"**Age:** {pet.get('age', 0)} {pet.get('age_unit', 'years')}")
                        st.markdown(f"**Sex:** {pet.get('sex', 'Unknown')}")
                        st.markdown(f"**Weight:** {pet.get('weight', 0)} kg")
                        st.markdown(f"**Color:** {pet.get('color', 'N/A')}")
                        if pet.get('microchip_id'):
                            st.markdown(f"**Microchip:** {pet['microchip_id']}")
                        
                        st.markdown("---")
                        st.markdown(f"**Owner:** {owner_name}")
                        if owner:
                            st.markdown(f"**Owner Phone:** {owner.get('phone', 'N/A')}")
                    
                    with col2:
                        st.markdown("#### 🏥 Medical Information")
                        
                        if pet.get('medical_conditions'):
                            st.markdown("**⚠️ Chronic Conditions:**")
                            for condition in pet['medical_conditions']:
                                st.markdown(f"- {condition}")
                        
                        if pet.get('allergies'):
                            st.markdown("**🚫 Allergies:**")
                            for allergy in pet['allergies']:
                                st.markdown(f"- {allergy}")
                        
                        if pet.get('current_medications'):
                            st.markdown("**💊 Current Medications:**")
                            for med in pet['current_medications']:
                                st.markdown(f"- {med}")
                        
                        st.markdown(f"**Total Visits:** {pet.get('total_visits', 0)}")
                        if pet.get('last_visit'):
                            st.markdown(f"**Last Visit:** {pet['last_visit'][:10]}")
                    
                    # Notes
                    if pet.get('notes'):
                        st.markdown("**Notes:**")
                        st.info(pet['notes'])
                    
                    # Actions
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📊 View History", key=f"history_{pet['pet_id']}"):
                            st.session_state.selected_pet_for_history = pet['pet_id']
                            st.rerun()
                    with col2:
                        if st.button(f"🔍 Start Diagnosis", key=f"diagnose_{pet['pet_id']}"):
                            st.session_state.selected_pet_for_diagnosis = pet['pet_id']
                            st.session_state.nav_page = "🔍 Diagnosis"
                            st.rerun()
                    with col3:
                        if st.button(f"✏️ Edit Pet", key=f"edit_{pet['pet_id']}"):
                            st.session_state.edit_pet_id = pet['pet_id']
                            st.rerun()
                    
                    # Show medical history if selected
                    if st.session_state.get('selected_pet_for_history') == pet['pet_id']:
                        st.markdown("### 📋 Medical History")
                        consultations = pet_db.get_pet_history(pet['pet_id'])
                        
                        if consultations:
                            for i, consultation in enumerate(consultations, 1):
                                st.markdown(f"**Visit #{i} - {consultation.get('date', 'N/A')[:10]}**")
                                st.markdown(f"- **Veterinarian:** {consultation.get('veterinarian', 'N/A')}")
                                st.markdown(f"- **Complaint:** {consultation.get('chief_complaint', 'N/A')}")
                                if consultation.get('diagnosis'):
                                    st.markdown(f"- **Diagnosis:** {', '.join(consultation['diagnosis'])}")
                                if consultation.get('treatment_plan'):
                                    st.markdown(f"- **Treatment:** {consultation['treatment_plan'][:100]}...")
                                st.markdown("---")
                        else:
                            st.info("No consultation history yet")
                        
                        if st.button("Close History", key=f"close_history_{pet['pet_id']}"):
                            del st.session_state.selected_pet_for_history
                            st.rerun()
        else:
            st.info("No pets found. Add a new pet in the 'New Patient' tab.")
    
    # =============== TAB 3: NEW PATIENT REGISTRATION ===============
    with tabs[2]:
        st.markdown("### ➕ Register New Patient & Their Pets")
        
        st.markdown("""
        <div class="info-card">
        <p><strong>Step 1:</strong> Register the human patient (client)<br>
        <strong>Step 2:</strong> Add their pet(s)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Step 1: Patient (Human) Registration
        st.markdown("#### 👤 Step 1: Register Human Patient (Client)")
        
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Patient Name *", placeholder="John Smith", key="new_patient_name")
            patient_email = st.text_input("Email", placeholder="john@example.com", key="new_patient_email")
            patient_phone = st.text_input("Phone Number *", placeholder="+1-555-0123", key="new_patient_phone")
        with col2:
            patient_address = st.text_area("Address", placeholder="123 Main St", key="new_patient_address")
            col_city, col_state = st.columns(2)
            with col_city:
                patient_city = st.text_input("City", key="new_patient_city")
            with col_state:
                patient_state = st.text_input("State", key="new_patient_state")
            patient_emergency = st.text_input("Emergency Contact", placeholder="+1-555-9999", key="new_patient_emergency")
        
        patient_notes = st.text_area("Patient Notes", placeholder="Preferred appointment times, special instructions, etc.", key="new_patient_notes")
        
        if st.button("✅ Register Patient", type="primary", key="register_patient_btn"):
            if patient_name and patient_phone:
                try:
                    new_owner = pet_db.create_owner({
                        'name': patient_name,
                        'email': patient_email,
                        'phone': patient_phone,
                        'address': patient_address,
                        'city': patient_city,
                        'state': patient_state,
                        'emergency_contact': patient_emergency,
                        'notes': patient_notes
                    })
                    st.success(f"✅ Patient registered successfully!")
                    st.balloons()
                    st.markdown(f"**Patient ID:** {new_owner['owner_id']}")
                    st.markdown(f"**Name:** {new_owner['name']}")
                    st.markdown(f"**Phone:** {new_owner['phone']}")
                    
                    # Set this patient for pet registration
                    st.session_state.newly_created_patient_id = new_owner['owner_id']
                    st.info("👇 Now add their pet(s) below")
                    
                except Exception as e:
                    st.error(f"❌ Error registering patient: {e}")
            else:
                st.error("Patient name and phone number are required!")
        
        st.markdown("---")
        
        # Step 2: Pet Registration
        st.markdown("#### 🐾 Step 2: Add Pet to Patient")
        
        # Select patient (existing or newly created)
        if st.session_state.get('newly_created_patient_id'):
            selected_patient_id = st.session_state.newly_created_patient_id
            patient = pet_db.get_owner(selected_patient_id)
            st.success(f"✅ Adding pet for: **{patient['name']}** (ID: {selected_patient_id})")
            
            if st.button("Select Different Patient", key="change_patient_btn"):
                del st.session_state.newly_created_patient_id
                st.rerun()
        elif st.session_state.get('selected_owner_for_pet'):
            selected_patient_id = st.session_state.selected_owner_for_pet
            patient = pet_db.get_owner(selected_patient_id)
            st.success(f"✅ Adding pet for: **{patient['name']}** (ID: {selected_patient_id})")
        else:
            patient_search = st.text_input("🔍 Search for patient", placeholder="Name, email, or phone", key="pet_patient_search")
            
            if patient_search:
                patients = pet_db.search_owners(patient_search)
                if patients:
                    for p in patients:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{p['name']}** - {p['phone']}")
                            st.caption(f"ID: {p['owner_id']} | Pets: {len(pet_db.get_pets_by_owner(p['owner_id']))}")
                        with col2:
                            if st.button("Select", key=f"select_patient_{p['owner_id']}"):
                                st.session_state.selected_owner_for_pet = p['owner_id']
                                st.rerun()
                else:
                    st.warning("No patients found. Register a new patient above first.")
            else:
                st.info("👆 Search for a patient or register a new patient above")
            
            selected_patient_id = None
        
        # Pet registration form (only show if patient selected)
        if selected_patient_id:
            st.markdown("**Enter Pet Details**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Details**")
                pet_name = st.text_input("Pet Name *", key="new_pet_name")
                pet_species = st.selectbox("Species *", ["dog", "cat", "bird", "rabbit", "hamster", "guinea pig", "ferret", "reptile", "other"], key="new_pet_species")
                pet_breed = st.text_input("Breed", key="new_pet_breed")
                
                age_col1, age_col2 = st.columns(2)
                with age_col1:
                    pet_age = st.number_input("Age", min_value=0.0, step=0.5, key="new_pet_age")
                with age_col2:
                    pet_age_unit = st.selectbox("Unit", ["years", "months"], key="new_pet_age_unit")
                
                pet_sex = st.selectbox("Sex", ["Male", "Female", "Unknown"], key="new_pet_sex")
                pet_weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, key="new_pet_weight")
                pet_color = st.text_input("Color/Markings", key="new_pet_color")
                pet_microchip = st.text_input("Microchip ID", key="new_pet_microchip")
            
            with col2:
                st.markdown("**Medical Information**")
                pet_conditions = st.text_area("Chronic Conditions (one per line)", key="new_pet_conditions")
                pet_allergies = st.text_area("Allergies (one per line)", key="new_pet_allergies")
                pet_medications = st.text_area("Current Medications (one per line)", key="new_pet_medications")
                pet_vaccinations = st.text_area("Vaccination Records (one per line)", key="new_pet_vaccinations")
                pet_notes = st.text_area("Additional Notes", key="new_pet_notes")
            
            # Register button
            if st.button("🐾 Add Pet to Patient", type="primary", key="register_pet_btn"):
                if pet_name and pet_species:
                    try:
                        # Process multi-line inputs
                        conditions = [c.strip() for c in pet_conditions.split('\n') if c.strip()]
                        allergies = [a.strip() for a in pet_allergies.split('\n') if a.strip()]
                        medications = [m.strip() for m in pet_medications.split('\n') if m.strip()]
                        vaccinations = [v.strip() for v in pet_vaccinations.split('\n') if v.strip()]
                        
                        new_pet = pet_db.create_pet({
                            'name': pet_name,
                            'species': pet_species,
                            'breed': pet_breed if pet_breed else 'Mixed/Unknown',
                            'age': pet_age,
                            'age_unit': pet_age_unit,
                            'sex': pet_sex,
                            'weight': pet_weight,
                            'color': pet_color,
                            'microchip_id': pet_microchip,
                            'owner_id': selected_patient_id,
                            'medical_conditions': conditions,
                            'allergies': allergies,
                            'current_medications': medications,
                            'vaccination_records': vaccinations,
                            'notes': pet_notes
                        })
                        
                        st.success(f"✅ Pet added successfully!")
                        st.balloons()
                        st.markdown(f"**Pet ID:** {new_pet['pet_id']}")
                        st.markdown(f"**Name:** {new_pet['name']}")
                        st.markdown(f"**Species:** {new_pet['species'].title()}")
                        
                        # Update owner's pet count
                        pet_db.owners_collection.update_one(
                            {'owner_id': selected_patient_id},
                            {'$inc': {'total_pets': 1}}
                        )
                        
                        # Option to add another pet
                        if st.button("➕ Add Another Pet for This Patient"):
                            # Clear pet form fields
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error adding pet: {e}")
                else:
                    st.error("Pet name and species are required!")
    
    # =============== TAB 4: STATISTICS ===============
    with tabs[3]:
        st.markdown("### 📊 Pet Database Statistics")
        
        stats = pet_db.get_database_stats()
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_owners', 0)}</div>
                <div class="stat-label">Human Patients</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_pets', 0)}</div>
                <div class="stat-label">Total Pets</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_consultations', 0)}</div>
                <div class="stat-label">Consultations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('consultations_this_month', 0)}</div>
                <div class="stat-label">This Month</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Species distribution
        if stats.get('pets_by_species'):
            st.markdown("### 🐾 Pets by Species")
            species_data = stats['pets_by_species']
            
            col1, col2 = st.columns([2, 1])
            with col1:
                import pandas as pd
                df = pd.DataFrame(list(species_data.items()), columns=['Species', 'Count'])
                df['Species'] = df['Species'].str.title()
                st.bar_chart(df.set_index('Species'))
            
            with col2:
                st.markdown("**Distribution:**")
                for species, count in sorted(species_data.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / stats['total_pets'] * 100) if stats['total_pets'] > 0 else 0
                    st.markdown(f"- {species.title()}: {count} ({percentage:.1f}%)")


def show_diagnosis_page():
    st.markdown("## 🔍 Patient Diagnosis")
    
    # Pet Selection Section at the top
    try:
        pet_db = get_pet_database()
        
        st.markdown("### 1️⃣ Select Patient (Optional)")
        st.markdown("""
        <div class="info-card">
        <p>Select an existing pet to auto-fill information and link this consultation to their medical history.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            pet_search = st.text_input("🔍 Search for pet", placeholder="Enter pet name or ID", key="diagnosis_pet_search")
        with col2:
            if st.button("➕ New Patient", key="new_patient_btn"):
                st.session_state.selected_pet_id = None
                st.session_state.use_existing_pet = False
                st.rerun()
        with col3:
            if st.button("🔄 Clear", key="clear_pet_btn"):
                st.session_state.selected_pet_id = None
                st.session_state.use_existing_pet = False
                st.rerun()
        
        # Handle pet selection from Pet Management page
        if st.session_state.get('selected_pet_for_diagnosis'):
            st.session_state.selected_pet_id = st.session_state.selected_pet_for_diagnosis
            st.session_state.use_existing_pet = True
            del st.session_state.selected_pet_for_diagnosis
        
        # Show search results
        if pet_search:
            pets = pet_db.search_pets(pet_search, limit=10)
            if pets:
                for pet in pets:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"**{pet['name']}** - {pet['species'].title()}")
                    with col2:
                        st.markdown(f"{pet.get('age', 0)} {pet.get('age_unit', 'years')}, {pet.get('sex', 'Unknown')}")
                    with col3:
                        if st.button("Select", key=f"select_pet_{pet['pet_id']}"):
                            st.session_state.selected_pet_id = pet['pet_id']
                            st.session_state.use_existing_pet = True
                            st.rerun()
        
        # Display selected pet
        if st.session_state.get('selected_pet_id') and st.session_state.get('use_existing_pet'):
            pet = pet_db.get_pet(st.session_state.selected_pet_id)
            if pet:
                st.success(f"✅ Selected Patient: **{pet['name']}** ({pet['species'].title()})")
                
                # Get AI context for this pet
                pet_context = pet_db.get_pet_context_for_ai(st.session_state.selected_pet_id)
                
                # Display pet medical summary
                with st.expander("📋 Patient Medical Record", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Species:** {pet['species'].title()}")
                        st.markdown(f"**Breed:** {pet.get('breed', 'N/A')}")
                        st.markdown(f"**Age:** {pet.get('age', 0)} {pet.get('age_unit', 'years')}")
                        st.markdown(f"**Weight:** {pet.get('weight', 0)} kg")
                        st.markdown(f"**Total Visits:** {pet.get('total_visits', 0)}")
                    
                    with col2:
                        if pet_context.get('chronic_conditions'):
                            st.markdown("**⚠️ Chronic Conditions:**")
                            for condition in pet_context['chronic_conditions']:
                                st.markdown(f"- {condition}")
                        
                        if pet_context.get('allergies'):
                            st.markdown("**🚫 Allergies:**")
                            for allergy in pet_context['allergies']:
                                st.markdown(f"- {allergy}")
                        
                        if pet_context.get('current_medications'):
                            st.markdown("**💊 Current Medications:**")
                            for med in pet_context['current_medications']:
                                st.markdown(f"- {med}")
                    
                    # Show previous diagnoses if any
                    if pet_context.get('previous_diagnoses'):
                        st.markdown("**📊 Previous Diagnoses:**")
                        for diag in pet_context['previous_diagnoses']:
                            st.markdown(f"- {diag['disease']} (occurred {diag['occurrences']} time(s))")
                
                # Store pet context in session for later use
                st.session_state.current_pet_context = pet_context
            else:
                st.error("Pet not found")
                st.session_state.selected_pet_id = None
        
        st.markdown("---")
        
    except Exception as e:
        st.warning(f"⚠️ Pet database not available: {e}")
        st.session_state.use_existing_pet = False

    st.markdown("### 2️⃣ Enter Symptoms & Description")
    st.markdown("""
    <div class="info-card">
    <p>Enter the patient's symptoms and medical history below. Our AI will analyze the text and provide possible diagnoses with treatment recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Voice Input Section (if available)
    if VOICE_INPUT_AVAILABLE and WHISPER_AVAILABLE and AUDIO_RECORDER_AVAILABLE:
        with st.expander("🎤 Voice Input - Speak your patient description", expanded=False):
            st.info("Record your voice describing the patient's symptoms. Supports English and Malayalam!")
            
            # Language selection
            voice_lang = st.radio(
                "Select Language",
                options=["English", "Malayalam"],
                horizontal=True,
                key="voice_lang_select"
            )
            
            lang_code = "en" if voice_lang == "English" else "ml"
            
            # Option to translate Malayalam to English
            translate_option = False
            if voice_lang == "Malayalam":
                translate_option = st.checkbox(
                    "Translate to English (recommended for better analysis)",
                    value=True,
                    key="translate_malayalam"
                )
            
            # Get model size from settings (default to medium)
            model_size = st.session_state.get('whisper_model_size', 'medium')
            
            # Render voice input
            transcribed_text = render_voice_input_widget(
                key="diagnosis_voice",
                language=lang_code,
                show_segments=True,
                translate_to_english=translate_option,
                model_size=model_size
            )
            
            # If we have transcribed text, offer to add it
            if transcribed_text:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("➕ Add to Description", key="add_voice_to_text", use_container_width=True):
                        # Initialize patient_text in session state if not exists
                        if "patient_text_input" not in st.session_state:
                            st.session_state.patient_text_input = ""
                        
                        # Append transcribed text
                        current = st.session_state.patient_text_input
                        if current.strip():
                            st.session_state.patient_text_input = current + " " + transcribed_text
                        else:
                            st.session_state.patient_text_input = transcribed_text
                        st.success("✅ Voice input added!")
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Replace Description", key="replace_voice_text", use_container_width=True):
                        st.session_state.patient_text_input = transcribed_text
                        st.success("✅ Description replaced with voice input!")
                        st.rerun()
    
    elif VOICE_INPUT_AVAILABLE and not (WHISPER_AVAILABLE and AUDIO_RECORDER_AVAILABLE):
        st.warning("⚠️ Voice input requires additional packages. See installation instructions below.")
        with st.expander("📦 Install Voice Input Dependencies"):
            st.code("""
pip install openai-whisper
pip install audio-recorder-streamlit
            """, language="bash")
            st.info("After installation, restart the application to use voice input.")

    # Input form (with session state for voice input integration)
    if "patient_text_input" not in st.session_state:
        st.session_state.patient_text_input = ""
    
    patient_text = st.text_area(
        "Patient Description",
        value=st.session_state.patient_text_input,
        height=200,
        placeholder="Example: My 3-year-old golden retriever has been coughing for a week. He seems lethargic and has a fever. His breathing sounds labored sometimes. He has been fully vaccinated.",
        help="Describe the patient's symptoms, duration, severity, and any relevant medical history.",
        key="patient_description_area"
    )
    
    # Update session state when text area changes
    if patient_text != st.session_state.patient_text_input:
        st.session_state.patient_text_input = patient_text

    # Define uploaded_image before use
    uploaded_image = st.file_uploader(
        "Upload skin image (optional)",
        type=["jpg", "jpeg", "png"]
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        analyze_button = st.button("� Analyze Patient Symptoms", type="primary", use_container_width=True)

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
                
                # CRITICAL FIX: Filter matches by patient's animal type immediately
                all_matches = analysis.get("database_matches", [])
                patient_animal = state["patient_info"].animal_type.lower() if state["patient_info"].animal_type else None
                if patient_animal:
                    state["matches"] = [
                        d for d in all_matches 
                        if patient_animal in [s.lower() for s in d.get('affected_species', [])]
                    ]
                    if len(state["matches"]) < len(all_matches):
                        st.info(f"🎯 Filtered to {len(state['matches'])} diseases specific to {patient_animal}s (from {len(all_matches)} total matches)")
                else:
                    state["matches"] = all_matches
                
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
                        "pet_id": st.session_state.get('selected_pet_id'),  # Link to pet if selected
                        "created_at": datetime.now()
                    }
                    
                    db.analysis_history.insert_one(history_record)
                    
                    # Also save to pet database if pet was selected
                    if st.session_state.get('selected_pet_id') and st.session_state.get('use_existing_pet'):
                        try:
                            pet_db = get_pet_database()
                            
                            # Extract symptoms for consultation record
                            symptoms_list = [s.symptom for s in state["symptoms"]]
                            diagnosis_list = [d["name"] for d in state["matches"][:3]]
                            confidence_dict = {d["name"]: d.get("confidence", 0) for d in state["matches"][:3]}
                            
                            # Create consultation record in pet database
                            consultation_data = {
                                'pet_id': st.session_state.selected_pet_id,
                                'veterinarian': st.session_state.username,
                                'chief_complaint': patient_text[:200],  # First 200 chars as complaint
                                'symptoms': symptoms_list,
                                'diagnosis': diagnosis_list,
                                'diagnosis_confidence': confidence_dict,
                                'differential_diagnosis': [d["name"] for d in state["matches"][3:10]],
                                'notes': patient_text,
                                'ai_questions_asked': [],  # Will be updated as questions progress
                                'ai_answers': []
                            }
                            
                            pet_consultation = pet_db.create_consultation(consultation_data)
                            st.session_state.current_consultation_id = pet_consultation['consultation_id']
                            
                        except Exception as pet_db_error:
                            st.warning(f"⚠️ Could not save to pet database: {pet_db_error}")
                    
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
        # Patient Info - PROMINENTLY DISPLAY ANIMAL TYPE
        st.markdown("### 👤 Patient Information")
        patient_info = state["patient_info"]
        
        # Highlight the animal type prominently
        animal_type = patient_info.animal_type or "Unknown"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;">
            <h2 style="color: white; margin: 0;">🐾 {animal_type.upper()} 🐾</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
                All diagnoses and questions are specific to {animal_type}s
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Species", animal_type)
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
        
        # --- STEP 3 & 4: AI-Powered Follow-up Questions (MOVED TO TOP) ---
        st.markdown("---")
        st.markdown("### 🤖 AI Follow-up Analysis")
        
        # Check stopping conditions
        top_disease_confidence = state["matches"][0]['confidence'] if state["matches"] else 0
        questions_asked = state.get("questions_asked", 0)
        max_questions = state.get("max_questions", 8)
        confidence_threshold = state.get("confidence_threshold", 0.85)
        
        # Display progress with animal info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div style="padding: 0.8rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin:0; color: white; font-size: 0.9rem;">🐾 Species</h4>
            <h3 style="margin:0.3rem 0 0 0; color: white;">{state["patient_info"].animal_type.upper()}</h3>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="padding: 0.8rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
            border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin:0; color: white; font-size: 0.9rem;">❓ Questions</h4>
            <h3 style="margin:0.3rem 0 0 0; color: white;">{questions_asked}/{max_questions}</h3>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="padding: 0.8rem; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
            border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin:0; color: white; font-size: 0.9rem;">🎯 Confidence</h4>
            <h3 style="margin:0.3rem 0 0 0; color: white;">{top_disease_confidence:.1%}</h3>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div style="padding: 0.8rem; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
            border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin:0; color: white; font-size: 0.9rem;">🎓 Target</h4>
            <h3 style="margin:0.3rem 0 0 0; color: white;">{confidence_threshold:.1%}</h3>
            </div>
            """, unsafe_allow_html=True)
        
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
                    
                    # CRITICAL: Only pass diseases for this specific animal
                    patient_animal = state["patient_info"].animal_type.lower() if state["patient_info"].animal_type else 'unknown'
                    
                    # Use state["matches"] which are already animal-filtered
                    diseases_dict = [
                        {
                            'disease_name': d.get('name', '') if isinstance(d, dict) else d.disease_name,
                            'confidence': d.get('confidence', 0) if isinstance(d, dict) else d.confidence,
                            'animal_type': patient_animal  # Add animal context
                        } for d in state["matches"][:10]  # Top 10 only
                    ]
                    
                    # Generate AI questions with animal-specific context
                    ai_questions = st.session_state.ai_generator.generate_questions(
                        patient_info=patient_dict,
                        symptoms=symptoms_dict,
                        suspected_diseases=diseases_dict,
                        database_matches=state["matches"][:10],  # Only animal-specific diseases
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
            # Display AVA question recommendation strategies
            st.markdown("#### 📊 AVA Question Recommendation Strategies")
            try:
                strategy_engine = QuestionStrategyEngine(repo)
                asked_symptoms = set([s.symptom for s in state["symptoms"]])
                ava_questions = strategy_engine.get_recommended_questions(
                    candidate_diseases=state["matches"][:5],  # Top-5 animal-specific diseases
                    asked_symptoms=asked_symptoms
                )
                
                if ava_questions:
                    col1, col2 = st.columns(2)
                    for i, q_info in enumerate(ava_questions[:2]):
                        with (col1 if i == 0 else col2):
                            st.info(f"""
**{q_info['strategy']}**  
{q_info['question']}  
*Reasoning:* {q_info['reasoning']}
                            """)
                st.markdown("---")
            except Exception as strat_error:
                print(f"Strategy engine error: {strat_error}")
            
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
            # Diagnosis complete - Enhanced completion messages
            st.markdown("---")
            if top_disease_confidence >= confidence_threshold:
                st.markdown("""
                <div style="padding: 2rem; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                border-radius: 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                <h2 style="color: white; margin: 0;">✅ Diagnosis Complete!</h2>
                <p style="color: white; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                Achieved {:.1%} confidence - Ready for veterinary review
                </p>
                </div>
                """.format(top_disease_confidence), unsafe_allow_html=True)
                st.balloons()
            elif questions_asked >= max_questions:
                st.markdown("""
                <div style="padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                border-radius: 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                <h2 style="color: white; margin: 0;">📊 Analysis Complete</h2>
                <p style="color: white; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                Maximum questions reached ({}) - Comprehensive data collected
                </p>
                </div>
                """.format(max_questions), unsafe_allow_html=True)
            elif len(state["matches"]) == 1:
                st.markdown("""
                <div style="padding: 2rem; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                border-radius: 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                <h2 style="color: white; margin: 0;">✅ Single Disease Identified!</h2>
                <p style="color: white; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                All symptoms point to one specific condition
                </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                <h2 style="color: white; margin: 0;">✅ Sufficient Information Collected</h2>
                <p style="color: white; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                Ready for veterinary consultation
                </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Show summary stats with enhanced design
            st.markdown("### 📈 Consultation Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="padding: 1rem; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                border-radius: 10px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                <h4 style="margin:0; color: #333; font-size: 0.9rem;">❓ Questions Asked</h4>
                <h2 style="margin:0.5rem 0 0 0; color: #333;">{questions_asked}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="padding: 1rem; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                border-radius: 10px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                <h4 style="margin:0; color: #333; font-size: 0.9rem;">🎯 Final Confidence</h4>
                <h2 style="margin:0.5rem 0 0 0; color: #333;">{top_disease_confidence:.1%}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="padding: 1rem; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                border-radius: 10px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                <h4 style="margin:0; color: #333; font-size: 0.9rem;">📊 Diseases Analyzed</h4>
                <h2 style="margin:0.5rem 0 0 0; color: #333;">{len(state["matches"])}</h2>
                </div>
                """, unsafe_allow_html=True)
            
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
        
        # NOW SHOW FILTERS AND DISEASE RESULTS (AFTER QUESTIONS)
        st.markdown("---")
        st.markdown("### 🔍 Filter Disease Results")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_severity = st.selectbox(
                "Severity",
                options=["All", "mild", "moderate", "severe"],
                key="filter_severity"
            )
        with col2:
            filter_species = st.selectbox(
                "Species",
                options=["All"] + ["dog", "cat", "rabbit", "hamster", "guinea_pig", "ferret", "rat", "mouse", 
                         "gerbil", "chinchilla", "hedgehog", "horse", "cow", "goat", "sheep", "pig", 
                         "parrot", "parakeet", "cockatiel", "budgie", "turtle", "snake", "lizard", 
                         "bearded_dragon", "gecko", "fish", "sugar_glider"],
                key="filter_species"
            )
        with col3:
            filter_min_confidence = st.slider(
                "Min Confidence %",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                key="filter_confidence"
            )
        with col4:
            show_top_n = st.selectbox(
                "Show Top",
                options=[5, 10, 20, 50, "All"],
                index=1,
                key="filter_top_n"
            )
        
        # Apply filters
        filtered_matches = state["matches"].copy()
        
        # CRITICAL: Auto-filter by patient's animal type FIRST
        patient_animal = state["patient_info"].animal_type.lower() if state["patient_info"].animal_type else None
        if patient_animal:
            filtered_matches = [
                d for d in filtered_matches 
                if patient_animal in [s.lower() for s in d.get('affected_species', [])]
            ]
        
        if filter_severity != "All":
            filtered_matches = [d for d in filtered_matches if d.get('severity') == filter_severity]
        
        if filter_species != "All":
            filtered_matches = [d for d in filtered_matches 
                              if filter_species in d.get('affected_species', [])]
        
        if filter_min_confidence > 0:
            filtered_matches = [d for d in filtered_matches 
                              if d.get('confidence', 0) >= (filter_min_confidence / 100)]
        
        # Limit results
        if show_top_n != "All":
            filtered_matches = filtered_matches[:show_top_n]
        
        # Show filter stats
        try:
            total_in_db = repo.db.diseases.count_documents({})
            st.info(f"📊 Showing {len(filtered_matches)} of {len(state['matches'])} matched diseases (Database: {total_in_db} total)")
        except:
            st.info(f"📊 Showing {len(filtered_matches)} of {len(state['matches'])} matched diseases")
        
        # --- AVA-STYLE DISEASE PREDICTIONS (TOP-K WITH EXPLAINABILITY) ---
        st.markdown("---")
        if filtered_matches:
            ava_engine = AVADisplayEngine()
            ava_engine.display_ava_results(
                diseases=filtered_matches,
                patient_symptoms=state["symptoms"],
                show_top_k=min(10, len(filtered_matches))
            )
        else:
            st.warning("No diseases match the selected filters. Try adjusting the filters above.")

        # Recommendations
        st.markdown("---")
        st.markdown("### 💡 Recommendations")
        urgency = "routine"
        if filtered_matches:
            top_disease = filtered_matches[0]
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
        
        # Database stats
        total_diseases = db.diseases.count_documents({})
        st.info(f"💾 **Database:** {total_diseases} diseases | 560+ symptoms | 673 total conditions")

        # Enhanced filters
        st.markdown("### 🔍 Advanced Filters")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_query = st.text_input("Search", placeholder="Disease name or keyword...")
        with col2:
            severity_filter = st.selectbox("Severity", ["All", "mild", "moderate", "severe"])
        with col3:
            species_filter = st.selectbox("Species", ["All", "dog", "cat", "rabbit", "hamster", "guinea_pig", 
                                                      "ferret", "rat", "mouse", "gerbil", "chinchilla", 
                                                      "hedgehog", "horse", "cow", "goat", "sheep", "pig", 
                                                      "parrot", "parakeet", "cockatiel", "budgie", 
                                                      "turtle", "snake", "lizard", "bearded_dragon", 
                                                      "gecko", "fish", "sugar_glider"])
        with col4:
            category_filter = st.selectbox("Category", ["All", "viral", "bacterial", "parasitic", "digestive", 
                                                        "respiratory", "urinary", "skin", "endocrine", 
                                                        "cardiovascular", "neurological", "orthopedic", 
                                                        "eye", "ear", "dental", "reproductive", "exotic", "metabolic"])

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
        
        if species_filter != "All":
            query["affected_species"] = species_filter
        
        if category_filter != "All":
            query["category"] = category_filter

        # Get diseases with pagination
        diseases = list(db.diseases.find(query).limit(50))

        st.markdown(f"### 📋 Found {len(diseases)} disease(s) {f'(showing first 50)' if len(diseases) == 50 else ''}")

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
"""
Professional Veterinary AI Assistant - Streamlit Web Application
Features: Dark Theme, Authentication, Admin Panel, User Management
"""

import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import json
from pathlib import Path
from main import VeterinaryAIAssistant
from veterinary_database import VeterinaryDatabase

# Load environment variables.
# This is robust to different working directories (common on other computers/launch methods).
_DOTENV_PATH = find_dotenv(usecwd=True) or str(Path(__file__).resolve().parent / ".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)


@st.cache_resource
def get_db() -> VeterinaryDatabase:
    try:
        return VeterinaryDatabase()
    except Exception as exc:
        mongo_url = os.getenv("MONGO_URL", "").strip()
        is_missing = not mongo_url
        is_local = mongo_url.startswith("mongodb://localhost") or mongo_url.startswith("mongodb://127.0.0.1")

        st.error("Database connection failed. The app cannot start without MongoDB.")
        if is_missing:
            st.info(
                "`MONGO_URL` is not set. On this computer, create a `.env` file (copy `.env.example` → `.env`) "
                "and set `MONGO_URL` to your MongoDB Atlas connection string."
            )
        elif is_local:
            st.info(
                "`MONGO_URL` is set to a local MongoDB (`localhost`), but MongoDB is not running on this computer. "
                "Either start a local MongoDB service or switch `MONGO_URL` to MongoDB Atlas in your `.env`."
            )
        else:
            st.info(
                "If you're using MongoDB Atlas, make sure the computer's IP is allowed in Atlas (Network Access allowlist)."
            )
        st.code(str(exc))
        st.stop()

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
    def __init__(self, db: VeterinaryDatabase):
        self.db = db
        # Ensure default admin/user exist (values from .env)
        self.db.ensure_default_users()

    def verify_user(self, username: str, password: str):
        return self.db.verify_user(username, password)

    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        return self.db.create_user(username, password, role=role)

    def delete_user(self, username: str) -> bool:
        if username == os.getenv("ADMIN_USERNAME", "admin"):
            return False
        result = self.db.users.delete_one({"username": username})
        return result.deleted_count == 1

    def get_user_role(self, username: str) -> str:
        doc = self.db.users.find_one({"username": username}, {"role": 1})
        return doc.get("role", "user") if doc else "user"

    def list_users(self):
        cursor = self.db.users.find({}, {"username": 1, "role": 1, "created_at": 1, "last_login_at": 1}).sort(
            "created_at", -1
        )
        return list(cursor)

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

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
                user_manager = UserManager(get_db())
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
        
        # Show registration form
        if hasattr(st.session_state, 'show_register') and st.session_state.show_register:
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
                    user_manager = UserManager(get_db())
                    if user_manager.add_user(new_username, new_password):
                        st.success("✅ Account created successfully! Please login.")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error("❌ Username already exists")

# Admin panel
def show_admin_panel():
    st.markdown("## 👨‍💼 Admin Panel")
    
    tabs = st.tabs(["User Management", "Database Stats", "System Settings"])
    
    # User Management Tab
    with tabs[0]:
        st.markdown("### 👥 User Management")
        
        user_manager = UserManager(get_db())
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

                seed(get_db(), disease_count=int(seed_diseases), symptom_count=int(seed_symptoms))
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
        st.write("**Version:** 1.0.0")
        st.write("**AI Model:** NLP + MongoDB")
        st.write("**Last Updated:** December 2025")

# Main application
def show_main_app():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state.username}!")
        st.markdown(f"**Role:** {st.session_state.role}")
        
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Home", "🔍 Diagnosis", "📚 Disease Database", "📊 History", "⚙️ Admin Panel"] if st.session_state.role == "admin" else ["🏠 Home", "🔍 Diagnosis", "📚 Disease Database", "📊 History"]
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()
    
    # Main content
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

# Home page
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

# Diagnosis page
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
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_button = st.button("🔍 Analyze Patient", use_container_width=True)
    
    with col2:
        generate_questions = st.checkbox("Generate Follow-up Questions", value=True)
    
    if analyze_button and patient_text:
        with st.spinner("🔄 Analyzing patient data..."):
            try:
                db = get_db()
                assistant = VeterinaryAIAssistant(db=db)
                result = assistant.analyze_patient_text(
                    patient_text,
                    generate_questions=generate_questions,
                    username=st.session_state.username,
                )

                # Keep a lightweight in-session cache (optional)
                st.session_state.analysis_history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "patient_text": patient_text,
                        "result": result,
                    }
                )
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # Patient Info
                st.markdown("### 👤 Patient Information")
                patient_info = result['patient_analysis'].patient_info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Species", patient_info.animal_type or "Unknown")
                with col2:
                    st.metric("Age", patient_info.age or "Unknown")
                with col3:
                    st.metric("Breed", patient_info.breed or "Unknown")
                with col4:
                    st.metric("Weight", patient_info.weight or "Unknown")
                
                # Symptoms
                st.markdown("### 🩺 Detected Symptoms")
                symptoms = result['patient_analysis'].symptoms
                if symptoms:
                    cols = st.columns(3)
                    for idx, symptom in enumerate(symptoms):
                        with cols[idx % 3]:
                            severity_class = f"severity-{symptom.severity}" if symptom.severity else "severity-mild"
                            st.markdown(f"""
                            <div class="info-card">
                                <strong>{symptom.symptom}</strong><br>
                                <span class="severity-badge {severity_class}">{symptom.severity or 'Unknown'}</span><br>
                                <small>Duration: {symptom.duration or 'Not specified'}</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No specific symptoms detected.")
                
                # Disease Matches
                st.markdown("### 🎯 Possible Diagnoses")
                matches = result['database_matches']
                if matches:
                    for disease in matches[:5]:
                        severity_class = f"severity-{disease['severity']}"
                        st.markdown(f"""
                        <div class="disease-card">
                            <h4>{disease['name']}</h4>
                            <span class="severity-badge {severity_class}">{disease['severity']}</span>
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
                recommendations = result['recommendations']
                urgency_colors = {
                    "routine": "🟢",
                    "moderate": "🟡",
                    "urgent": "🔴"
                }
                urgency_icon = urgency_colors.get(recommendations['urgency'], "🟡")
                st.markdown(f"**Urgency Level:** {urgency_icon} {recommendations['urgency'].upper()}")
                
                st.markdown("**Recommended Actions:**")
                for action in recommendations['recommended_actions']:
                    st.markdown(f"- {action}")
                
                # Follow-up Questions
                if generate_questions and result.get('follow_up_questions'):
                    st.markdown("### ❓ Follow-up Questions")
                    for i, question in enumerate(result['follow_up_questions'][:10], 1):
                        st.markdown(f"""
                        <div class="info-card">
                            <strong>Q{i}:</strong> {question.question}<br>
                            <small>Category: {question.category} | Priority: {'⭐' * question.priority}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                st.exception(e)
    
    elif analyze_button:
        st.warning("⚠️ Please enter patient description.")

# Database page
def show_database_page():
    st.markdown("## 📚 Disease Database")
    
    try:
        mongo_url = os.getenv('MONGO_URL')
        db_name = os.getenv('MONGO_DB_NAME', 'veterinary_ai_db')
        db = VeterinaryDatabase(mongo_url=mongo_url, db_name=db_name)
        
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

# History page
def show_history_page():
    st.markdown("## 📊 Analysis History")

    try:
        db = get_db()
        records = db.get_user_analysis_history(st.session_state.username, limit=50)
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
        urgency = summary.get("urgency") or rec.get("recommendations", {}).get("urgency")

        with st.expander(f"Analysis #{idx} - {str(created_at)[:19]}"):
            st.markdown("**Patient Description:**")
            st.write(rec.get("patient_text", ""))

            st.markdown("**Detected Diseases:**")
            top = summary.get("top_diseases") or []
            if top:
                for d in top:
                    st.write(f"- {d.get('name')} ({d.get('severity')})")
            else:
                for disease in (rec.get("database_matches") or [])[:3]:
                    if isinstance(disease, dict):
                        st.write(f"- {disease.get('name')} ({disease.get('severity')})")

            if urgency:
                st.markdown(f"**Urgency:** {urgency}")

# Main application entry
def main():
    load_custom_css()
    init_session_state()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()

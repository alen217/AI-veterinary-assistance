"""
Environment Configuration Example
Use this to configure MongoDB connection from environment variables
"""

import os
from dotenv import load_dotenv
from main import VeterinaryAIAssistant

# Load environment variables from .env file
load_dotenv()

# Get MongoDB configuration from .env file
# Default is MongoDB Atlas - update your .env file with your connection string
mongo_url = os.getenv("MONGO_URL", "mongodb+srv://user:pass@cluster.mongodb.net/veterinary_ai_db")
mongo_db_name = os.getenv("MONGO_DB_NAME", "veterinary_ai_db")

print(f"Connecting to MongoDB...")
print(f"URL: {mongo_url}")
print(f"Database: {mongo_db_name}\n")

# Create assistant with environment configuration
with VeterinaryAIAssistant(mongo_url=mongo_url, db_name=mongo_db_name) as assistant:
    # Example usage
    patient_text = """
    My 5-year-old dog has been vomiting for 2 days and seems lethargic.
    He won't eat and has diarrhea.
    """
    
    print("Analyzing patient...")
    result = assistant.analyze_patient_text(patient_text)
    print(assistant.generate_report(result))

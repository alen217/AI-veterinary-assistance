from pymongo import MongoClient
from datetime import datetime
import os
import bcrypt

from dotenv import load_dotenv, find_dotenv


# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("MONGO_DB_NAME", "veterinary_ai_db")


class UserDatabase:
    def __init__(self):
        if not MONGO_URL:
            raise RuntimeError("MONGO_URL not set in .env")

        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]

        print(f"✅ Connected to MongoDB: {self.db.name}")

        self.users = self.db.users
        self.analysis_history = self.db.analysis_history

        self._ensure_indexes()
        self._ensure_default_admin()

    # --------------------------------------------------
    # SETUP
    # --------------------------------------------------
    def _ensure_indexes(self):
        self.users.create_index("username", unique=True)
        self.analysis_history.create_index("username")

    def _hash_password(self, password: str) -> bytes:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

    def _ensure_default_admin(self):
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_username or not admin_password:
            return

        if self.users.find_one({"username": admin_username}):
            return

        self.users.insert_one({
            "username": admin_username,
            "password_hash": self._hash_password(admin_password),
            "role": "admin",
            "created_at": datetime.utcnow()
        })

        print("✅ Default admin user created")

    # --------------------------------------------------
    # AUTH
    # --------------------------------------------------
    def verify_user(self, username: str, password: str):
        user = self.users.find_one({"username": username})
        if not user:
            return None

        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"]
        ):
            return user

        return None

    def create_user(self, username: str, password: str, role="user") -> bool:
        try:
            self.users.insert_one({
                "username": username,
                "password_hash": self._hash_password(password),
                "role": role,
                "created_at": datetime.utcnow()
            })
            return True
        except Exception:
            return False

    # --------------------------------------------------
    # HISTORY
    # --------------------------------------------------
    def save_analysis(self, username: str, record: dict):
        record["username"] = username
        record["created_at"] = datetime.utcnow()
        self.analysis_history.insert_one(record)

    def get_user_history(self, username: str, limit=50):
        return list(
            self.analysis_history
            .find({"username": username})
            .sort("created_at", -1)
            .limit(limit)
        )

    from pymongo import MongoClient
import os

_client = None
_db = None

def get_db():
    global _client, _db

    if _db is None:
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB_NAME", "veterinary_ai_db")

        _client = MongoClient(mongo_url)
        _db = _client[db_name]

    return _db

"""
Disease, User, and Treatment Database (SQLite)
Used by Veterinary AI Assistant
"""

import json
import os
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# =========================
# Data Models
# =========================

@dataclass
class Disease:
    id: int
    name: str
    scientific_name: str
    description: str
    common_symptoms: List[str]
    causes: List[str]
    treatment: str
    prevention: str
    severity: str
    affected_species: List[str]


@dataclass
class TreatmentOption:
    id: int
    disease_id: int
    name: str
    description: str
    medication: str
    dosage: str
    duration: str
    effectiveness: float


# =========================
# Database Class
# =========================

class VeterinaryDatabase:
    def __init__(self, db_path: str = "veterinary_ai.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_database()
        self.ensure_default_users()

    # -------------------------
    # Initialization
    # -------------------------

    def _initialize_database(self):
        cursor = self.conn.cursor()

        # Diseases
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            scientific_name TEXT,
            description TEXT,
            common_symptoms TEXT,
            causes TEXT,
            treatment TEXT,
            prevention TEXT,
            severity TEXT,
            affected_species TEXT
        )
        """)

        # Symptoms
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER,
            symptom TEXT
        )
        """)

        # Treatments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER,
            name TEXT,
            description TEXT,
            medication TEXT,
            dosage TEXT,
            duration TEXT,
            effectiveness REAL
        )
        """)

        # Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            created_at TEXT,
            last_login_at TEXT
        )
        """)

        # Analysis History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            patient_text TEXT,
            summary TEXT,
            created_at TEXT
        )
        """)

        self.conn.commit()
        self._populate_default_diseases()

    # -------------------------
    # Security
    # -------------------------

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # -------------------------
    # User Management
    # -------------------------

    def ensure_default_users(self):
        cursor = self.conn.cursor()

        admin_user = os.getenv("ADMIN_USERNAME", "admin")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")

        cursor.execute("SELECT 1 FROM users WHERE username=?", (admin_user,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, ?, ?)
            """, (
                admin_user,
                self._hash_password(admin_pass),
                "admin",
                datetime.utcnow().isoformat()
            ))
            self.conn.commit()

    def verify_user(self, username: str, password: str):
        cursor = self.conn.cursor()
        hashed = self._hash_password(password)

        cursor.execute("""
        SELECT username, role FROM users
        WHERE username=? AND password=?
        """, (username, hashed))

        user = cursor.fetchone()
        if user:
            cursor.execute("""
            UPDATE users SET last_login_at=?
            WHERE username=?
            """, (datetime.utcnow().isoformat(), username))
            self.conn.commit()
            return dict(user)

        return None

    def create_user(self, username: str, password: str, role="user") -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, ?, ?)
            """, (
                username,
                self._hash_password(password),
                role,
                datetime.utcnow().isoformat()
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    # -------------------------
    # Analysis History
    # -------------------------

    def save_analysis(self, username: str, patient_text: str, summary: Dict):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO analysis_history (username, patient_text, summary, created_at)
        VALUES (?, ?, ?, ?)
        """, (
            username,
            patient_text,
            json.dumps(summary),
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()

    def get_user_analysis_history(self, username: str, limit=50):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM analysis_history
        WHERE username=?
        ORDER BY created_at DESC
        LIMIT ?
        """, (username, limit))
        return [dict(row) for row in cursor.fetchall()]

    # -------------------------
    # Disease Logic (Preserved)
    # -------------------------

    def _populate_default_diseases(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM diseases")
        if cursor.fetchone()[0] > 0:
            return

        diseases = [
            ("Gastroenteritis", "Gastritis", "GI inflammation",
             ["vomiting", "diarrhea"], ["infection"], "Fluids", "Clean diet", "moderate", ["dog", "cat"]),
            ("Parvovirus", "CPV", "Severe viral disease",
             ["vomiting", "fever"], ["virus"], "IV care", "Vaccination", "severe", ["dog"])
        ]

        for d in diseases:
            cursor.execute("""
            INSERT INTO diseases
            (name, scientific_name, description, common_symptoms, causes,
             treatment, prevention, severity, affected_species)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d[0], d[1], d[2],
                json.dumps(d[3]), json.dumps(d[4]),
                d[5], d[6], d[7], json.dumps(d[8])
            ))

        self.conn.commit()

    # -------------------------
    # Cleanup
    # -------------------------

    def close(self):
        self.conn.close()

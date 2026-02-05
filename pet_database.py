"""
Pet Database Management System
Handles pet patient records, medical history, and consultation tracking
"""

import pymongo
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class PetDatabaseManager:
    """Manages pet patient records and medical history"""
    
    def __init__(self):
        """Initialize connection to MongoDB"""
        try:
            # MongoDB connection using same pattern as disease repository
            mongo_url = os.getenv("MONGO_URL")
            if not mongo_url:
                raise RuntimeError("MONGO_URL not set in environment")
            
            self.client = pymongo.MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            self.db = self.client[os.getenv("MONGO_DB_NAME", "veterinary_ai_db")]
            
            # Collections
            self.pets_collection = self.db['pets']
            self.owners_collection = self.db['owners']
            self.consultations_collection = self.db['consultations']
            
            # Test connection
            self.client.server_info()
            
            # Create indexes for performance
            self._create_indexes()
            
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Pet indexes
            self.pets_collection.create_index([("pet_id", pymongo.ASCENDING)], unique=True)
            self.pets_collection.create_index([("owner_id", pymongo.ASCENDING)])
            self.pets_collection.create_index([("species", pymongo.ASCENDING)])
            self.pets_collection.create_index([("name", pymongo.TEXT)])
            
            # Owner indexes
            self.owners_collection.create_index([("owner_id", pymongo.ASCENDING)], unique=True)
            self.owners_collection.create_index([("email", pymongo.ASCENDING)])
            self.owners_collection.create_index([("phone", pymongo.ASCENDING)])
            
            # Consultation indexes
            self.consultations_collection.create_index([("consultation_id", pymongo.ASCENDING)], unique=True)
            self.consultations_collection.create_index([("pet_id", pymongo.ASCENDING)])
            self.consultations_collection.create_index([("date", pymongo.DESCENDING)])
            self.consultations_collection.create_index([("veterinarian", pymongo.ASCENDING)])
            
        except Exception as e:
            print(f"Index creation warning: {e}")
    
    # ====================== PET MANAGEMENT ======================
    
    def create_pet(self, pet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new pet record
        
        Args:
            pet_data: Dictionary containing:
                - name: Pet name (required)
                - species: Dog, Cat, Bird, etc. (required)
                - breed: Specific breed
                - age: Age in years/months
                - age_unit: 'years' or 'months'
                - sex: Male/Female
                - weight: Weight in kg
                - color: Coat color
                - microchip_id: Microchip number
                - owner_id: Owner's ID (required)
                - medical_conditions: List of chronic conditions
                - allergies: List of known allergies
                - current_medications: List of current meds
                - vaccination_records: List of vaccinations
                - notes: Additional notes
        
        Returns:
            Created pet document with pet_id
        """
        try:
            # Generate unique pet ID
            import uuid
            pet_id = f"PET{str(uuid.uuid4())[:8].upper()}"
            
            # Required fields validation
            if not pet_data.get('name') or not pet_data.get('species') or not pet_data.get('owner_id'):
                raise ValueError("Name, species, and owner_id are required")
            
            # Build pet document
            pet_document = {
                'pet_id': pet_id,
                'name': pet_data['name'].strip().title(),
                'species': pet_data['species'].strip().lower(),
                'breed': pet_data.get('breed', 'Mixed/Unknown').strip(),
                'age': pet_data.get('age', 0),
                'age_unit': pet_data.get('age_unit', 'years'),
                'sex': pet_data.get('sex', 'Unknown'),
                'weight': pet_data.get('weight', 0.0),
                'color': pet_data.get('color', ''),
                'microchip_id': pet_data.get('microchip_id', ''),
                'owner_id': pet_data['owner_id'],
                
                # Medical information
                'medical_conditions': pet_data.get('medical_conditions', []),
                'allergies': pet_data.get('allergies', []),
                'current_medications': pet_data.get('current_medications', []),
                'vaccination_records': pet_data.get('vaccination_records', []),
                
                # Additional info
                'notes': pet_data.get('notes', ''),
                'photo_url': pet_data.get('photo_url', ''),
                
                # Metadata
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'last_visit': None,
                'total_visits': 0,
                'status': 'active'  # active, inactive, deceased
            }
            
            # Insert into database
            self.pets_collection.insert_one(pet_document)
            
            return pet_document
            
        except Exception as e:
            raise Exception(f"Error creating pet record: {e}")
    
    def get_pet(self, pet_id: str) -> Optional[Dict[str, Any]]:
        """Get pet by ID"""
        try:
            pet = self.pets_collection.find_one({'pet_id': pet_id})
            if pet:
                pet.pop('_id', None)  # Remove MongoDB ID
            return pet
        except Exception as e:
            print(f"Error fetching pet: {e}")
            return None
    
    def get_pets_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """Get all pets for a specific owner"""
        try:
            pets = list(self.pets_collection.find({'owner_id': owner_id}))
            for pet in pets:
                pet.pop('_id', None)
            return pets
        except Exception as e:
            print(f"Error fetching owner's pets: {e}")
            return []
    
    def search_pets(self, query: str, species: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search pets by name or other criteria
        
        Args:
            query: Search term (name, breed, microchip)
            species: Optional species filter
            limit: Max results
        
        Returns:
            List of matching pets
        """
        try:
            search_filter = {}
            
            # Text search or regex
            if query:
                search_filter['$or'] = [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'breed': {'$regex': query, '$options': 'i'}},
                    {'microchip_id': {'$regex': query, '$options': 'i'}}
                ]
            
            # Species filter
            if species:
                search_filter['species'] = species.lower()
            
            pets = list(self.pets_collection.find(search_filter).limit(limit))
            for pet in pets:
                pet.pop('_id', None)
            
            return pets
            
        except Exception as e:
            print(f"Error searching pets: {e}")
            return []
    
    def update_pet(self, pet_id: str, updates: Dict[str, Any]) -> bool:
        """Update pet information"""
        try:
            updates['last_updated'] = datetime.now().isoformat()
            
            result = self.pets_collection.update_one(
                {'pet_id': pet_id},
                {'$set': updates}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating pet: {e}")
            return False
    
    def delete_pet(self, pet_id: str) -> bool:
        """Soft delete pet (mark as inactive)"""
        try:
            result = self.pets_collection.update_one(
                {'pet_id': pet_id},
                {'$set': {'status': 'inactive', 'last_updated': datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting pet: {e}")
            return False
    
    # ====================== OWNER MANAGEMENT ======================
    
    def create_owner(self, owner_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new pet owner/client record
        
        Args:
            owner_data: Dictionary containing:
                - name: Owner name (required)
                - email: Email address
                - phone: Phone number (required)
                - address: Full address
                - city: City
                - state: State/Province
                - postal_code: ZIP/Postal code
                - emergency_contact: Emergency contact info
                - notes: Additional notes
        
        Returns:
            Created owner document with owner_id
        """
        try:
            import uuid
            owner_id = f"OWN{str(uuid.uuid4())[:8].upper()}"
            
            if not owner_data.get('name') or not owner_data.get('phone'):
                raise ValueError("Name and phone are required")
            
            owner_document = {
                'owner_id': owner_id,
                'name': owner_data['name'].strip().title(),
                'email': owner_data.get('email', '').strip().lower(),
                'phone': owner_data['phone'].strip(),
                'address': owner_data.get('address', ''),
                'city': owner_data.get('city', ''),
                'state': owner_data.get('state', ''),
                'postal_code': owner_data.get('postal_code', ''),
                'emergency_contact': owner_data.get('emergency_contact', ''),
                'notes': owner_data.get('notes', ''),
                
                # Metadata
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_pets': 0,
                'total_visits': 0,
                'status': 'active'
            }
            
            self.owners_collection.insert_one(owner_document)
            return owner_document
            
        except Exception as e:
            raise Exception(f"Error creating owner record: {e}")
    
    def get_owner(self, owner_id: str) -> Optional[Dict[str, Any]]:
        """Get owner by ID"""
        try:
            owner = self.owners_collection.find_one({'owner_id': owner_id})
            if owner:
                owner.pop('_id', None)
            return owner
        except Exception as e:
            print(f"Error fetching owner: {e}")
            return None
    
    def search_owners(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search owners by name, email, or phone"""
        try:
            search_filter = {
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'email': {'$regex': query, '$options': 'i'}},
                    {'phone': {'$regex': query, '$options': 'i'}}
                ]
            }
            
            owners = list(self.owners_collection.find(search_filter).limit(limit))
            for owner in owners:
                owner.pop('_id', None)
            
            return owners
            
        except Exception as e:
            print(f"Error searching owners: {e}")
            return []
    
    def update_owner(self, owner_id: str, updates: Dict[str, Any]) -> bool:
        """Update owner information"""
        try:
            updates['last_updated'] = datetime.now().isoformat()
            
            result = self.owners_collection.update_one(
                {'owner_id': owner_id},
                {'$set': updates}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating owner: {e}")
            return False
    
    # ====================== CONSULTATION MANAGEMENT ======================
    
    def create_consultation(self, consultation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new consultation record
        
        Args:
            consultation_data: Dictionary containing:
                - pet_id: Pet ID (required)
                - veterinarian: Vet name/username (required)
                - chief_complaint: Main reason for visit
                - symptoms: List of symptoms
                - diagnosis: List of diagnosed conditions
                - diagnosis_confidence: Confidence scores
                - treatment_plan: Treatment recommendations
                - prescriptions: Medications prescribed
                - follow_up_date: Next appointment date
                - notes: Consultation notes
                - vital_signs: Temperature, heart rate, etc.
        
        Returns:
            Created consultation document
        """
        try:
            import uuid
            consultation_id = f"CON{str(uuid.uuid4())[:8].upper()}"
            
            if not consultation_data.get('pet_id') or not consultation_data.get('veterinarian'):
                raise ValueError("Pet ID and veterinarian are required")
            
            # Get pet info
            pet = self.get_pet(consultation_data['pet_id'])
            if not pet:
                raise ValueError(f"Pet not found: {consultation_data['pet_id']}")
            
            consultation_document = {
                'consultation_id': consultation_id,
                'pet_id': consultation_data['pet_id'],
                'pet_name': pet.get('name', 'Unknown'),
                'species': pet.get('species', 'unknown'),
                'owner_id': pet.get('owner_id', ''),
                'veterinarian': consultation_data['veterinarian'],
                
                # Consultation details
                'date': datetime.now().isoformat(),
                'chief_complaint': consultation_data.get('chief_complaint', ''),
                'symptoms': consultation_data.get('symptoms', []),
                'vital_signs': consultation_data.get('vital_signs', {}),
                
                # Diagnosis
                'diagnosis': consultation_data.get('diagnosis', []),
                'diagnosis_confidence': consultation_data.get('diagnosis_confidence', {}),
                'differential_diagnosis': consultation_data.get('differential_diagnosis', []),
                
                # Treatment
                'treatment_plan': consultation_data.get('treatment_plan', ''),
                'prescriptions': consultation_data.get('prescriptions', []),
                'lab_tests_ordered': consultation_data.get('lab_tests_ordered', []),
                
                # Follow-up
                'follow_up_date': consultation_data.get('follow_up_date', ''),
                'follow_up_instructions': consultation_data.get('follow_up_instructions', ''),
                
                # Additional
                'notes': consultation_data.get('notes', ''),
                'ai_questions_asked': consultation_data.get('ai_questions_asked', []),
                'ai_answers': consultation_data.get('ai_answers', []),
                'images': consultation_data.get('images', []),
                
                # Metadata
                'status': 'completed',  # scheduled, in-progress, completed, cancelled
                'duration_minutes': consultation_data.get('duration_minutes', 0),
                'cost': consultation_data.get('cost', 0.0)
            }
            
            # Insert consultation
            self.consultations_collection.insert_one(consultation_document)
            
            # Update pet's last visit
            self.pets_collection.update_one(
                {'pet_id': consultation_data['pet_id']},
                {
                    '$set': {'last_visit': datetime.now().isoformat()},
                    '$inc': {'total_visits': 1}
                }
            )
            
            # Update owner's total visits
            self.owners_collection.update_one(
                {'owner_id': pet.get('owner_id')},
                {'$inc': {'total_visits': 1}}
            )
            
            return consultation_document
            
        except Exception as e:
            raise Exception(f"Error creating consultation: {e}")
    
    def get_consultation(self, consultation_id: str) -> Optional[Dict[str, Any]]:
        """Get consultation by ID"""
        try:
            consultation = self.consultations_collection.find_one({'consultation_id': consultation_id})
            if consultation:
                consultation.pop('_id', None)
            return consultation
        except Exception as e:
            print(f"Error fetching consultation: {e}")
            return None
    
    def get_pet_history(self, pet_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all consultations for a pet (medical history)"""
        try:
            consultations = list(
                self.consultations_collection.find({'pet_id': pet_id})
                .sort('date', pymongo.DESCENDING)
                .limit(limit)
            )
            
            for consultation in consultations:
                consultation.pop('_id', None)
            
            return consultations
            
        except Exception as e:
            print(f"Error fetching pet history: {e}")
            return []
    
    def get_vet_consultations(self, veterinarian: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all consultations by a specific veterinarian"""
        try:
            consultations = list(
                self.consultations_collection.find({'veterinarian': veterinarian})
                .sort('date', pymongo.DESCENDING)
                .limit(limit)
            )
            
            for consultation in consultations:
                consultation.pop('_id', None)
            
            return consultations
            
        except Exception as e:
            print(f"Error fetching vet consultations: {e}")
            return []
    
    def update_consultation(self, consultation_id: str, updates: Dict[str, Any]) -> bool:
        """Update consultation record"""
        try:
            result = self.consultations_collection.update_one(
                {'consultation_id': consultation_id},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating consultation: {e}")
            return False
    
    # ====================== AI CONTEXT RETRIEVAL ======================
    
    def get_pet_context_for_ai(self, pet_id: str) -> Dict[str, Any]:
        """
        Get comprehensive pet information for AI diagnosis
        Includes medical history, chronic conditions, allergies, etc.
        
        Returns:
            Dictionary with pet info and medical history for AI context
        """
        try:
            # Get pet info
            pet = self.get_pet(pet_id)
            if not pet:
                return {}
            
            # Get consultation history
            history = self.get_pet_history(pet_id, limit=10)
            
            # Extract relevant information
            context = {
                'pet_id': pet_id,
                'name': pet.get('name', 'Unknown'),
                'species': pet.get('species', 'unknown'),
                'breed': pet.get('breed', 'Mixed'),
                'age': pet.get('age', 0),
                'age_unit': pet.get('age_unit', 'years'),
                'sex': pet.get('sex', 'Unknown'),
                'weight': pet.get('weight', 0.0),
                
                # Medical background
                'chronic_conditions': pet.get('medical_conditions', []),
                'allergies': pet.get('allergies', []),
                'current_medications': pet.get('current_medications', []),
                'vaccination_status': pet.get('vaccination_records', []),
                
                # Past diagnoses (from history)
                'previous_diagnoses': [],
                'recurring_symptoms': [],
                'last_visit_date': pet.get('last_visit', None),
                'total_visits': pet.get('total_visits', 0)
            }
            
            # Extract diagnoses and symptoms from history
            all_diagnoses = []
            all_symptoms = []
            
            for consultation in history:
                if consultation.get('diagnosis'):
                    all_diagnoses.extend(consultation['diagnosis'])
                if consultation.get('symptoms'):
                    all_symptoms.extend(consultation['symptoms'])
            
            # Find most common diagnoses (recurring issues)
            from collections import Counter
            if all_diagnoses:
                diagnosis_counts = Counter(all_diagnoses)
                context['previous_diagnoses'] = [
                    {'disease': d, 'occurrences': count}
                    for d, count in diagnosis_counts.most_common(5)
                ]
            
            # Find recurring symptoms
            if all_symptoms:
                symptom_counts = Counter(all_symptoms)
                context['recurring_symptoms'] = [
                    {'symptom': s, 'occurrences': count}
                    for s, count in symptom_counts.most_common(5)
                ]
            
            return context
            
        except Exception as e:
            print(f"Error getting pet context for AI: {e}")
            return {}
    
    # ====================== STATISTICS & REPORTS ======================
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {
                'total_pets': self.pets_collection.count_documents({'status': 'active'}),
                'total_owners': self.owners_collection.count_documents({'status': 'active'}),
                'total_consultations': self.consultations_collection.count_documents({}),
                'pets_by_species': {},
                'consultations_this_month': 0,
                'most_common_diagnoses': []
            }
            
            # Count by species
            species_counts = self.pets_collection.aggregate([
                {'$match': {'status': 'active'}},
                {'$group': {'_id': '$species', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ])
            
            for item in species_counts:
                stats['pets_by_species'][item['_id']] = item['count']
            
            # Consultations this month
            from datetime import timedelta
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            stats['consultations_this_month'] = self.consultations_collection.count_documents({
                'date': {'$gte': month_ago}
            })
            
            return stats
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        try:
            self.client.close()
        except:
            pass


# Singleton instance
_pet_db_instance = None

def get_pet_database() -> PetDatabaseManager:
    """Get or create pet database manager instance"""
    global _pet_db_instance
    if _pet_db_instance is None:
        _pet_db_instance = PetDatabaseManager()
    return _pet_db_instance


if __name__ == "__main__":
    # Test the pet database
    print("🐾 Testing Pet Database System...")
    
    try:
        db = get_pet_database()
        
        # Test owner creation
        print("\n1. Creating test owner...")
        owner = db.create_owner({
            'name': 'John Smith',
            'email': 'john@example.com',
            'phone': '+1-555-0123',
            'address': '123 Main St',
            'city': 'New York',
            'state': 'NY'
        })
        print(f"✓ Owner created: {owner['owner_id']} - {owner['name']}")
        
        # Test pet creation
        print("\n2. Creating test pet...")
        pet = db.create_pet({
            'name': 'Buddy',
            'species': 'dog',
            'breed': 'Golden Retriever',
            'age': 3,
            'sex': 'Male',
            'weight': 30.5,
            'owner_id': owner['owner_id'],
            'medical_conditions': ['Hip dysplasia'],
            'allergies': ['Chicken'],
            'current_medications': ['Carprofen 75mg daily']
        })
        print(f"✓ Pet created: {pet['pet_id']} - {pet['name']}")
        
        # Test consultation creation
        print("\n3. Creating test consultation...")
        consultation = db.create_consultation({
            'pet_id': pet['pet_id'],
            'veterinarian': 'Dr. Smith',
            'chief_complaint': 'Limping on right front leg',
            'symptoms': ['limping', 'pain on palpation', 'reduced activity'],
            'diagnosis': ['Osteoarthritis'],
            'diagnosis_confidence': {'Osteoarthritis': 85.5},
            'treatment_plan': 'Pain management with NSAIDs, weight management, physiotherapy',
            'prescriptions': ['Carprofen 75mg twice daily', 'Glucosamine supplement']
        })
        print(f"✓ Consultation created: {consultation['consultation_id']}")
        
        # Test AI context retrieval
        print("\n4. Getting AI context...")
        context = db.get_pet_context_for_ai(pet['pet_id'])
        print(f"✓ AI Context retrieved:")
        print(f"  - Pet: {context['name']} ({context['species']})")
        print(f"  - Age: {context['age']} {context['age_unit']}")
        print(f"  - Chronic conditions: {context['chronic_conditions']}")
        print(f"  - Allergies: {context['allergies']}")
        print(f"  - Current meds: {context['current_medications']}")
        
        # Test search
        print("\n5. Testing search...")
        search_results = db.search_pets("Buddy")
        print(f"✓ Found {len(search_results)} pet(s) matching 'Buddy'")
        
        # Get statistics
        print("\n6. Database statistics...")
        stats = db.get_database_stats()
        print(f"✓ Total pets: {stats['total_pets']}")
        print(f"✓ Total owners: {stats['total_owners']}")
        print(f"✓ Total consultations: {stats['total_consultations']}")
        print(f"✓ Pets by species: {stats['pets_by_species']}")
        
        print("\n✅ All tests passed! Pet database is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

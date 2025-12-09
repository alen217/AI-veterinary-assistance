"""
MongoDB Setup and Verification Script
Helps verify MongoDB installation and setup for the Veterinary AI Assistant
"""

import sys


def check_pymongo():
    """Check if PyMongo is installed"""
    print("Checking PyMongo installation...")
    try:
        import pymongo
        print(f"✓ PyMongo version {pymongo.__version__} is installed")
        return True
    except ImportError:
        print("✗ PyMongo is not installed")
        print("  Install with: pip install pymongo")
        return False


def check_mongodb_connection(mongo_url="mongodb://localhost:27017/"):
    """Check if MongoDB is accessible"""
    print(f"\nChecking MongoDB connection at {mongo_url}...")
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        info = client.server_info()
        print(f"✓ Connected to MongoDB version {info['version']}")
        client.close()
        return True
    except Exception as e:
        print(f"✗ Cannot connect to MongoDB: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure MongoDB is installed")
        print("  2. Start MongoDB service:")
        print("     Windows: net start MongoDB")
        print("     Mac/Linux: sudo systemctl start mongod")
        print("  3. Check if MongoDB is running on port 27017")
        return False


def test_database_setup():
    """Test database initialization"""
    print("\nTesting database setup...")
    try:
        from veterinary_database import VeterinaryDatabase
        
        db = VeterinaryDatabase()
        diseases = db.get_all_diseases()
        
        print(f"✓ Database initialized successfully")
        print(f"  Found {len(diseases)} diseases in database")
        
        if len(diseases) > 0:
            print(f"  Sample disease: {diseases[0].name}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False


def test_basic_operations():
    """Test basic database operations"""
    print("\nTesting basic operations...")
    try:
        from veterinary_database import VeterinaryDatabase
        
        db = VeterinaryDatabase()
        
        # Test symptom search
        results = db.search_by_symptoms(['vomiting', 'diarrhea'])
        print(f"✓ Symptom search: Found {len(results)} matching diseases")
        
        # Test name search
        disease = db.search_by_name("Gastroenteritis")
        if disease:
            print(f"✓ Name search: Found '{disease.name}'")
        else:
            print("⚠ Name search: Disease not found (database may be empty)")
        
        # Test keyword search
        results = db.search_by_keyword("infection")
        print(f"✓ Keyword search: Found {len(results)} diseases")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Basic operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_connection_info():
    """Display connection information"""
    print("\n" + "="*80)
    print("MongoDB Connection Information")
    print("="*80)
    print("\nDefault Connection:")
    print("  URL: mongodb://localhost:27017/")
    print("  Database: veterinary_ai_db")
    print("  Collections: diseases, treatments")
    print("\nCustom Connection:")
    print("  from veterinary_database import VeterinaryDatabase")
    print('  db = VeterinaryDatabase(')
    print('      mongo_url="mongodb://your-url",')
    print('      db_name="your-database"')
    print('  )')
    print("\nMongoDB Atlas (Cloud):")
    print('  mongo_url = "mongodb+srv://user:pass@cluster.mongodb.net/"')


def show_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*80)
    print("Next Steps")
    print("="*80)
    print("\n1. Run examples:")
    print("   python mongodb_examples.py")
    print("\n2. Run tests:")
    print("   python test_suite.py")
    print("\n3. Use the system:")
    print("   python main.py")
    print("\n4. Read documentation:")
    print("   - MONGODB_MIGRATION_GUIDE.md")
    print("   - MONGODB_QUICK_REFERENCE.md")
    print("\n5. Migrate existing SQLite data (if applicable):")
    print("   python migrate_sqlite_to_mongodb.py")


def run_all_checks():
    """Run all verification checks"""
    print("\n" + "#"*80)
    print("VETERINARY AI - MongoDB Setup Verification".center(80))
    print("#"*80 + "\n")
    
    checks = []
    
    # Check 1: PyMongo
    checks.append(("PyMongo Installation", check_pymongo()))
    
    if not checks[-1][1]:
        print("\n⚠ Cannot proceed without PyMongo")
        print("Install with: pip install pymongo")
        return False
    
    # Check 2: MongoDB Connection
    checks.append(("MongoDB Connection", check_mongodb_connection()))
    
    if not checks[-1][1]:
        print("\n⚠ Cannot proceed without MongoDB connection")
        return False
    
    # Check 3: Database Setup
    checks.append(("Database Setup", test_database_setup()))
    
    # Check 4: Basic Operations
    checks.append(("Basic Operations", test_basic_operations()))
    
    # Summary
    print("\n" + "="*80)
    print("Verification Summary")
    print("="*80)
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name:.<50} {status}")
    
    all_passed = all(result for _, result in checks)
    
    print("="*80)
    
    if all_passed:
        print("\n✓ All checks passed! System is ready to use.")
        show_connection_info()
        show_next_steps()
    else:
        print("\n⚠ Some checks failed. Please review the errors above.")
        print("\nFor help, see:")
        print("  - MONGODB_MIGRATION_GUIDE.md (troubleshooting section)")
        print("  - MONGODB_QUICK_REFERENCE.md")
    
    print("\n" + "#"*80 + "\n")
    
    return all_passed


def quick_test():
    """Quick connection test only"""
    print("\n" + "="*80)
    print("Quick MongoDB Connection Test")
    print("="*80 + "\n")
    
    if check_pymongo():
        if check_mongodb_connection():
            print("\n✓ MongoDB is ready!")
            return True
    
    print("\n✗ Setup incomplete")
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test only
        success = quick_test()
    else:
        # Full verification
        success = run_all_checks()
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python
"""Check if SQLAdmin is working correctly"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect
from database import DATABASE_URL, Base

def check_admin_setup():
    """Verify SQLAdmin setup"""
    issues = []
    
    # Check static directory
    static_dir = Path(__file__).parent / "static"
    if not static_dir.exists():
        issues.append("❌ Static directory missing - creating it...")
        static_dir.mkdir(exist_ok=True)
        print("✅ Created static directory")
    else:
        print("✅ Static directory exists")
    
    # Check database connection
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        issues.append(f"❌ Database connection failed: {e}")
    
    # Check if tables exist
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"✅ Found {len(tables)} tables in database")
        else:
            issues.append("⚠️ No tables found - run migrations")
    except Exception as e:
        issues.append(f"❌ Could not inspect database: {e}")
    
    # Summary
    if issues:
        print("\n⚠️ Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ All checks passed! SQLAdmin should work correctly.")
        print("🚀 Access admin at: http://localhost:8000/admin")
        return True

if __name__ == "__main__":
    success = check_admin_setup()
    sys.exit(0 if success else 1)

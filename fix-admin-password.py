#!/usr/bin/env python3
"""
Script to fix the admin user password_hash issue
"""
import os
import sys
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from routes.auth import get_password_hash

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pm_user:QlILLYN4kmmkuDzNwGrEsBQ4M@pm_postgres_db:5432/pm_database")

def fix_admin_password():
    """Fix the admin user password_hash"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            # Check if admin user exists and has password_hash
            result = conn.execute(text("""
                SELECT id, username, password_hash 
                FROM users 
                WHERE username = 'admin'
            """))
            user = result.fetchone()
            
            if not user:
                print("❌ Admin user not found")
                return False
            
            if user.password_hash is None:
                print("🔧 Fixing admin user password_hash...")
                
                # Generate password hash
                hashed_password = get_password_hash("admin123")
                
                # Update the user
                conn.execute(text("""
                    UPDATE users 
                    SET password_hash = :password_hash 
                    WHERE username = 'admin'
                """), {"password_hash": hashed_password})
                
                conn.commit()
                print("✅ Admin user password_hash updated successfully")
                print(f"   Username: admin")
                print(f"   Password: admin123")
                return True
            else:
                print("✅ Admin user already has password_hash")
                return True
                
    except Exception as e:
        print(f"❌ Error fixing admin password: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing admin user password_hash...")
    success = fix_admin_password()
    if success:
        print("🎉 Admin user fix completed successfully!")
    else:
        print("💥 Admin user fix failed!")
        sys.exit(1) 
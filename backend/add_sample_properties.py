#!/usr/bin/env python3
"""
Script to add sample properties to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db, engine
from models.models import Property
from datetime import datetime

def add_sample_properties():
    """Add sample properties to the database"""
    db = next(get_db())
    
    try:
        # Check if properties already exist
        existing_properties = db.query(Property).all()
        if existing_properties:
            print(f"Found {len(existing_properties)} existing properties:")
            for prop in existing_properties:
                print(f"  ID {prop.id}: {prop.name}")
            return
        
        # Add sample properties
        properties = [
            Property(
                name="Lubd Chainatown",
                address="Chainatown, Bangkok, Thailand",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Property(
                name="Lubd Siam",
                address="Siam, Bangkok, Thailand", 
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for property_obj in properties:
            db.add(property_obj)
        
        db.commit()
        
        print("✅ Sample properties added successfully!")
        print("Properties created:")
        for prop in properties:
            print(f"  ID {prop.id}: {prop.name}")
            
    except Exception as e:
        print(f"❌ Error adding properties: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding sample properties to database...")
    add_sample_properties() 
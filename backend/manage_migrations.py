#!/usr/bin/env python3
"""
Database Migration Management Script for PM System
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    print("🔍 Checking database connection...")
    
    # Try to connect to database
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_initial_migration():
    """Create initial migration from current models"""
    if not check_database_connection():
        return False
    
    return run_command(
        "alembic revision --autogenerate -m 'Initial migration'",
        "Creating initial migration"
    )

def create_migration(message):
    """Create a new migration"""
    if not check_database_connection():
        return False
    
    return run_command(
        f"alembic revision --autogenerate -m '{message}'",
        f"Creating migration: {message}"
    )

def upgrade_database(revision="head"):
    """Upgrade database to specified revision"""
    if not check_database_connection():
        return False
    
    return run_command(
        f"alembic upgrade {revision}",
        f"Upgrading database to {revision}"
    )

def downgrade_database(revision):
    """Downgrade database to specified revision"""
    if not check_database_connection():
        return False
    
    return run_command(
        f"alembic downgrade {revision}",
        f"Downgrading database to {revision}"
    )

def show_migration_history():
    """Show migration history"""
    return run_command(
        "alembic history",
        "Showing migration history"
    )

def show_current_revision():
    """Show current database revision"""
    return run_command(
        "alembic current",
        "Showing current revision"
    )

def show_pending_migrations():
    """Show pending migrations"""
    return run_command(
        "alembic show head",
        "Showing pending migrations"
    )

def reset_database():
    """Reset database (drop all tables and recreate)"""
    print("⚠️  WARNING: This will delete all data!")
    confirm = input("Are you sure you want to reset the database? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Database reset cancelled")
        return False
    
    # Drop all tables
    try:
        from database import engine
        from models.models import Base
        
        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
        
        # Create all tables
        print("🏗️  Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created")
        
        # Run initial migration
        print("📝 Creating initial migration...")
        Base.metadata.create_all(bind=engine)
        run_command(
            "alembic stamp head",
            "Stamping current revision"
        )
        
        return True
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("""
🔧 PM System Database Migration Manager

Usage:
  python manage_migrations.py <command> [options]

Commands:
  init              - Create initial migration
  create <message>  - Create new migration with message
  upgrade [rev]     - Upgrade to revision (default: head)
  downgrade <rev>   - Downgrade to revision
  history           - Show migration history
  current           - Show current revision
  pending           - Show pending migrations
  reset             - Reset database (WARNING: deletes all data)

Examples:
  python manage_migrations.py init
  python manage_migrations.py create "Add user table"
  python manage_migrations.py upgrade
  python manage_migrations.py downgrade -1
  python manage_migrations.py history
        """)
        return

    command = sys.argv[1].lower()
    
    if command == "init":
        create_initial_migration()
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Please provide a migration message")
            return
        message = sys.argv[2]
        create_migration(message)
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade_database(revision)
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("❌ Please provide a revision to downgrade to")
            return
        revision = sys.argv[2]
        downgrade_database(revision)
    elif command == "history":
        show_migration_history()
    elif command == "current":
        show_current_revision()
    elif command == "pending":
        show_pending_migrations()
    elif command == "reset":
        reset_database()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 
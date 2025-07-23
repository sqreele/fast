"""
Database initialization script for PM System
Works with both SQLite and PostgreSQL
"""
import os
import time
from sqlalchemy import create_engine, text
from database import engine, Base
from models.models import *
from admin import AdminManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_database(max_retries=30, retry_interval=2):
    """Wait for database to be ready"""
    logger.info("Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            # Test database connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database is ready!")
            return True
        except Exception as e:
            logger.warning(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
    
    logger.error("Database failed to become ready")
    return False

def init_database():
    """Initialize database with tables and initial data"""
    try:
        # Wait for database to be ready
        if not wait_for_database():
            return False
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # Initialize admin data
        logger.info("Initializing admin data...")
        admin = AdminManager()
        
        # Create admin user
        admin_user = admin.create_admin_user(
            username="admin",
            email="admin@pmsystem.com",
            first_name="System",
            last_name="Administrator"
        )
        logger.info(f"Admin user created: {admin_user.username}")
        
        # Create default topics
        topics = admin.create_default_topics()
        logger.info(f"Created {len(topics)} default topics")
        
        # Create sample procedures
        procedures = admin.create_sample_procedures()
        logger.info(f"Created {len(procedures)} sample procedures")
        
        # Show system stats
        stats = admin.get_system_stats()
        logger.info("=== System Statistics ===")
        logger.info(f"Users: {stats['users']['total']} total, {stats['users']['active']} active")
        logger.info(f"Properties: {stats['properties']['total']} total")
        logger.info(f"Machines: {stats['machines']['total']} total")
        logger.info(f"PM Schedules: {stats['pm_schedules']['total']} total, {stats['pm_schedules']['overdue']} overdue")
        logger.info(f"Issues: {stats['issues']['total']} total, {stats['issues']['open']} open, {stats['issues']['critical']} critical")
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database() 
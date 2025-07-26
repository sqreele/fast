from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use PostgreSQL in production (Docker) or SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pm_system.db")

logger.info(f"Using database URL: {DATABASE_URL}")

if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration with connection retry settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
        connect_args={
            "connect_timeout": 10,
            "application_name": "pm_system"
        }
    )
else:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables_with_retry(max_retries=5, base_delay=2):
    """Create database tables with retry logic"""
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting to create database tables (attempt {attempt}/{max_retries})")
            
            # Import models to ensure they're registered with Base
            from models import models
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed to create tables: {e}")
            
            if attempt < max_retries:
                delay = base_delay ** attempt
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to create tables after {max_retries} attempts")
                raise e
    
    return False

def setup_admin():
    """Setup SQLAlchemy Admin interface"""
    try:
        # Import admin setup here to avoid circular imports
        from admin import admin_views
        from sqladmin import Admin
        
        # This will be set up when the FastAPI app is ready
        logger.info("Admin views configuration ready")
        return True
    except Exception as e:
        logger.error(f"Failed to setup admin interface: {e}")
        return False

def init_database():
    """Initialize database with all components"""
    logger.info("Starting database initialization...")
    
    # Create tables with retry logic
    success = create_tables_with_retry()
    
    if success:
        # Setup admin interface
        setup_admin()
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")
        raise Exception("Database initialization failed")
    
    return success

# Legacy function for backwards compatibility
def create_tables():
    """Legacy function - use init_database instead"""
    return create_tables_with_retry() 
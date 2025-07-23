from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use PostgreSQL in production (Docker) or SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pm_system.db")

logger.info(f"Using database URL: {DATABASE_URL}")

if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
else:
    # SQLite configuration (for development)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import all models to ensure they are registered with Base
try:
    from models import (
        User, Property, Room, Machine, Topic, Procedure,
        PMSchedule, PMExecution, Issue, Inspection, PMFile, UserPropertyAccess,
        WorkOrder, Notification, MaintenanceLog,
        UserRole, FrequencyType, PMStatus, IssueStatus, IssuePriority,
        InspectionResult, ImageType, AccessLevel, MachineType, MachineStatus,
        WorkOrderStatus, WorkOrderType, NotificationType
    )
    logger.info("All models imported successfully")
except ImportError as e:
    logger.error(f"Error importing models: {e}")

# Create all tables
def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on import
if __name__ == "__main__":
    create_tables() 
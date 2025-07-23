from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from database import get_db
import subprocess
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def require_admin_role(db: Session = Depends(get_db)):
    """Dependency to check if user has admin role"""
    # This is a simplified check - in production you'd use proper authentication
    logger.info("Migration endpoint accessed")
    return True

@router.get("/status")
def get_migration_status(db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Get current migration status"""
    try:
        # Get current revision
        result = subprocess.run(
            ["alembic", "current"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        current_revision = result.stdout.strip()
        
        # Get head revision
        result = subprocess.run(
            ["alembic", "heads"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        head_revision = result.stdout.strip()
        
        # Check if up to date
        is_up_to_date = current_revision == head_revision
        
        return {
            "current_revision": current_revision,
            "head_revision": head_revision,
            "is_up_to_date": is_up_to_date,
            "needs_migration": not is_up_to_date
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting migration status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get migration status")

@router.get("/history")
def get_migration_history(db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Get migration history"""
    try:
        result = subprocess.run(
            ["alembic", "history", "--verbose"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        return {
            "history": result.stdout,
            "raw_output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting migration history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get migration history")

@router.post("/upgrade")
def upgrade_database(
    revision: str = "head",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db), 
    _: bool = Depends(require_admin_role)
):
    """Upgrade database to specified revision"""
    try:
        logger.info(f"Starting database upgrade to revision: {revision}")
        
        result = subprocess.run(
            ["alembic", "upgrade", revision], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"Database upgrade completed successfully")
        
        return {
            "message": f"Database upgraded to {revision}",
            "revision": revision,
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error upgrading database: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upgrade database: {e.stderr}"
        )

@router.post("/downgrade")
def downgrade_database(
    revision: str,
    db: Session = Depends(get_db), 
    _: bool = Depends(require_admin_role)
):
    """Downgrade database to specified revision"""
    try:
        logger.info(f"Starting database downgrade to revision: {revision}")
        
        result = subprocess.run(
            ["alembic", "downgrade", revision], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"Database downgrade completed successfully")
        
        return {
            "message": f"Database downgraded to {revision}",
            "revision": revision,
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downgrading database: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to downgrade database: {e.stderr}"
        )

@router.post("/create")
def create_migration(
    message: str,
    db: Session = Depends(get_db), 
    _: bool = Depends(require_admin_role)
):
    """Create a new migration"""
    try:
        logger.info(f"Creating new migration: {message}")
        
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"Migration created successfully")
        
        return {
            "message": f"Migration created: {message}",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating migration: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create migration: {e.stderr}"
        )

@router.post("/stamp")
def stamp_database(
    revision: str = "head",
    db: Session = Depends(get_db), 
    _: bool = Depends(require_admin_role)
):
    """Stamp database with current revision (without running migrations)"""
    try:
        logger.info(f"Stamping database with revision: {revision}")
        
        result = subprocess.run(
            ["alembic", "stamp", revision], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"Database stamped successfully")
        
        return {
            "message": f"Database stamped with {revision}",
            "revision": revision,
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stamping database: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to stamp database: {e.stderr}"
        ) 
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from database import get_db
from models.models import User, UserRole
from admin_manager import AdminManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def require_admin_role(db: Session = Depends(get_db)):
    """Dependency to check if user has admin role"""
    # This is a simplified check - in production you'd use proper authentication
    # For now, we'll allow all requests but log them
    logger.info("Admin endpoint accessed")
    return True

@router.get("/stats", response_model=Dict[str, Any])
def get_system_statistics(db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Get system statistics"""
    try:
        admin = AdminManager()
        stats = admin.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")

@router.post("/setup")
def run_initial_setup(db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Run initial system setup"""
    try:
        admin = AdminManager()
        
        # Create admin user
        admin_user = admin.create_admin_user(
            username="admin",
            email="admin@pmsystem.com",
            first_name="System",
            last_name="Administrator"
        )
        
        # Create default topics
        topics = admin.create_default_topics()
        
        # Create sample procedures
        procedures = admin.create_sample_procedures()
        
        return {
            "message": "Initial setup completed successfully",
            "admin_user": admin_user.username,
            "topics_created": len(topics),
            "procedures_created": len(procedures)
        }
    except Exception as e:
        logger.error(f"Error in initial setup: {e}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

@router.post("/cleanup/files")
def cleanup_old_files(days_old: int = 90, db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Clean up old file records"""
    try:
        admin = AdminManager()
        cleaned_count = admin.cleanup_old_files(days_old)
        return {
            "message": f"Cleaned up {cleaned_count} old file records",
            "files_cleaned": cleaned_count,
            "days_old": days_old
        }
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup files")

@router.post("/users/deactivate-inactive")
def deactivate_inactive_users(days_inactive: int = 365, db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Deactivate users who haven't been active for specified days"""
    try:
        admin = AdminManager()
        deactivated_count = admin.deactivate_inactive_users(days_inactive)
        return {
            "message": f"Deactivated {deactivated_count} inactive users",
            "users_deactivated": deactivated_count,
            "days_inactive": days_inactive
        }
    except Exception as e:
        logger.error(f"Error deactivating users: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate users")

@router.get("/users/by-role", response_model=Dict[str, int])
def get_users_by_role(db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Get user count by role"""
    try:
        role_counts = {}
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            role_counts[role.value] = count
        return role_counts
    except Exception as e:
        logger.error(f"Error getting users by role: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users by role")

@router.get("/health")
def system_health_check(db: Session = Depends(get_db)):
    """System health check"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Get basic stats
        admin = AdminManager()
        stats = admin.get_system_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": admin.db.query("SELECT CURRENT_TIMESTAMP").scalar(),
            "summary": {
                "users": stats["users"]["total"],
                "properties": stats["properties"]["total"],
                "machines": stats["machines"]["total"],
                "overdue_pm": stats["pm_schedules"]["overdue"],
                "open_issues": stats["issues"]["open"]
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"System unhealthy: {str(e)}"
        )

@router.post("/reset-database", status_code=status.HTTP_200_OK)
def reset_database(db: Session = Depends(get_db), _: bool = Depends(require_admin_role)):
    """Reset database - DANGEROUS! Use with extreme caution"""
    try:
        admin = AdminManager()
        success = admin.reset_database()
        
        if success:
            return {"message": "Database reset completed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Database reset failed")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}")

@router.get("/")
def admin_root(_: bool = Depends(require_admin_role)):
    """Root admin endpoint - provides available admin operations"""
    return {
        "message": "PM System Admin API",
        "version": "1.0.0",
        "available_endpoints": [
            "/stats - System statistics",
            "/setup - Initial system setup", 
            "/users - User management",
            "/test - System tests",
            "/backup - Database backup",
            "/reset - Database reset"
        ]
    } 
"""
Simple authentication utilities for PM System API
"""
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import User

def get_current_user(
    db: Session = Depends(get_db),
    # For now, we'll use a simple approach - in production, implement proper JWT auth
    user_id: int = 1  # Default to admin user ID 1
) -> User:
    """
    Get current user - simplified version for development
    In production, implement proper JWT token authentication
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Create a default admin user if none exists
        from admin import AdminManager
        admin = AdminManager()
        user = admin.create_admin_user(
            username="admin",
            email="admin@pmsystem.com",
            first_name="System",
            last_name="Administrator"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user 
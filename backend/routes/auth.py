"""
Authentication routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from database import get_db
from models.models import User, UserRole, UserPropertyAccess, AccessLevel
from schemas import UserCreate, User as UserSchema, MessageResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    token: str
    name: str  # For NextAuth compatibility

@router.post("/register", response_model=UserSchema)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=user_data.is_active,
        password_hash=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Assign properties if provided
        if hasattr(user_data, 'property_ids') and user_data.property_ids:
            for property_id in user_data.property_ids:
                access = UserPropertyAccess(
                    user_id=db_user.id,
                    property_id=property_id,
                    access_level=AccessLevel.FULL_ACCESS
                )
                db.add(access)
            db.commit()
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return token"""
    
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Generate token (you can implement JWT token generation here)
    # For now, return user data
    return LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        token="dummy_token",  # Replace with actual JWT token
        name=f"{user.first_name} {user.last_name}"  # For NextAuth compatibility
    )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    db: Session = Depends(get_db)
    # In a real implementation, you would get the user from JWT token
    # For now, we'll return a default user or implement proper auth
):
    """Get current user information"""
    # This is a simplified implementation
    # In production, you would decode the JWT token to get the user ID
    # For now, return the first admin user
    user = db.query(User).filter(User.role == UserRole.ADMIN, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout user"""
    # In a real implementation, you would invalidate the JWT token
    # For now, just return a success message
    return MessageResponse(message="Successfully logged out")
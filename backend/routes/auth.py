"""
Authentication routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from jose import JWTError, jwt
import redis
import os

from database import get_db
from models.models import User, UserRole, UserPropertyAccess, AccessLevel
from schemas import UserCreate, User as UserSchema, MessageResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")  # Use environment variable
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for token authentication
security = HTTPBearer()

# Token blacklist - use Redis if available, fallback to in-memory
try:
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    redis_client.ping()  # Test connection
    USE_REDIS = True
    print("Using Redis for token blacklisting")
except Exception as e:
    print(f"Redis not available, using in-memory blacklist: {e}")
    USE_REDIS = False
    blacklisted_tokens = set()

def blacklist_token(token: str):
    """Add token to blacklist"""
    if USE_REDIS:
        try:
            # Set with expiration equal to token expiration
            redis_client.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, "1")
        except Exception as e:
            print(f"Failed to blacklist token in Redis: {e}")
            # Fallback to in-memory
            blacklisted_tokens.add(token)
    else:
        blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    if USE_REDIS:
        try:
            return redis_client.exists(f"blacklist:{token}") > 0
        except Exception as e:
            print(f"Failed to check Redis blacklist: {e}")
            # Fallback to in-memory
            return token in blacklisted_tokens
    else:
        return token in blacklisted_tokens

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials, db: Session):
    """Verify JWT token and return user"""
    try:
        token = credentials.credentials
        
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    return verify_token(credentials, db)

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

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, description="New password")

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
    
    # Generate JWT access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        token=access_token,
        name=f"{user.first_name} {user.last_name}"  # For NextAuth compatibility
    )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user by blacklisting the token"""
    try:
        token = credentials.credentials
        blacklist_token(token)
        return MessageResponse(message="Successfully logged out")
    except Exception as e:
        print(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout user"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    
    try:
        db.commit()
        return MessageResponse(message="Password changed successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

@router.get("/verify-token", response_model=MessageResponse)
async def verify_token_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Verify if token is valid"""
    return MessageResponse(message=f"Token is valid for user: {current_user.username}")
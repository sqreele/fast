from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import UserRole

class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
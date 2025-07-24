from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from schemas import User, UserCreate, UserUpdate, UserWithProperties, UserPropertyAccess, UserPropertyAccessCreate
from models.models import User as UserModel, UserPropertyAccess as UserPropertyAccessModel
from database import get_db

router = APIRouter()

@router.get("/users/", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).filter(UserModel.is_active == True).all()
    return users

@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False
    db.commit()
    return {"message": "User deleted successfully"}

# Many-to-many relationship endpoints
@router.get("/users/{user_id}/properties", response_model=List[UserPropertyAccess])
def get_user_properties(user_id: int, db: Session = Depends(get_db)):
    """Get all properties a user has access to"""
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.property_access

@router.post("/users/{user_id}/properties", response_model=UserPropertyAccess)
def add_user_property_access(user_id: int, property_access: UserPropertyAccessCreate, db: Session = Depends(get_db)):
    """Add property access for a user"""
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if access already exists
    existing_access = db.query(UserPropertyAccessModel).filter(
        UserPropertyAccessModel.user_id == user_id,
        UserPropertyAccessModel.property_id == property_access.property_id
    ).first()
    
    if existing_access:
        raise HTTPException(status_code=400, detail="User already has access to this property")
    
    db_property_access = UserPropertyAccessModel(**property_access.dict())
    db.add(db_property_access)
    db.commit()
    db.refresh(db_property_access)
    return db_property_access

@router.delete("/users/{user_id}/properties/{property_id}")
def remove_user_property_access(user_id: int, property_id: int, db: Session = Depends(get_db)):
    """Remove property access for a user"""
    property_access = db.query(UserPropertyAccessModel).filter(
        UserPropertyAccessModel.user_id == user_id,
        UserPropertyAccessModel.property_id == property_id
    ).first()
    
    if not property_access:
        raise HTTPException(status_code=404, detail="Property access not found")
    
    db.delete(property_access)
    db.commit()
    return {"message": "Property access removed successfully"}

@router.get("/users/{user_id}/with-properties", response_model=UserWithProperties)
def get_user_with_properties(user_id: int, db: Session = Depends(get_db)):
    """Get user with all their property access details"""
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user 
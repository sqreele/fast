from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from schemas import User, UserCreate, UserUpdate, UserWithProperties, UserPropertyAccess, UserPropertyAccessCreate, UserPropertyAccessProfile
from models.models import User as UserModel, UserPropertyAccess as UserPropertyAccessModel
from database import get_db
from routes.auth import get_current_user

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

# Current user endpoints
@router.get("/users/me", response_model=User)
def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.put("/users/me", response_model=User)
def update_current_user_profile(
    user_update: UserUpdate, 
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Only allow updating certain fields
    allowed_fields = {'first_name', 'last_name', 'phone', 'email'}
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if k in allowed_fields}
    
    # Check if email is being changed and if it's already taken
    if 'email' in update_data and update_data['email'] != current_user.email:
        existing_user = db.query(UserModel).filter(
            UserModel.email == update_data['email'],
            UserModel.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/users/me/properties", response_model=List[UserPropertyAccessProfile])
def get_current_user_properties(current_user: UserModel = Depends(get_current_user)):
    """Get current user's property access"""
    property_access_list = []
    for access in current_user.property_access:
        property_access_list.append(UserPropertyAccessProfile(
            property_id=access.property_id,
            property_name=access.property.name if access.property else "Unknown Property",
            access_level=access.access_level,
            granted_at=access.granted_at,
            expires_at=access.expires_at
        ))
    return property_access_list 
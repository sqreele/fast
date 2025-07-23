from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.user import User, UserCreate, UserUpdate
from models.models import User as UserModel
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
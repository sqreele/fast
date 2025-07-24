"""
Property management routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.models import Property, Room, Machine, User, UserPropertyAccess as UserPropertyAccessModel
from schemas import PropertyCreate, PropertyUpdate, Property as PropertySchema, PropertyWithUsers
from schemas import RoomCreate, RoomUpdate, Room as RoomSchema
from schemas import MachineCreate, MachineUpdate, Machine as MachineSchema
from schemas import MessageResponse, PaginatedResponse, UserPropertyAccess, UserPropertyAccessCreate
from auth import get_current_user

router = APIRouter(prefix="/properties", tags=["properties"])

# Property routes
@router.get("/", response_model=List[PropertySchema])
async def get_properties(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all properties"""
    query = db.query(Property)
    if is_active is not None:
        query = query.filter(Property.is_active == is_active)
    return query.all()

@router.get("/public", response_model=List[PropertySchema])
async def get_public_properties(
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all active properties (public endpoint for registration)"""
    query = db.query(Property)
    if is_active is not None:
        query = query.filter(Property.is_active == is_active)
    return query.all()

@router.get("/{property_id}", response_model=PropertySchema)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj

@router.post("/", response_model=PropertySchema)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new property"""
    property_obj = Property(**property_data.dict())
    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)
    return property_obj

@router.put("/{property_id}", response_model=PropertySchema)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    for field, value in property_data.dict(exclude_unset=True).items():
        setattr(property_obj, field, value)
    
    property_obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(property_obj)
    return property_obj

@router.delete("/{property_id}", response_model=MessageResponse)
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a property (soft delete)"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj.is_active = False
    property_obj.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Property deleted successfully")

# Room routes
@router.get("/{property_id}/rooms", response_model=List[RoomSchema])
async def get_rooms(
    property_id: int,
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all rooms for a property"""
    query = db.query(Room).filter(Room.property_id == property_id)
    if is_active is not None:
        query = query.filter(Room.is_active == is_active)
    return query.all()

@router.get("/{property_id}/rooms/{room_id}", response_model=RoomSchema)
async def get_room(
    property_id: int,
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific room"""
    room = db.query(Room).filter(
        Room.id == room_id,
        Room.property_id == property_id
    ).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/{property_id}/rooms", response_model=RoomSchema)
async def create_room(
    property_id: int,
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new room"""
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    room_data_dict = room_data.dict()
    room_data_dict["property_id"] = property_id
    room = Room(**room_data_dict)
    
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.put("/{property_id}/rooms/{room_id}", response_model=RoomSchema)
async def update_room(
    property_id: int,
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a room"""
    room = db.query(Room).filter(
        Room.id == room_id,
        Room.property_id == property_id
    ).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    for field, value in room_data.dict(exclude_unset=True).items():
        setattr(room, field, value)
    
    room.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(room)
    return room

@router.delete("/{property_id}/rooms/{room_id}", response_model=MessageResponse)
async def delete_room(
    property_id: int,
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a room (soft delete)"""
    room = db.query(Room).filter(
        Room.id == room_id,
        Room.property_id == property_id
    ).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room.is_active = False
    room.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Room deleted successfully")

# Machine routes
@router.get("/{property_id}/rooms/{room_id}/machines", response_model=List[MachineSchema])
async def get_machines(
    property_id: int,
    room_id: int,
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all machines in a room"""
    query = db.query(Machine).filter(
        Machine.room_id == room_id,
        Room.property_id == property_id
    ).join(Room)
    
    if is_active is not None:
        query = query.filter(Machine.is_active == is_active)
    return query.all()

@router.get("/{property_id}/rooms/{room_id}/machines/{machine_id}", response_model=MachineSchema)
async def get_machine(
    property_id: int,
    room_id: int,
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific machine"""
    machine = db.query(Machine).filter(
        Machine.id == machine_id,
        Machine.room_id == room_id,
        Room.property_id == property_id
    ).join(Room).first()
    
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.post("/{property_id}/rooms/{room_id}/machines", response_model=MachineSchema)
async def create_machine(
    property_id: int,
    room_id: int,
    machine_data: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new machine"""
    # Verify room exists and belongs to property
    room = db.query(Room).filter(
        Room.id == room_id,
        Room.property_id == property_id
    ).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    machine_data_dict = machine_data.dict()
    machine_data_dict["room_id"] = room_id
    machine = Machine(**machine_data_dict)
    
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine

@router.put("/{property_id}/rooms/{room_id}/machines/{machine_id}", response_model=MachineSchema)
async def update_machine(
    property_id: int,
    room_id: int,
    machine_id: int,
    machine_data: MachineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a machine"""
    machine = db.query(Machine).filter(
        Machine.id == machine_id,
        Machine.room_id == room_id,
        Room.property_id == property_id
    ).join(Room).first()
    
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    for field, value in machine_data.dict(exclude_unset=True).items():
        setattr(machine, field, value)
    
    machine.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(machine)
    return machine

@router.delete("/{property_id}/rooms/{room_id}/machines/{machine_id}", response_model=MessageResponse)
async def delete_machine(
    property_id: int,
    room_id: int,
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a machine (soft delete)"""
    machine = db.query(Machine).filter(
        Machine.id == machine_id,
        Machine.room_id == room_id,
        Room.property_id == property_id
    ).join(Room).first()
    
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine.is_active = False
    machine.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Machine deleted successfully")

# Many-to-many relationship endpoints for properties
@router.get("/{property_id}/users", response_model=List[UserPropertyAccess])
async def get_property_users(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users who have access to a property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return property_obj.user_access

@router.post("/{property_id}/users", response_model=UserPropertyAccess)
async def add_property_user_access(
    property_id: int,
    user_access: UserPropertyAccessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add user access to a property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check if access already exists
    existing_access = db.query(UserPropertyAccessModel).filter(
        UserPropertyAccessModel.property_id == property_id,
        UserPropertyAccessModel.user_id == user_access.user_id
    ).first()
    
    if existing_access:
        raise HTTPException(status_code=400, detail="User already has access to this property")
    
    user_access_dict = user_access.dict()
    user_access_dict["property_id"] = property_id
    db_user_access = UserPropertyAccessModel(**user_access_dict)
    db.add(db_user_access)
    db.commit()
    db.refresh(db_user_access)
    return db_user_access

@router.delete("/{property_id}/users/{user_id}", response_model=MessageResponse)
async def remove_property_user_access(
    property_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove user access from a property"""
    user_access = db.query(UserPropertyAccessModel).filter(
        UserPropertyAccessModel.property_id == property_id,
        UserPropertyAccessModel.user_id == user_id
    ).first()
    
    if not user_access:
        raise HTTPException(status_code=404, detail="User access not found")
    
    db.delete(user_access)
    db.commit()
    return MessageResponse(message="User access removed successfully")

@router.get("/{property_id}/with-users", response_model=PropertyWithUsers)
async def get_property_with_users(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get property with all user access details"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return property_obj 
"""
Notification management routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.models import Notification, User, NotificationType
from schemas import (
    NotificationCreate, NotificationUpdate, Notification as NotificationSchema,
    MessageResponse, PaginatedResponse
)
from auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationSchema])
async def get_notifications(
    user_id: Optional[int] = Query(None),
    notification_type: Optional[NotificationType] = Query(None),
    is_read: Optional[bool] = Query(None),
    related_entity_type: Optional[str] = Query(None),
    related_entity_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notifications with optional filtering"""
    query = db.query(Notification)
    
    # By default, show notifications for current user
    if user_id is None:
        user_id = current_user.id
    
    query = query.filter(Notification.user_id == user_id)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    if related_entity_type:
        query = query.filter(Notification.related_entity_type == related_entity_type)
    if related_entity_id:
        query = query.filter(Notification.related_entity_id == related_entity_id)
    
    return query.order_by(Notification.created_at.desc()).all()

@router.get("/{notification_id}", response_model=NotificationSchema)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check if user can access this notification
    if notification.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to access this notification")
    
    return notification

@router.post("/", response_model=NotificationSchema)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification"""
    # Verify user exists
    user = db.query(User).filter(User.id == notification_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notification = Notification(**notification_data.dict())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

@router.put("/{notification_id}", response_model=NotificationSchema)
async def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check if user can update this notification
    if notification.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to update this notification")
    
    for field, value in notification_data.dict(exclude_unset=True).items():
        setattr(notification, field, value)
    
    db.commit()
    db.refresh(notification)
    return notification

@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check if user can delete this notification
    if notification.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to delete this notification")
    
    db.delete(notification)
    db.commit()
    
    return MessageResponse(message="Notification deleted successfully")

# Mark as read/unread
@router.put("/{notification_id}/read", response_model=NotificationSchema)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check if user can access this notification
    if notification.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to access this notification")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification

@router.put("/{notification_id}/unread", response_model=NotificationSchema)
async def mark_notification_unread(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as unread"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check if user can access this notification
    if notification.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to access this notification")
    
    notification.is_read = False
    notification.read_at = None
    db.commit()
    db.refresh(notification)
    return notification

# Bulk operations
@router.put("/mark-all-read", response_model=MessageResponse)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for current user"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({
        Notification.is_read: True,
        Notification.read_at: datetime.utcnow()
    })
    db.commit()
    
    return MessageResponse(message="All notifications marked as read")

@router.delete("/clear-read", response_model=MessageResponse)
async def clear_read_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all read notifications for current user"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == True
    ).delete()
    db.commit()
    
    return MessageResponse(message="All read notifications cleared")

# Dashboard routes
@router.get("/dashboard/unread")
async def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unread notifications for current user"""
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).all()
    
    return {
        "unread_count": len(unread_notifications),
        "unread_notifications": unread_notifications
    }

@router.get("/dashboard/recent")
async def get_recent_notifications(
    days: int = Query(7, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent notifications for current user"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    recent_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.created_at >= start_date
    ).order_by(Notification.created_at.desc()).all()
    
    return {
        "recent_count": len(recent_notifications),
        "recent_notifications": recent_notifications,
        "days_back": days
    }

# Statistics routes
@router.get("/stats/summary")
async def get_notification_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for current user"""
    total_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    read_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == True
    ).count()
    
    # Count by type
    notification_types = db.query(Notification.notification_type).filter(
        Notification.user_id == current_user.id
    ).distinct().all()
    
    type_counts = {}
    for notification_type in notification_types:
        count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.notification_type == notification_type[0]
        ).count()
        type_counts[notification_type[0]] = count
    
    return {
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "read_notifications": read_notifications,
        "notification_types": type_counts,
        "read_rate": (read_notifications / total_notifications * 100) if total_notifications > 0 else 0
    } 
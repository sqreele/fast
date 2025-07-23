"""
Work order management routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from database import get_db
from models.models import WorkOrder, Machine, User, WorkOrderStatus, WorkOrderType, IssuePriority
from schemas import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrder as WorkOrderSchema,
    MessageResponse, PaginatedResponse
)
from auth import get_current_user

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

@router.get("/", response_model=List[WorkOrderSchema])
async def get_work_orders(
    machine_id: Optional[int] = Query(None),
    created_by_id: Optional[int] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    work_order_type: Optional[WorkOrderType] = Query(None),
    status: Optional[WorkOrderStatus] = Query(None),
    priority: Optional[IssuePriority] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all work orders with optional filtering"""
    query = db.query(WorkOrder)
    
    if machine_id:
        query = query.filter(WorkOrder.machine_id == machine_id)
    if created_by_id:
        query = query.filter(WorkOrder.created_by_id == created_by_id)
    if assigned_to_id:
        query = query.filter(WorkOrder.assigned_to_id == assigned_to_id)
    if work_order_type:
        query = query.filter(WorkOrder.work_order_type == work_order_type)
    if status:
        query = query.filter(WorkOrder.status == status)
    if priority:
        query = query.filter(WorkOrder.priority == priority)
    if is_active is not None:
        query = query.filter(WorkOrder.is_active == is_active)
    
    return query.order_by(WorkOrder.created_at.desc()).all()

@router.get("/{work_order_id}", response_model=WorkOrderSchema)
async def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific work order"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return work_order

@router.post("/", response_model=WorkOrderSchema)
async def create_work_order(
    work_order_data: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new work order"""
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == work_order_data.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Set creator to current user if not specified
    work_order_data_dict = work_order_data.dict()
    if not work_order_data_dict.get("created_by_id"):
        work_order_data_dict["created_by_id"] = current_user.id
    
    work_order = WorkOrder(**work_order_data_dict)
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order

@router.put("/{work_order_id}", response_model=WorkOrderSchema)
async def update_work_order(
    work_order_id: int,
    work_order_data: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a work order"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    for field, value in work_order_data.dict(exclude_unset=True).items():
        setattr(work_order, field, value)
    
    # If status is completed, set completed_at
    if work_order_data.status == WorkOrderStatus.COMPLETED:
        work_order.completed_at = datetime.utcnow()
    
    # If status is in progress, set started_at
    if work_order_data.status == WorkOrderStatus.IN_PROGRESS and not work_order.started_at:
        work_order.started_at = datetime.utcnow()
    
    work_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(work_order)
    return work_order

@router.delete("/{work_order_id}", response_model=MessageResponse)
async def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a work order (soft delete)"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    work_order.is_active = False
    work_order.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Work order deleted successfully")

# Work order status management
@router.put("/{work_order_id}/assign", response_model=WorkOrderSchema)
async def assign_work_order(
    work_order_id: int,
    assigned_to_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a work order to a user"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    work_order.assigned_to_id = assigned_to_id
    work_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(work_order)
    return work_order

@router.put("/{work_order_id}/status", response_model=WorkOrderSchema)
async def update_work_order_status(
    work_order_id: int,
    status: WorkOrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work order status"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    work_order.status = status
    
    # Set appropriate timestamps based on status
    if status == WorkOrderStatus.COMPLETED:
        work_order.completed_at = datetime.utcnow()
    elif status == WorkOrderStatus.IN_PROGRESS and not work_order.started_at:
        work_order.started_at = datetime.utcnow()
    
    work_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(work_order)
    return work_order

# Dashboard routes
@router.get("/dashboard/pending")
async def get_pending_work_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending work orders"""
    pending_work_orders = db.query(WorkOrder).filter(
        WorkOrder.status.in_([WorkOrderStatus.DRAFT, WorkOrderStatus.APPROVED]),
        WorkOrder.is_active == True
    ).all()
    
    return {
        "pending_count": len(pending_work_orders),
        "pending_work_orders": pending_work_orders
    }

@router.get("/dashboard/in-progress")
async def get_in_progress_work_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get in-progress work orders"""
    in_progress_work_orders = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.IN_PROGRESS,
        WorkOrder.is_active == True
    ).all()
    
    return {
        "in_progress_count": len(in_progress_work_orders),
        "in_progress_work_orders": in_progress_work_orders
    }

@router.get("/dashboard/completed")
async def get_completed_work_orders(
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recently completed work orders"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    completed_work_orders = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.COMPLETED,
        WorkOrder.completed_at >= start_date,
        WorkOrder.is_active == True
    ).all()
    
    return {
        "completed_count": len(completed_work_orders),
        "completed_work_orders": completed_work_orders,
        "days_back": days
    }

# Statistics routes
@router.get("/stats/summary")
async def get_work_order_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get work order statistics"""
    total_work_orders = db.query(WorkOrder).filter(WorkOrder.is_active == True).count()
    pending_work_orders = db.query(WorkOrder).filter(
        WorkOrder.status.in_([WorkOrderStatus.DRAFT, WorkOrderStatus.APPROVED]),
        WorkOrder.is_active == True
    ).count()
    in_progress_work_orders = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.IN_PROGRESS,
        WorkOrder.is_active == True
    ).count()
    completed_work_orders = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.COMPLETED,
        WorkOrder.is_active == True
    ).count()
    
    # Calculate total costs
    total_estimated_cost = db.query(WorkOrder).filter(
        WorkOrder.cost_estimate.isnot(None),
        WorkOrder.is_active == True
    ).with_entities(func.sum(WorkOrder.cost_estimate)).scalar() or 0
    
    total_actual_cost = db.query(WorkOrder).filter(
        WorkOrder.actual_cost.isnot(None),
        WorkOrder.is_active == True
    ).with_entities(func.sum(WorkOrder.actual_cost)).scalar() or 0
    
    return {
        "total_work_orders": total_work_orders,
        "pending_work_orders": pending_work_orders,
        "in_progress_work_orders": in_progress_work_orders,
        "completed_work_orders": completed_work_orders,
        "total_estimated_cost": total_estimated_cost,
        "total_actual_cost": total_actual_cost,
        "completion_rate": (completed_work_orders / total_work_orders * 100) if total_work_orders > 0 else 0
    } 
"""
Maintenance log management routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.models import MaintenanceLog, Machine, User
from schemas import (
    MaintenanceLogCreate, MaintenanceLogUpdate, MaintenanceLog as MaintenanceLogSchema,
    MessageResponse, PaginatedResponse
)
from auth import get_current_user

router = APIRouter(prefix="/maintenance-logs", tags=["maintenance-logs"])

@router.get("/", response_model=List[MaintenanceLogSchema])
async def get_maintenance_logs(
    machine_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    log_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all maintenance logs with optional filtering"""
    query = db.query(MaintenanceLog)
    
    if machine_id:
        query = query.filter(MaintenanceLog.machine_id == machine_id)
    if user_id:
        query = query.filter(MaintenanceLog.user_id == user_id)
    if log_type:
        query = query.filter(MaintenanceLog.log_type == log_type)
    if start_date:
        query = query.filter(MaintenanceLog.performed_at >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.performed_at <= end_date)
    
    return query.order_by(MaintenanceLog.performed_at.desc()).all()

@router.get("/{log_id}", response_model=MaintenanceLogSchema)
async def get_maintenance_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific maintenance log"""
    maintenance_log = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
    if not maintenance_log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return maintenance_log

@router.post("/", response_model=MaintenanceLogSchema)
async def create_maintenance_log(
    log_data: MaintenanceLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new maintenance log"""
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == log_data.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == log_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    maintenance_log = MaintenanceLog(**log_data.dict())
    db.add(maintenance_log)
    db.commit()
    db.refresh(maintenance_log)
    return maintenance_log

@router.put("/{log_id}", response_model=MaintenanceLogSchema)
async def update_maintenance_log(
    log_id: int,
    log_data: MaintenanceLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a maintenance log"""
    maintenance_log = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
    if not maintenance_log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    
    for field, value in log_data.dict(exclude_unset=True).items():
        setattr(maintenance_log, field, value)
    
    db.commit()
    db.refresh(maintenance_log)
    return maintenance_log

@router.delete("/{log_id}", response_model=MessageResponse)
async def delete_maintenance_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a maintenance log"""
    maintenance_log = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
    if not maintenance_log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    
    db.delete(maintenance_log)
    db.commit()
    
    return MessageResponse(message="Maintenance log deleted successfully")

# Machine-specific logs
@router.get("/machine/{machine_id}", response_model=List[MaintenanceLogSchema])
async def get_machine_maintenance_logs(
    machine_id: int,
    log_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance logs for a specific machine"""
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    query = db.query(MaintenanceLog).filter(MaintenanceLog.machine_id == machine_id)
    
    if log_type:
        query = query.filter(MaintenanceLog.log_type == log_type)
    if start_date:
        query = query.filter(MaintenanceLog.performed_at >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.performed_at <= end_date)
    
    return query.order_by(MaintenanceLog.performed_at.desc()).all()

# User-specific logs
@router.get("/user/{user_id}", response_model=List[MaintenanceLogSchema])
async def get_user_maintenance_logs(
    user_id: int,
    log_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance logs for a specific user"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(MaintenanceLog).filter(MaintenanceLog.user_id == user_id)
    
    if log_type:
        query = query.filter(MaintenanceLog.log_type == log_type)
    if start_date:
        query = query.filter(MaintenanceLog.performed_at >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.performed_at <= end_date)
    
    return query.order_by(MaintenanceLog.performed_at.desc()).all()

# Dashboard routes
@router.get("/dashboard/recent")
async def get_recent_maintenance_logs(
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent maintenance logs"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    recent_logs = db.query(MaintenanceLog).filter(
        MaintenanceLog.performed_at >= start_date
    ).order_by(MaintenanceLog.performed_at.desc()).all()
    
    return {
        "recent_count": len(recent_logs),
        "recent_logs": recent_logs,
        "days_back": days
    }

@router.get("/dashboard/by-type")
async def get_maintenance_logs_by_type(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance logs grouped by type"""
    query = db.query(MaintenanceLog)
    
    if start_date:
        query = query.filter(MaintenanceLog.performed_at >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.performed_at <= end_date)
    
    logs = query.all()
    
    # Group by type
    type_counts = {}
    type_logs = {}
    
    for log in logs:
        log_type = log.log_type
        if log_type not in type_counts:
            type_counts[log_type] = 0
            type_logs[log_type] = []
        
        type_counts[log_type] += 1
        type_logs[log_type].append(log)
    
    return {
        "type_counts": type_counts,
        "type_logs": type_logs,
        "total_logs": len(logs)
    }

# Statistics routes
@router.get("/stats/summary")
async def get_maintenance_log_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance log statistics"""
    query = db.query(MaintenanceLog)
    
    if start_date:
        query = query.filter(MaintenanceLog.performed_at >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.performed_at <= end_date)
    
    logs = query.all()
    
    total_logs = len(logs)
    total_labor_hours = sum(log.labor_hours or 0 for log in logs)
    total_cost = sum(log.cost or 0 for log in logs)
    
    # Count by type
    type_counts = {}
    for log in logs:
        log_type = log.log_type
        type_counts[log_type] = type_counts.get(log_type, 0) + 1
    
    # Count by machine
    machine_counts = {}
    for log in logs:
        machine_id = log.machine_id
        machine_counts[machine_id] = machine_counts.get(machine_id, 0) + 1
    
    # Count by user
    user_counts = {}
    for log in logs:
        user_id = log.user_id
        user_counts[user_id] = user_counts.get(user_id, 0) + 1
    
    return {
        "total_logs": total_logs,
        "total_labor_hours": total_labor_hours,
        "total_cost": total_cost,
        "type_counts": type_counts,
        "machine_counts": machine_counts,
        "user_counts": user_counts,
        "average_cost_per_log": total_cost / total_logs if total_logs > 0 else 0,
        "average_labor_hours_per_log": total_labor_hours / total_logs if total_logs > 0 else 0
    }

@router.get("/stats/cost-analysis")
async def get_maintenance_cost_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed cost analysis"""
    query = db.query(MaintenanceLog)
    
    if start_date:
        query = query.filter(MaintenanceLog.performed_at >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.performed_at <= end_date)
    
    logs = query.all()
    
    # Cost by type
    cost_by_type = {}
    for log in logs:
        log_type = log.log_type
        cost = log.cost or 0
        if log_type not in cost_by_type:
            cost_by_type[log_type] = 0
        cost_by_type[log_type] += cost
    
    # Cost by machine
    cost_by_machine = {}
    for log in logs:
        machine_id = log.machine_id
        cost = log.cost or 0
        if machine_id not in cost_by_machine:
            cost_by_machine[machine_id] = 0
        cost_by_machine[machine_id] += cost
    
    # Monthly cost breakdown
    monthly_costs = {}
    for log in logs:
        month_key = log.performed_at.strftime("%Y-%m")
        cost = log.cost or 0
        if month_key not in monthly_costs:
            monthly_costs[month_key] = 0
        monthly_costs[month_key] += cost
    
    return {
        "cost_by_type": cost_by_type,
        "cost_by_machine": cost_by_machine,
        "monthly_costs": monthly_costs,
        "total_cost": sum(log.cost or 0 for log in logs)
    } 
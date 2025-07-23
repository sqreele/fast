"""
Maintenance management routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.models import (
    PMSchedule, PMExecution, Topic, Procedure, Machine, User,
    PMStatus, FrequencyType
)
from schemas import (
    PMScheduleCreate, PMScheduleUpdate, PMSchedule as PMScheduleSchema,
    PMExecutionCreate, PMExecutionUpdate, PMExecution as PMExecutionSchema,
    TopicCreate, TopicUpdate, Topic as TopicSchema,
    ProcedureCreate, ProcedureUpdate, Procedure as ProcedureSchema,
    MessageResponse, PaginatedResponse
)
from auth import get_current_user

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

# Topic routes
@router.get("/topics", response_model=List[TopicSchema])
async def get_topics(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all maintenance topics"""
    query = db.query(Topic)
    if is_active is not None:
        query = query.filter(Topic.is_active == is_active)
    return query.all()

@router.get("/topics/{topic_id}", response_model=TopicSchema)
async def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.post("/topics", response_model=TopicSchema)
async def create_topic(
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new topic"""
    topic = Topic(**topic_data.dict())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
async def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    for field, value in topic_data.dict(exclude_unset=True).items():
        setattr(topic, field, value)
    
    topic.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(topic)
    return topic

@router.delete("/topics/{topic_id}", response_model=MessageResponse)
async def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a topic (soft delete)"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic.is_active = False
    topic.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Topic deleted successfully")

# Procedure routes
@router.get("/topics/{topic_id}/procedures", response_model=List[ProcedureSchema])
async def get_procedures(
    topic_id: int,
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all procedures for a topic"""
    query = db.query(Procedure).filter(Procedure.topic_id == topic_id)
    if is_active is not None:
        query = query.filter(Procedure.is_active == is_active)
    return query.all()

@router.get("/topics/{topic_id}/procedures/{procedure_id}", response_model=ProcedureSchema)
async def get_procedure(
    topic_id: int,
    procedure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific procedure"""
    procedure = db.query(Procedure).filter(
        Procedure.id == procedure_id,
        Procedure.topic_id == topic_id
    ).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return procedure

@router.post("/topics/{topic_id}/procedures", response_model=ProcedureSchema)
async def create_procedure(
    topic_id: int,
    procedure_data: ProcedureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new procedure"""
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    procedure_data_dict = procedure_data.dict()
    procedure_data_dict["topic_id"] = topic_id
    procedure = Procedure(**procedure_data_dict)
    
    db.add(procedure)
    db.commit()
    db.refresh(procedure)
    return procedure

@router.put("/topics/{topic_id}/procedures/{procedure_id}", response_model=ProcedureSchema)
async def update_procedure(
    topic_id: int,
    procedure_id: int,
    procedure_data: ProcedureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a procedure"""
    procedure = db.query(Procedure).filter(
        Procedure.id == procedure_id,
        Procedure.topic_id == topic_id
    ).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    for field, value in procedure_data.dict(exclude_unset=True).items():
        setattr(procedure, field, value)
    
    procedure.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(procedure)
    return procedure

@router.delete("/topics/{topic_id}/procedures/{procedure_id}", response_model=MessageResponse)
async def delete_procedure(
    topic_id: int,
    procedure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a procedure (soft delete)"""
    procedure = db.query(Procedure).filter(
        Procedure.id == procedure_id,
        Procedure.topic_id == topic_id
    ).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    procedure.is_active = False
    procedure.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Procedure deleted successfully")

# PM Schedule routes
@router.get("/schedules", response_model=List[PMScheduleSchema])
async def get_pm_schedules(
    machine_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    overdue: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all PM schedules with optional filtering"""
    query = db.query(PMSchedule)
    
    if machine_id:
        query = query.filter(PMSchedule.machine_id == machine_id)
    if user_id:
        query = query.filter(PMSchedule.user_id == user_id)
    if is_active is not None:
        query = query.filter(PMSchedule.is_active == is_active)
    if overdue:
        query = query.filter(PMSchedule.next_due < datetime.utcnow())
    
    return query.all()

@router.get("/schedules/{schedule_id}", response_model=PMScheduleSchema)
async def get_pm_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific PM schedule"""
    schedule = db.query(PMSchedule).filter(PMSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="PM Schedule not found")
    return schedule

@router.post("/schedules", response_model=PMScheduleSchema)
async def create_pm_schedule(
    schedule_data: PMScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new PM schedule"""
    # Verify machine and procedure exist
    machine = db.query(Machine).filter(Machine.id == schedule_data.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    procedure = db.query(Procedure).filter(Procedure.id == schedule_data.procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    schedule = PMSchedule(**schedule_data.dict())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.put("/schedules/{schedule_id}", response_model=PMScheduleSchema)
async def update_pm_schedule(
    schedule_id: int,
    schedule_data: PMScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a PM schedule"""
    schedule = db.query(PMSchedule).filter(PMSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="PM Schedule not found")
    
    for field, value in schedule_data.dict(exclude_unset=True).items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/schedules/{schedule_id}", response_model=MessageResponse)
async def delete_pm_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a PM schedule (soft delete)"""
    schedule = db.query(PMSchedule).filter(PMSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="PM Schedule not found")
    
    schedule.is_active = False
    schedule.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="PM Schedule deleted successfully")

# PM Execution routes
@router.get("/schedules/{schedule_id}/executions", response_model=List[PMExecutionSchema])
async def get_pm_executions(
    schedule_id: int,
    status: Optional[PMStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all executions for a PM schedule"""
    query = db.query(PMExecution).filter(PMExecution.pm_schedule_id == schedule_id)
    if status:
        query = query.filter(PMExecution.status == status)
    return query.all()

@router.get("/executions/{execution_id}", response_model=PMExecutionSchema)
async def get_pm_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific PM execution"""
    execution = db.query(PMExecution).filter(PMExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="PM Execution not found")
    return execution

@router.post("/schedules/{schedule_id}/executions", response_model=PMExecutionSchema)
async def create_pm_execution(
    schedule_id: int,
    execution_data: PMExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new PM execution"""
    # Verify schedule exists
    schedule = db.query(PMSchedule).filter(PMSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="PM Schedule not found")
    
    execution_data_dict = execution_data.dict()
    execution_data_dict["pm_schedule_id"] = schedule_id
    execution_data_dict["executed_by_id"] = current_user.id
    
    execution = PMExecution(**execution_data_dict)
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution

@router.put("/executions/{execution_id}", response_model=PMExecutionSchema)
async def update_pm_execution(
    execution_id: int,
    execution_data: PMExecutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a PM execution"""
    execution = db.query(PMExecution).filter(PMExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="PM Execution not found")
    
    for field, value in execution_data.dict(exclude_unset=True).items():
        setattr(execution, field, value)
    
    # If status is completed, update the schedule's last_completed
    if execution_data.status == PMStatus.COMPLETED:
        execution.completed_at = datetime.utcnow()
        # Update the schedule's last_completed
        schedule = execution.pm_schedule
        schedule.last_completed = execution.completed_at
        
        # Calculate next due date based on frequency
        if schedule.frequency == FrequencyType.DAILY:
            schedule.next_due = execution.completed_at + timedelta(days=schedule.frequency_value)
        elif schedule.frequency == FrequencyType.WEEKLY:
            schedule.next_due = execution.completed_at + timedelta(weeks=schedule.frequency_value)
        elif schedule.frequency == FrequencyType.MONTHLY:
            schedule.next_due = execution.completed_at + timedelta(days=30 * schedule.frequency_value)
        elif schedule.frequency == FrequencyType.QUARTERLY:
            schedule.next_due = execution.completed_at + timedelta(days=90 * schedule.frequency_value)
        elif schedule.frequency == FrequencyType.ANNUAL:
            schedule.next_due = execution.completed_at + timedelta(days=365 * schedule.frequency_value)
    
    execution.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(execution)
    return execution

@router.delete("/executions/{execution_id}", response_model=MessageResponse)
async def delete_pm_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a PM execution"""
    execution = db.query(PMExecution).filter(PMExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="PM Execution not found")
    
    db.delete(execution)
    db.commit()
    
    return MessageResponse(message="PM Execution deleted successfully")

# Dashboard routes
@router.get("/dashboard/overdue")
async def get_overdue_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all overdue PM schedules"""
    overdue_schedules = db.query(PMSchedule).filter(
        PMSchedule.next_due < datetime.utcnow(),
        PMSchedule.is_active == True
    ).all()
    
    return {
        "overdue_count": len(overdue_schedules),
        "overdue_schedules": overdue_schedules
    }

@router.get("/dashboard/upcoming")
async def get_upcoming_schedules(
    days: int = Query(7, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming PM schedules"""
    end_date = datetime.utcnow() + timedelta(days=days)
    upcoming_schedules = db.query(PMSchedule).filter(
        PMSchedule.next_due >= datetime.utcnow(),
        PMSchedule.next_due <= end_date,
        PMSchedule.is_active == True
    ).all()
    
    return {
        "upcoming_count": len(upcoming_schedules),
        "upcoming_schedules": upcoming_schedules,
        "days_ahead": days
    } 
"""
FastAPI routes for Job management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Job, JobUserAssignment, User, Property, Room, Topic, JobStatus
from schemas import (
    JobCreate, JobUpdate, Job as JobSchema, JobWithAssignments,
    JobUserAssignmentCreate, JobUserAssignmentUpdate, JobUserAssignment as JobUserAssignmentSchema
)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

# Job CRUD operations
@router.post("/", response_model=JobSchema)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job"""
    # Verify that the property exists
    property_exists = db.query(Property).filter(Property.id == job.property_id).first()
    if not property_exists:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Verify that the creator exists
    creator = db.query(User).filter(User.id == job.created_by_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator user not found")
    
    # Verify optional room and topic if provided
    if job.room_id:
        room = db.query(Room).filter(Room.id == job.room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if room.property_id != job.property_id:
            raise HTTPException(status_code=400, detail="Room does not belong to the specified property")
    
    if job.topic_id:
        topic = db.query(Topic).filter(Topic.id == job.topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
    
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("/", response_model=List[JobSchema])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[JobStatus] = None,
    property_id: Optional[int] = None,
    room_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    created_by_id: Optional[int] = None,
    assigned_user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get jobs with optional filtering"""
    query = db.query(Job)
    
    if status:
        query = query.filter(Job.status == status)
    if property_id:
        query = query.filter(Job.property_id == property_id)
    if room_id:
        query = query.filter(Job.room_id == room_id)
    if topic_id:
        query = query.filter(Job.topic_id == topic_id)
    if created_by_id:
        query = query.filter(Job.created_by_id == created_by_id)
    
    if assigned_user_id:
        query = query.join(JobUserAssignment).filter(
            JobUserAssignment.user_id == assigned_user_id,
            JobUserAssignment.is_active == True
        )
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobWithAssignments)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job with user assignments"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobSchema)
async def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Update a job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Validate room belongs to property if both are being updated
    if job_update.room_id and job_update.property_id:
        room = db.query(Room).filter(Room.id == job_update.room_id).first()
        if room and room.property_id != job_update.property_id:
            raise HTTPException(status_code=400, detail="Room does not belong to the specified property")
    elif job_update.room_id:
        room = db.query(Room).filter(Room.id == job_update.room_id).first()
        if room and room.property_id != db_job.property_id:
            raise HTTPException(status_code=400, detail="Room does not belong to the job's property")
    
    # Update job fields
    update_data = job_update.dict(exclude_unset=True)
    
    # Auto-set started_at when status changes to IN_PROGRESS
    if (job_update.status == JobStatus.IN_PROGRESS and 
        db_job.status != JobStatus.IN_PROGRESS and 
        not db_job.started_at):
        update_data['started_at'] = datetime.utcnow()
    
    # Auto-set completed_at when status changes to COMPLETED
    if (job_update.status == JobStatus.COMPLETED and 
        db_job.status != JobStatus.COMPLETED and 
        not db_job.completed_at):
        update_data['completed_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job

@router.delete("/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete associated assignments first
    db.query(JobUserAssignment).filter(JobUserAssignment.job_id == job_id).delete()
    
    db.delete(db_job)
    db.commit()
    return {"message": "Job deleted successfully"}

# Job User Assignment operations
@router.post("/{job_id}/assignments", response_model=JobUserAssignmentSchema)
async def assign_user_to_job(
    job_id: int, 
    assignment: JobUserAssignmentCreate, 
    db: Session = Depends(get_db)
):
    """Assign a user to a job"""
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == assignment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify assigner exists
    assigner = db.query(User).filter(User.id == assignment.assigned_by_id).first()
    if not assigner:
        raise HTTPException(status_code=404, detail="Assigner user not found")
    
    # Check if user is already assigned to this job
    existing_assignment = db.query(JobUserAssignment).filter(
        JobUserAssignment.job_id == job_id,
        JobUserAssignment.user_id == assignment.user_id,
        JobUserAssignment.is_active == True
    ).first()
    
    if existing_assignment:
        raise HTTPException(status_code=400, detail="User is already assigned to this job")
    
    # Create assignment
    assignment_data = assignment.dict()
    assignment_data['job_id'] = job_id
    db_assignment = JobUserAssignment(**assignment_data)
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.get("/{job_id}/assignments", response_model=List[JobUserAssignmentSchema])
async def get_job_assignments(job_id: int, db: Session = Depends(get_db)):
    """Get all user assignments for a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    assignments = db.query(JobUserAssignment).filter(
        JobUserAssignment.job_id == job_id,
        JobUserAssignment.is_active == True
    ).all()
    
    return assignments

@router.put("/assignments/{assignment_id}", response_model=JobUserAssignmentSchema)
async def update_job_assignment(
    assignment_id: int,
    assignment_update: JobUserAssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Update a job user assignment"""
    db_assignment = db.query(JobUserAssignment).filter(
        JobUserAssignment.id == assignment_id
    ).first()
    
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    update_data = assignment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assignment, field, value)
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.delete("/assignments/{assignment_id}")
async def remove_job_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Remove a user assignment from a job"""
    db_assignment = db.query(JobUserAssignment).filter(
        JobUserAssignment.id == assignment_id
    ).first()
    
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Soft delete by setting is_active to False
    db_assignment.is_active = False
    db.commit()
    
    return {"message": "Assignment removed successfully"}

# Utility endpoints
@router.get("/{job_id}/history")
async def get_job_history(job_id: int, db: Session = Depends(get_db)):
    """Get assignment history for a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    assignments = db.query(JobUserAssignment).filter(
        JobUserAssignment.job_id == job_id
    ).order_by(JobUserAssignment.assigned_at.desc()).all()
    
    return assignments

@router.get("/user/{user_id}/assigned", response_model=List[JobSchema])
async def get_user_assigned_jobs(
    user_id: int,
    status: Optional[JobStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all jobs assigned to a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Job).join(JobUserAssignment).filter(
        JobUserAssignment.user_id == user_id,
        JobUserAssignment.is_active == True
    )
    
    if status:
        query = query.filter(Job.status == status)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs
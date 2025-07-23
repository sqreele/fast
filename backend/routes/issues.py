"""
Issue and inspection management routes for PM System API
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.models import (
    Issue, Inspection, Machine, Room, User, Procedure,
    IssueStatus, IssuePriority, InspectionResult
)
from schemas import (
    IssueCreate, IssueUpdate, Issue as IssueSchema,
    InspectionCreate, InspectionUpdate, Inspection as InspectionSchema,
    MessageResponse, PaginatedResponse
)
from auth import get_current_user

router = APIRouter(prefix="/issues", tags=["issues"])

# Issue routes
@router.get("/", response_model=List[IssueSchema])
async def get_issues(
    machine_id: Optional[int] = Query(None),
    room_id: Optional[int] = Query(None),
    reported_by_id: Optional[int] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    status: Optional[IssueStatus] = Query(None),
    priority: Optional[IssuePriority] = Query(None),
    is_open: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all issues with optional filtering"""
    query = db.query(Issue)
    
    if machine_id:
        query = query.filter(Issue.machine_id == machine_id)
    if room_id:
        query = query.filter(Issue.room_id == room_id)
    if reported_by_id:
        query = query.filter(Issue.reported_by_id == reported_by_id)
    if assigned_to_id:
        query = query.filter(Issue.assigned_to_id == assigned_to_id)
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if is_open is not None:
        if is_open:
            query = query.filter(Issue.status.in_([IssueStatus.OPEN, IssueStatus.ASSIGNED, IssueStatus.IN_PROGRESS]))
        else:
            query = query.filter(Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED]))
    
    return query.order_by(Issue.reported_at.desc()).all()

@router.get("/{issue_id}", response_model=IssueSchema)
async def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.post("/", response_model=IssueSchema)
async def create_issue(
    issue_data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new issue"""
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == issue_data.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Set reporter to current user if not specified
    issue_data_dict = issue_data.dict()
    if not issue_data_dict.get("reported_by_id"):
        issue_data_dict["reported_by_id"] = current_user.id
    
    issue = Issue(**issue_data_dict)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@router.put("/{issue_id}", response_model=IssueSchema)
async def update_issue(
    issue_id: int,
    issue_data: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    for field, value in issue_data.dict(exclude_unset=True).items():
        setattr(issue, field, value)
    
    # If status is resolved or closed, set resolved_at
    if issue_data.status in [IssueStatus.RESOLVED, IssueStatus.CLOSED]:
        issue.resolved_at = datetime.utcnow()
    
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue

@router.delete("/{issue_id}", response_model=MessageResponse)
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db.delete(issue)
    db.commit()
    
    return MessageResponse(message="Issue deleted successfully")

# Issue assignment routes
@router.put("/{issue_id}/assign", response_model=IssueSchema)
async def assign_issue(
    issue_id: int,
    assigned_to_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign an issue to a user"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    issue.assigned_to_id = assigned_to_id
    issue.status = IssueStatus.ASSIGNED
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue

@router.put("/{issue_id}/status", response_model=IssueSchema)
async def update_issue_status(
    issue_id: int,
    status: IssueStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update issue status"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue.status = status
    
    # If status is resolved or closed, set resolved_at
    if status in [IssueStatus.RESOLVED, IssueStatus.CLOSED]:
        issue.resolved_at = datetime.utcnow()
    
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue

# Inspection routes
@router.get("/inspections", response_model=List[InspectionSchema])
async def get_inspections(
    machine_id: Optional[int] = Query(None),
    inspector_id: Optional[int] = Query(None),
    procedure_id: Optional[int] = Query(None),
    result: Optional[InspectionResult] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all inspections with optional filtering"""
    query = db.query(Inspection)
    
    if machine_id:
        query = query.filter(Inspection.machine_id == machine_id)
    if inspector_id:
        query = query.filter(Inspection.inspector_id == inspector_id)
    if procedure_id:
        query = query.filter(Inspection.procedure_id == procedure_id)
    if result:
        query = query.filter(Inspection.result == result)
    
    return query.order_by(Inspection.inspection_date.desc()).all()

@router.get("/inspections/{inspection_id}", response_model=InspectionSchema)
async def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific inspection"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection

@router.post("/inspections", response_model=InspectionSchema)
async def create_inspection(
    inspection_data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new inspection"""
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == inspection_data.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Set inspector to current user if not specified
    inspection_data_dict = inspection_data.dict()
    if not inspection_data_dict.get("inspector_id"):
        inspection_data_dict["inspector_id"] = current_user.id
    
    inspection = Inspection(**inspection_data_dict)
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection

@router.put("/inspections/{inspection_id}", response_model=InspectionSchema)
async def update_inspection(
    inspection_id: int,
    inspection_data: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an inspection"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    for field, value in inspection_data.dict(exclude_unset=True).items():
        setattr(inspection, field, value)
    
    inspection.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(inspection)
    return inspection

@router.delete("/inspections/{inspection_id}", response_model=MessageResponse)
async def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an inspection"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    db.delete(inspection)
    db.commit()
    
    return MessageResponse(message="Inspection deleted successfully")

# Dashboard routes
@router.get("/dashboard/open-issues")
async def get_open_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all open issues"""
    open_issues = db.query(Issue).filter(
        Issue.status.in_([IssueStatus.OPEN, IssueStatus.ASSIGNED, IssueStatus.IN_PROGRESS])
    ).all()
    
    return {
        "open_count": len(open_issues),
        "open_issues": open_issues
    }

@router.get("/dashboard/critical-issues")
async def get_critical_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all critical issues"""
    critical_issues = db.query(Issue).filter(
        Issue.priority == IssuePriority.CRITICAL,
        Issue.status.in_([IssueStatus.OPEN, IssueStatus.ASSIGNED, IssueStatus.IN_PROGRESS])
    ).all()
    
    return {
        "critical_count": len(critical_issues),
        "critical_issues": critical_issues
    }

@router.get("/dashboard/failed-inspections")
async def get_failed_inspections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all failed inspections"""
    failed_inspections = db.query(Inspection).filter(
        Inspection.result.in_([InspectionResult.FAIL, InspectionResult.NEEDS_ATTENTION])
    ).all()
    
    return {
        "failed_count": len(failed_inspections),
        "failed_inspections": failed_inspections
    }

# Statistics routes
@router.get("/stats/issues")
async def get_issue_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get issue statistics"""
    total_issues = db.query(Issue).count()
    open_issues = db.query(Issue).filter(
        Issue.status.in_([IssueStatus.OPEN, IssueStatus.ASSIGNED, IssueStatus.IN_PROGRESS])
    ).count()
    critical_issues = db.query(Issue).filter(
        Issue.priority == IssuePriority.CRITICAL,
        Issue.status.in_([IssueStatus.OPEN, IssueStatus.ASSIGNED, IssueStatus.IN_PROGRESS])
    ).count()
    resolved_issues = db.query(Issue).filter(
        Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED])
    ).count()
    
    return {
        "total_issues": total_issues,
        "open_issues": open_issues,
        "critical_issues": critical_issues,
        "resolved_issues": resolved_issues,
        "resolution_rate": (resolved_issues / total_issues * 100) if total_issues > 0 else 0
    }

@router.get("/stats/inspections")
async def get_inspection_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inspection statistics"""
    total_inspections = db.query(Inspection).count()
    passed_inspections = db.query(Inspection).filter(Inspection.result == InspectionResult.PASS).count()
    failed_inspections = db.query(Inspection).filter(Inspection.result == InspectionResult.FAIL).count()
    needs_attention = db.query(Inspection).filter(Inspection.result == InspectionResult.NEEDS_ATTENTION).count()
    
    return {
        "total_inspections": total_inspections,
        "passed_inspections": passed_inspections,
        "failed_inspections": failed_inspections,
        "needs_attention": needs_attention,
        "pass_rate": (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0
    } 
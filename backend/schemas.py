"""
Pydantic schemas for PM System API
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.models import (
    UserRole, FrequencyType, PMStatus, IssueStatus, IssuePriority,
    InspectionResult, ImageType, AccessLevel, MachineType, MachineStatus,
    WorkOrderStatus, WorkOrderType, NotificationType, JobStatus
)

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# User schemas
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(True, description="User active status")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Property schemas
class PropertyBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100, description="Property name")
    address: Optional[str] = Field(None, description="Property address")
    is_active: bool = Field(True, description="Property active status")

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = None
    is_active: Optional[bool] = None

class Property(PropertyBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Room schemas
class RoomBase(BaseSchema):
    property_id: int = Field(..., description="Property ID")
    name: str = Field(..., min_length=1, max_length=100, description="Room name")
    room_number: Optional[str] = Field(None, max_length=20, description="Room number")
    is_active: bool = Field(True, description="Room active status")

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseSchema):
    property_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    room_number: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class Room(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime
    property: Optional[Property] = None

# Machine schemas
class MachineBase(BaseSchema):
    room_id: int = Field(..., description="Room ID")
    name: str = Field(..., min_length=1, max_length=100, description="Machine name")
    model: Optional[str] = Field(None, max_length=100, description="Machine model")
    serial_number: str = Field(..., max_length=100, description="Unique serial number")
    manufacturer: Optional[str] = Field(None, max_length=100, description="Machine manufacturer")
    machine_type: MachineType = Field(MachineType.OTHER, description="Machine type")
    status: MachineStatus = Field(MachineStatus.OPERATIONAL, description="Machine status")
    description: Optional[str] = Field(None, description="Machine description")
    specifications: Optional[str] = Field(None, description="Machine specifications (JSON)")
    installation_date: Optional[datetime] = Field(None, description="Installation date")
    warranty_expiry: Optional[datetime] = Field(None, description="Warranty expiry date")
    last_maintenance: Optional[datetime] = Field(None, description="Last maintenance date")
    next_maintenance: Optional[datetime] = Field(None, description="Next maintenance date")
    is_active: bool = Field(True, description="Machine active status")

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseSchema):
    room_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    machine_type: Optional[MachineType] = None
    status: Optional[MachineStatus] = None
    description: Optional[str] = None
    specifications: Optional[str] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    is_active: Optional[bool] = None

class Machine(MachineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    room: Optional[Room] = None

# Topic schemas
class TopicBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=100, description="Topic title")
    description: Optional[str] = Field(None, description="Topic description")
    is_active: bool = Field(True, description="Topic active status")

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Topic(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Procedure schemas
class ProcedureBase(BaseSchema):
    topic_id: int = Field(..., description="Topic ID")
    title: str = Field(..., min_length=1, max_length=100, description="Procedure title")
    description: Optional[str] = Field(None, description="Procedure description")
    instructions: Optional[str] = Field(None, description="Procedure instructions")
    estimated_minutes: Optional[int] = Field(None, ge=1, description="Estimated duration in minutes")
    is_active: bool = Field(True, description="Procedure active status")

class ProcedureCreate(ProcedureBase):
    pass

class ProcedureUpdate(BaseSchema):
    topic_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    instructions: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

class Procedure(ProcedureBase):
    id: int
    created_at: datetime
    updated_at: datetime
    topic: Optional[Topic] = None

# PM Schedule schemas
class PMScheduleBase(BaseSchema):
    machine_id: int = Field(..., description="Machine ID")
    procedure_id: int = Field(..., description="Procedure ID")
    user_id: int = Field(..., description="Responsible user ID")
    frequency: FrequencyType = Field(..., description="Maintenance frequency")
    frequency_value: int = Field(1, ge=1, description="Frequency multiplier")
    last_completed: Optional[datetime] = Field(None, description="Last completion date")
    next_due: datetime = Field(..., description="Next due date")
    is_active: bool = Field(True, description="Schedule active status")

class PMScheduleCreate(PMScheduleBase):
    pass

class PMScheduleUpdate(BaseSchema):
    machine_id: Optional[int] = None
    procedure_id: Optional[int] = None
    user_id: Optional[int] = None
    frequency: Optional[FrequencyType] = None
    frequency_value: Optional[int] = Field(None, ge=1)
    last_completed: Optional[datetime] = None
    next_due: Optional[datetime] = None
    is_active: Optional[bool] = None

class PMSchedule(PMScheduleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    machine: Optional[Machine] = None
    procedure: Optional[Procedure] = None
    responsible_user: Optional[User] = None

# PM Execution schemas
class PMExecutionBase(BaseSchema):
    pm_schedule_id: int = Field(..., description="PM Schedule ID")
    executed_by_id: int = Field(..., description="Executor user ID")
    status: PMStatus = Field(PMStatus.SCHEDULED, description="Execution status")
    notes: Optional[str] = Field(None, description="Execution notes")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    next_due_calculated: Optional[datetime] = Field(None, description="Calculated next due date")

class PMExecutionCreate(PMExecutionBase):
    pass

class PMExecutionUpdate(BaseSchema):
    pm_schedule_id: Optional[int] = None
    executed_by_id: Optional[int] = None
    status: Optional[PMStatus] = None
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_due_calculated: Optional[datetime] = None

class PMExecution(PMExecutionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    pm_schedule: Optional[PMSchedule] = None
    executor: Optional[User] = None

# Issue schemas
class IssueBase(BaseSchema):
    machine_id: int = Field(..., description="Machine ID")
    room_id: Optional[int] = Field(None, description="Room ID")
    reported_by_id: int = Field(..., description="Reporter user ID")
    assigned_to_id: Optional[int] = Field(None, description="Assignee user ID")
    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    priority: IssuePriority = Field(IssuePriority.MEDIUM, description="Issue priority")
    status: IssueStatus = Field(IssueStatus.OPEN, description="Issue status")
    reported_at: Optional[datetime] = Field(None, description="Report date")
    resolved_at: Optional[datetime] = Field(None, description="Resolution date")

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseSchema):
    machine_id: Optional[int] = None
    room_id: Optional[int] = None
    reported_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[IssuePriority] = None
    status: Optional[IssueStatus] = None
    reported_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class Issue(IssueBase):
    id: int
    created_at: datetime
    updated_at: datetime
    machine: Optional[Machine] = None
    room: Optional[Room] = None
    reporter: Optional[User] = None
    assignee: Optional[User] = None

# Inspection schemas
class InspectionBase(BaseSchema):
    machine_id: int = Field(..., description="Machine ID")
    inspector_id: int = Field(..., description="Inspector user ID")
    procedure_id: Optional[int] = Field(None, description="Procedure ID")
    title: str = Field(..., min_length=1, max_length=200, description="Inspection title")
    findings: Optional[str] = Field(None, description="Inspection findings")
    result: InspectionResult = Field(..., description="Inspection result")
    inspection_date: datetime = Field(..., description="Inspection date")

class InspectionCreate(InspectionBase):
    pass

class InspectionUpdate(BaseSchema):
    machine_id: Optional[int] = None
    inspector_id: Optional[int] = None
    procedure_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    findings: Optional[str] = None
    result: Optional[InspectionResult] = None
    inspection_date: Optional[datetime] = None

class Inspection(InspectionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    machine: Optional[Machine] = None
    inspector: Optional[User] = None
    procedure: Optional[Procedure] = None

# PM File schemas
class PMFileBase(BaseSchema):
    pm_execution_id: Optional[int] = Field(None, description="PM Execution ID")
    issue_id: Optional[int] = Field(None, description="Issue ID")
    inspection_id: Optional[int] = Field(None, description="Inspection ID")
    file_name: str = Field(..., max_length=255, description="File name")
    file_path: str = Field(..., max_length=500, description="File path")
    file_type: str = Field(..., max_length=50, description="File type")
    image_type: Optional[ImageType] = Field(None, description="Image type")
    description: Optional[str] = Field(None, description="File description")
    uploaded_at: Optional[datetime] = Field(None, description="Upload date")

class PMFileCreate(PMFileBase):
    pass

class PMFileUpdate(BaseSchema):
    pm_execution_id: Optional[int] = None
    issue_id: Optional[int] = None
    inspection_id: Optional[int] = None
    file_name: Optional[str] = Field(None, max_length=255)
    file_path: Optional[str] = Field(None, max_length=500)
    file_type: Optional[str] = Field(None, max_length=50)
    image_type: Optional[ImageType] = None
    description: Optional[str] = None
    uploaded_at: Optional[datetime] = None

class PMFile(PMFileBase):
    id: int
    pm_execution: Optional[PMExecution] = None
    issue: Optional[Issue] = None
    inspection: Optional[Inspection] = None

# User Property Access schemas
class UserPropertyAccessBase(BaseSchema):
    user_id: int = Field(..., description="User ID")
    property_id: int = Field(..., description="Property ID")
    access_level: AccessLevel = Field(..., description="Access level")
    granted_at: Optional[datetime] = Field(None, description="Grant date")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")

class UserPropertyAccessCreate(UserPropertyAccessBase):
    pass

class UserPropertyAccessUpdate(BaseSchema):
    user_id: Optional[int] = None
    property_id: Optional[int] = None
    access_level: Optional[AccessLevel] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class UserPropertyAccess(UserPropertyAccessBase):
    user: Optional[User] = None
    property: Optional[Property] = None

# Response schemas
class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class MessageResponse(BaseSchema):
    message: str
    success: bool = True

class ErrorResponse(BaseSchema):
    message: str
    error: str
    success: bool = False

# Statistics schemas
class SystemStats(BaseSchema):
    users: Dict[str, Any]
    properties: Dict[str, Any]
    machines: Dict[str, Any]
    pm_schedules: Dict[str, Any]
    issues: Dict[str, Any]

class MigrationStatus(BaseSchema):
    current_revision: str
    head_revision: str
    is_up_to_date: bool
    needs_migration: bool

class MigrationHistory(BaseSchema):
    history: str
    raw_output: str

# Search and filter schemas
class SearchParams(BaseSchema):
    query: Optional[str] = Field(None, description="Search query")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order")

class UserSearchParams(SearchParams):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class IssueSearchParams(SearchParams):
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    machine_id: Optional[int] = None
    assigned_to_id: Optional[int] = None

class PMScheduleSearchParams(SearchParams):
    frequency: Optional[FrequencyType] = None
    is_active: Optional[bool] = None
    machine_id: Optional[int] = None
    user_id: Optional[int] = None
    overdue: Optional[bool] = None

# Dashboard schemas
class DashboardStats(BaseSchema):
    total_users: int
    active_users: int
    total_machines: int
    active_machines: int
    total_issues: int
    open_issues: int
    critical_issues: int
    overdue_pm: int
    completed_pm_today: int

class RecentActivity(BaseSchema):
    id: int
    type: str
    title: str
    description: str
    created_at: datetime
    user: Optional[User] = None

# Export schemas
class ExportRequest(BaseSchema):
    entity_type: str = Field(..., description="Entity type to export")
    format: str = Field("csv", pattern="^(csv|json|excel)$", description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")

class ExportResponse(BaseSchema):
    download_url: str
    filename: str
    expires_at: datetime

# Work Order schemas
class WorkOrderBase(BaseSchema):
    machine_id: int = Field(..., description="Machine ID")
    created_by_id: int = Field(..., description="Creator user ID")
    assigned_to_id: Optional[int] = Field(None, description="Assigned user ID")
    work_order_type: WorkOrderType = Field(..., description="Work order type")
    status: WorkOrderStatus = Field(WorkOrderStatus.DRAFT, description="Work order status")
    title: str = Field(..., min_length=1, max_length=200, description="Work order title")
    description: Optional[str] = Field(None, description="Work order description")
    priority: IssuePriority = Field(IssuePriority.MEDIUM, description="Work order priority")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Estimated hours")
    actual_hours: Optional[int] = Field(None, ge=0, description="Actual hours")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    cost_estimate: Optional[int] = Field(None, ge=0, description="Cost estimate in cents")
    actual_cost: Optional[int] = Field(None, ge=0, description="Actual cost in cents")
    notes: Optional[str] = Field(None, description="Work order notes")
    is_active: bool = Field(True, description="Work order active status")

class WorkOrderCreate(WorkOrderBase):
    pass

class WorkOrderUpdate(BaseSchema):
    machine_id: Optional[int] = None
    created_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    work_order_type: Optional[WorkOrderType] = None
    status: Optional[WorkOrderStatus] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[IssuePriority] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cost_estimate: Optional[int] = Field(None, ge=0)
    actual_cost: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class WorkOrder(WorkOrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    machine: Optional[Machine] = None
    created_by: Optional[User] = None
    assigned_to: Optional[User] = None

# Notification schemas
class NotificationBase(BaseSchema):
    user_id: int = Field(..., description="User ID")
    notification_type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., description="Notification message")
    is_read: bool = Field(False, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    related_entity_type: Optional[str] = Field(None, max_length=50, description="Related entity type")
    related_entity_id: Optional[int] = Field(None, description="Related entity ID")

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseSchema):
    user_id: Optional[int] = None
    notification_type: Optional[NotificationType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = None
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = None

class Notification(NotificationBase):
    id: int
    created_at: datetime
    user: Optional[User] = None

# Maintenance Log schemas
class MaintenanceLogBase(BaseSchema):
    machine_id: int = Field(..., description="Machine ID")
    user_id: int = Field(..., description="User ID")
    log_type: str = Field(..., max_length=50, description="Log type")
    title: str = Field(..., min_length=1, max_length=200, description="Log title")
    description: Optional[str] = Field(None, description="Log description")
    parts_used: Optional[str] = Field(None, description="Parts used (JSON)")
    labor_hours: Optional[int] = Field(None, ge=0, description="Labor hours")
    cost: Optional[int] = Field(None, ge=0, description="Cost in cents")
    performed_at: datetime = Field(..., description="Performed date")

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLogUpdate(BaseSchema):
    machine_id: Optional[int] = None
    user_id: Optional[int] = None
    log_type: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    parts_used: Optional[str] = None
    labor_hours: Optional[int] = Field(None, ge=0)
    cost: Optional[int] = Field(None, ge=0)
    performed_at: Optional[datetime] = None

class MaintenanceLog(MaintenanceLogBase):
    id: int
    created_at: datetime
    machine: Optional[Machine] = None
    user: Optional[User] = None

# Job schemas
class JobBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200, description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    topic_id: Optional[int] = Field(None, description="Related topic ID")
    room_id: Optional[int] = Field(None, description="Room ID where job is performed")
    property_id: int = Field(..., description="Property ID where job is performed")
    status: JobStatus = Field(JobStatus.PENDING, description="Job status")
    before_image: Optional[str] = Field(None, max_length=500, description="Before image file path")
    after_image: Optional[str] = Field(None, max_length=500, description="After image file path")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Estimated hours to complete")
    actual_hours: Optional[int] = Field(None, ge=0, description="Actual hours spent")
    priority: IssuePriority = Field(IssuePriority.MEDIUM, description="Job priority")

class JobCreate(JobBase):
    created_by_id: int = Field(..., description="User ID who created the job")

class JobUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    topic_id: Optional[int] = None
    room_id: Optional[int] = None
    status: Optional[JobStatus] = None
    before_image: Optional[str] = Field(None, max_length=500)
    after_image: Optional[str] = Field(None, max_length=500)
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    priority: Optional[IssuePriority] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Job(JobBase):
    id: int
    created_by_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    topic: Optional[Topic] = None
    room: Optional[Room] = None
    property: Optional[Property] = None
    created_by: Optional[User] = None

# JobUserAssignment schemas
class JobUserAssignmentBase(BaseSchema):
    job_id: int = Field(..., description="Job ID")
    user_id: int = Field(..., description="User ID")
    role_in_job: str = Field("ASSIGNEE", max_length=50, description="Role in job (ASSIGNEE, SUPERVISOR, etc.)")
    notes: Optional[str] = Field(None, description="Assignment notes")
    is_active: bool = Field(True, description="Assignment active status")

class JobUserAssignmentCreate(JobUserAssignmentBase):
    assigned_by_id: int = Field(..., description="User ID who made the assignment")

class JobUserAssignmentUpdate(BaseSchema):
    role_in_job: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class JobUserAssignment(JobUserAssignmentBase):
    id: int
    assigned_by_id: int
    assigned_at: datetime
    job: Optional[Job] = None
    user: Optional[User] = None
    assigned_by: Optional[User] = None

# Job with assignments schema
class JobWithAssignments(Job):
    user_assignments: List[JobUserAssignment] = Field(default_factory=list, description="User assignments for this job")
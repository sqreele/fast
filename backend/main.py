# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin, ModelView
from pathlib import Path
import os

# Import your database engine
from database import engine

# Import your models
from models.models import (
    User, Property, Room, Machine, Topic, Procedure,
    PMSchedule, PMExecution, Issue, Inspection, PMFile,
    UserPropertyAccess, WorkOrder, Notification, MaintenanceLog, 
    Job, JobUserAssignment
)

# Import your routes
from routes import (
    admin, auth, users, properties, maintenance, 
    issues, jobs, work_orders, notifications, files, 
    maintenance_logs, migrations
)

# Create FastAPI app
app = FastAPI(
    title="PM System API",
    description="Project Management System Backend API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IMPORTANT: Create and mount static directory for SQLAdmin CSS
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)

# Mount static files - This is crucial for SQLAdmin CSS to work
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize SQLAdmin with proper configuration
admin = Admin(
    app, 
    engine,
    title="PM System Admin",
    base_url="/admin",
    # Optional: Add custom logo or branding
    # logo_url="https://example.com/logo.png",
)

# Custom Admin Views with enhanced features
class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    
    # Column configuration
    column_list = [
        User.id, 
        User.username, 
        User.email, 
        User.role, 
        User.is_active, 
        User.created_at
    ]
    column_searchable_list = [
        User.username, 
        User.email, 
        User.first_name, 
        User.last_name
    ]
    column_filters = [
        User.role, 
        User.is_active, 
        User.created_at
    ]
    column_sortable_list = [
        User.id, 
        User.username, 
        User.email,
        User.created_at
    ]
    column_default_sort = [(User.created_at, True)]
    
    # Form configuration
    form_excluded_columns = ["password_hash", "pm_schedules", "pm_executions"]
    
    # Features
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
    
    # Display settings
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class PropertyAdmin(ModelView, model=Property):
    name = "Property"
    name_plural = "Properties"
    icon = "fa-solid fa-building"
    
    column_list = [
        Property.id, 
        Property.name, 
        Property.address, 
        Property.is_active, 
        Property.created_at
    ]
    column_searchable_list = [Property.name, Property.address]
    column_filters = [Property.is_active, Property.created_at]
    column_sortable_list = [Property.id, Property.name, Property.created_at]
    form_excluded_columns = ["rooms", "user_access", "jobs"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True

class RoomAdmin(ModelView, model=Room):
    name = "Room"
    name_plural = "Rooms"
    icon = "fa-solid fa-door-open"
    
    column_list = [
        Room.id, 
        Room.name, 
        Room.room_number, 
        Room.property_id, 
        Room.is_active
    ]
    column_searchable_list = [Room.name, Room.room_number]
    column_filters = [Room.is_active, Room.property_id]
    form_excluded_columns = ["machines", "issues", "jobs"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class MachineAdmin(ModelView, model=Machine):
    name = "Machine"
    name_plural = "Machines"
    icon = "fa-solid fa-gear"
    
    column_list = [
        Machine.id, 
        Machine.name, 
        Machine.serial_number, 
        Machine.machine_type, 
        Machine.status,
        Machine.room_id
    ]
    column_searchable_list = [
        Machine.name, 
        Machine.serial_number, 
        Machine.manufacturer
    ]
    column_filters = [
        Machine.machine_type, 
        Machine.status, 
        Machine.is_active
    ]
    column_sortable_list = [
        Machine.id, 
        Machine.name, 
        Machine.installation_date
    ]
    form_excluded_columns = ["pm_schedules", "issues", "inspections", "work_orders"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True

class IssueAdmin(ModelView, model=Issue):
    name = "Issue"
    name_plural = "Issues"
    icon = "fa-solid fa-triangle-exclamation"
    
    column_list = [
        Issue.id, 
        Issue.title, 
        Issue.priority, 
        Issue.status, 
        Issue.machine_id,
        Issue.reported_at
    ]
    column_searchable_list = [Issue.title, Issue.description]
    column_filters = [Issue.status, Issue.priority, Issue.reported_at]
    column_sortable_list = [Issue.id, Issue.reported_at, Issue.priority]
    column_default_sort = [(Issue.reported_at, True)]
    form_excluded_columns = ["files"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True

class PMScheduleAdmin(ModelView, model=PMSchedule):
    name = "PM Schedule"
    name_plural = "PM Schedules"
    icon = "fa-solid fa-calendar-check"
    
    column_list = [
        PMSchedule.id, 
        PMSchedule.machine_id, 
        PMSchedule.frequency, 
        PMSchedule.next_due, 
        PMSchedule.is_active
    ]
    column_filters = [PMSchedule.frequency, PMSchedule.is_active]
    column_sortable_list = [PMSchedule.next_due, PMSchedule.last_completed]
    form_excluded_columns = ["executions"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class WorkOrderAdmin(ModelView, model=WorkOrder):
    name = "Work Order"
    name_plural = "Work Orders"
    icon = "fa-solid fa-clipboard-list"
    
    column_list = [
        WorkOrder.id, 
        WorkOrder.title, 
        WorkOrder.status, 
        WorkOrder.priority, 
        WorkOrder.created_at
    ]
    column_searchable_list = [WorkOrder.title, WorkOrder.description]
    column_filters = [
        WorkOrder.status, 
        WorkOrder.priority, 
        WorkOrder.work_order_type
    ]
    column_sortable_list = [
        WorkOrder.id, 
        WorkOrder.created_at, 
        WorkOrder.priority
    ]
    form_excluded_columns = ["files", "created_by", "assigned_to"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True

class JobAdmin(ModelView, model=Job):
    name = "Job"
    name_plural = "Jobs"
    icon = "fa-solid fa-briefcase"
    
    column_list = [
        Job.id, 
        Job.title, 
        Job.status, 
        Job.priority, 
        Job.property_id,
        Job.created_at
    ]
    column_searchable_list = [Job.title, Job.description]
    column_filters = [Job.status, Job.priority, Job.property_id]
    column_sortable_list = [Job.id, Job.created_at, Job.priority]
    form_excluded_columns = ["user_assignments", "created_by"]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class NotificationAdmin(ModelView, model=Notification):
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"
    
    column_list = [
        Notification.id,
        Notification.user_id,
        Notification.notification_type,
        Notification.title,
        Notification.is_read,
        Notification.created_at
    ]
    column_searchable_list = [Notification.title, Notification.message]
    column_filters = [
        Notification.notification_type,
        Notification.is_read,
        Notification.created_at
    ]
    column_sortable_list = [Notification.id, Notification.created_at]
    column_default_sort = [(Notification.created_at, True)]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Register all admin views
admin.add_view(UserAdmin)
admin.add_view(PropertyAdmin)
admin.add_view(RoomAdmin)
admin.add_view(MachineAdmin)
admin.add_view(IssueAdmin)
admin.add_view(PMScheduleAdmin)
admin.add_view(WorkOrderAdmin)
admin.add_view(JobAdmin)
admin.add_view(NotificationAdmin)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(users.router, prefix="/api/v1")
app.include_router(properties.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1")
app.include_router(issues.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(work_orders.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(maintenance_logs.router, prefix="/api/v1")
app.include_router(migrations.router, prefix="/api/v1/migrations", tags=["migrations"])

@app.get("/")
async def root():
    return {
        "message": "PM System API",
        "version": "1.0.0",
        "admin_url": "/admin",
        "api_docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Set to False in production
    )

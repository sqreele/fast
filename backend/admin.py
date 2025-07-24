"""
SQLAlchemy Admin configuration for PM System
"""
from sqladmin import Admin, ModelView
from models.models import (
    User, Property, Room, Machine, Topic, Procedure,
    PMSchedule, PMExecution, Issue, Inspection, PMFile, UserPropertyAccess,
    WorkOrder, Notification, MaintenanceLog, Job
)
from database import engine

# User Admin View
class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    column_list = [User.id, User.username, User.email, User.first_name, User.last_name, User.role, User.is_active]
    column_searchable_list = [User.username, User.email, User.first_name, User.last_name]
    column_sortable_list = [User.id, User.username, User.email, User.role, User.is_active, User.created_at]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Property Admin View
class PropertyAdmin(ModelView, model=Property):
    name = "Property"
    name_plural = "Properties"
    icon = "fa-solid fa-building"
    column_list = [Property.id, Property.name, Property.address, Property.is_active, Property.created_at]
    column_searchable_list = [Property.name, Property.address]
    column_sortable_list = [Property.id, Property.name, Property.is_active, Property.created_at]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Room Admin View
class RoomAdmin(ModelView, model=Room):
    name = "Room"
    name_plural = "Rooms"
    icon = "fa-solid fa-door-open"
    column_list = [Room.id, Room.name, Room.room_number, Room.property_id, Room.is_active]
    column_searchable_list = [Room.name, Room.room_number]
    column_sortable_list = [Room.id, Room.name, Room.property_id, Room.is_active]
    column_default_sort = ("id", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Machine Admin View
class MachineAdmin(ModelView, model=Machine):
    name = "Machine"
    name_plural = "Machines"
    icon = "fa-solid fa-cogs"
    column_list = [
        Machine.id, Machine.name, Machine.model, Machine.serial_number,
        Machine.machine_type, Machine.status, Machine.room_id, Machine.is_active
    ]
    column_searchable_list = [Machine.name, Machine.model, Machine.serial_number, Machine.manufacturer]
    column_sortable_list = [
        Machine.id, Machine.name, Machine.machine_type, Machine.status,
        Machine.room_id, Machine.is_active, Machine.created_at
    ]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Topic Admin View
class TopicAdmin(ModelView, model=Topic):
    name = "Topic"
    name_plural = "Topics"
    icon = "fa-solid fa-tags"
    column_list = [Topic.id, Topic.title, Topic.description, Topic.is_active, Topic.created_at]
    column_searchable_list = [Topic.title, Topic.description]
    column_sortable_list = [Topic.id, Topic.title, Topic.is_active, Topic.created_at]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Procedure Admin View
class ProcedureAdmin(ModelView, model=Procedure):
    name = "Procedure"
    name_plural = "Procedures"
    icon = "fa-solid fa-clipboard-list"
    column_list = [
        Procedure.id, Procedure.title, Procedure.topic_id,
        Procedure.estimated_minutes, Procedure.is_active
    ]
    column_searchable_list = [Procedure.title, Procedure.description]
    column_sortable_list = [
        Procedure.id, Procedure.title, Procedure.topic_id,
        Procedure.estimated_minutes, Procedure.is_active
    ]
    column_default_sort = ("id", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# PM Schedule Admin View
class PMScheduleAdmin(ModelView, model=PMSchedule):
    name = "PM Schedule"
    name_plural = "PM Schedules"
    icon = "fa-solid fa-calendar-check"
    column_list = [
        PMSchedule.id, PMSchedule.machine_id, PMSchedule.procedure_id,
        PMSchedule.user_id, PMSchedule.frequency, PMSchedule.next_due,
        PMSchedule.is_active
    ]
    column_searchable_list = []
    column_sortable_list = [
        PMSchedule.id, PMSchedule.machine_id, PMSchedule.user_id,
        PMSchedule.frequency, PMSchedule.next_due, PMSchedule.is_active
    ]
    column_default_sort = ("next_due", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# PM Execution Admin View
class PMExecutionAdmin(ModelView, model=PMExecution):
    name = "PM Execution"
    name_plural = "PM Executions"
    icon = "fa-solid fa-tasks"
    column_list = [
        PMExecution.id, PMExecution.pm_schedule_id, PMExecution.executed_by_id,
        PMExecution.status, PMExecution.started_at, PMExecution.completed_at
    ]
    column_searchable_list = []
    column_sortable_list = [
        PMExecution.id, PMExecution.pm_schedule_id, PMExecution.executed_by_id,
        PMExecution.status, PMExecution.started_at, PMExecution.completed_at
    ]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Issue Admin View
class IssueAdmin(ModelView, model=Issue):
    name = "Issue"
    name_plural = "Issues"
    icon = "fa-solid fa-exclamation-triangle"
    column_list = [
        Issue.id, Issue.title, Issue.machine_id, Issue.reported_by_id,
        Issue.assigned_to_id, Issue.priority, Issue.status, Issue.reported_at
    ]
    column_searchable_list = [Issue.title, Issue.description]
    column_sortable_list = [
        Issue.id, Issue.machine_id, Issue.priority, Issue.status,
        Issue.reported_at, Issue.resolved_at
    ]
    column_default_sort = ("reported_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Inspection Admin View
class InspectionAdmin(ModelView, model=Inspection):
    name = "Inspection"
    name_plural = "Inspections"
    icon = "fa-solid fa-search"
    column_list = [
        Inspection.id, Inspection.title, Inspection.machine_id,
        Inspection.inspector_id, Inspection.result, Inspection.inspection_date
    ]
    column_searchable_list = [Inspection.title, Inspection.findings]
    column_sortable_list = [
        Inspection.id, Inspection.machine_id, Inspection.inspector_id,
        Inspection.result, Inspection.inspection_date
    ]
    column_default_sort = ("inspection_date", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Work Order Admin View
class WorkOrderAdmin(ModelView, model=WorkOrder):
    name = "Work Order"
    name_plural = "Work Orders"
    icon = "fa-solid fa-tools"
    column_list = [
        WorkOrder.id, WorkOrder.title, WorkOrder.machine_id,
        WorkOrder.work_order_type, WorkOrder.status, WorkOrder.priority,
        WorkOrder.assigned_to_id, WorkOrder.scheduled_date
    ]
    column_searchable_list = [WorkOrder.title, WorkOrder.description]
    column_sortable_list = [
        WorkOrder.id, WorkOrder.machine_id, WorkOrder.work_order_type,
        WorkOrder.status, WorkOrder.priority, WorkOrder.scheduled_date,
        WorkOrder.created_at
    ]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Notification Admin View
class NotificationAdmin(ModelView, model=Notification):
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"
    column_list = [
        Notification.id, Notification.title, Notification.user_id,
        Notification.notification_type, Notification.is_read, Notification.created_at
    ]
    column_searchable_list = [Notification.title, Notification.message]
    column_sortable_list = [
        Notification.id, Notification.user_id, Notification.notification_type,
        Notification.is_read, Notification.created_at
    ]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Maintenance Log Admin View
class MaintenanceLogAdmin(ModelView, model=MaintenanceLog):
    name = "Maintenance Log"
    name_plural = "Maintenance Logs"
    icon = "fa-solid fa-clipboard"
    column_list = [
        MaintenanceLog.id, MaintenanceLog.title, MaintenanceLog.machine_id,
        MaintenanceLog.user_id, MaintenanceLog.log_type, MaintenanceLog.performed_at
    ]
    column_searchable_list = [MaintenanceLog.title, MaintenanceLog.description]
    column_sortable_list = [
        MaintenanceLog.id, MaintenanceLog.machine_id, MaintenanceLog.user_id,
        MaintenanceLog.log_type, MaintenanceLog.performed_at
    ]
    column_default_sort = ("performed_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# PM File Admin View
class PMFileAdmin(ModelView, model=PMFile):
    name = "PM File"
    name_plural = "PM Files"
    icon = "fa-solid fa-file"
    column_list = [
        PMFile.id, PMFile.file_name, PMFile.file_type, PMFile.image_type,
        PMFile.pm_execution_id, PMFile.issue_id, PMFile.uploaded_at
    ]
    column_searchable_list = [PMFile.file_name, PMFile.description]
    column_sortable_list = [
        PMFile.id, PMFile.file_type, PMFile.image_type, PMFile.uploaded_at
    ]
    column_default_sort = ("uploaded_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# User Property Access Admin View
class UserPropertyAccessAdmin(ModelView, model=UserPropertyAccess):
    name = "User Property Access"
    name_plural = "User Property Access"
    icon = "fa-solid fa-key"
    column_list = [
        UserPropertyAccess.user_id, UserPropertyAccess.property_id,
        UserPropertyAccess.access_level, UserPropertyAccess.granted_at,
        UserPropertyAccess.expires_at
    ]
    column_searchable_list = []
    column_sortable_list = [
        UserPropertyAccess.user_id, UserPropertyAccess.property_id,
        UserPropertyAccess.access_level, UserPropertyAccess.granted_at
    ]
    column_default_sort = ("granted_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Job Admin View
class JobAdmin(ModelView, model=Job):
    name = "Job"
    name_plural = "Jobs"
    icon = "fa-solid fa-briefcase"
    column_list = [
        Job.id, Job.title, Job.status, Job.priority, Job.property_id, Job.room_id, Job.topic_id,
        Job.created_by_id, Job.estimated_hours, Job.actual_hours, Job.started_at, Job.completed_at, Job.created_at
    ]
    column_searchable_list = [Job.title, Job.description]
    column_sortable_list = [
        Job.id, Job.title, Job.status, Job.priority, Job.property_id, Job.room_id, Job.topic_id,
        Job.created_by_id, Job.estimated_hours, Job.actual_hours, Job.started_at, Job.completed_at, Job.created_at
    ]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Create admin views list
admin_views = [
    UserAdmin,
    PropertyAdmin,
    RoomAdmin,
    MachineAdmin,
    TopicAdmin,
    ProcedureAdmin,
    PMScheduleAdmin,
    PMExecutionAdmin,
    IssueAdmin,
    InspectionAdmin,
    WorkOrderAdmin,
    NotificationAdmin,
    MaintenanceLogAdmin,
    PMFileAdmin,
    UserPropertyAccessAdmin,
    JobAdmin
] 
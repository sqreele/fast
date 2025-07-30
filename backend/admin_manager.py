"""
Admin Manager for PM System
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database import get_db
from models.models import (
    User, Property, Room, Machine, Topic, Procedure, PMSchedule, 
    PMExecution, Issue, Inspection, PMFile, UserPropertyAccess, 
    WorkOrder, Notification, MaintenanceLog, Job, UserRole
)
from routes.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)

class AdminManager:
    def __init__(self):
        self.db = next(get_db())
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = {
                "users": {
                    "total": self.db.query(User).count(),
                    "active": self.db.query(User).filter(User.is_active == True).count(),
                },
                "properties": {
                    "total": self.db.query(Property).count(),
                    "active": self.db.query(Property).filter(Property.is_active == True).count(),
                },
                "machines": {
                    "total": self.db.query(Machine).count(),
                    "active": self.db.query(Machine).filter(Machine.is_active == True).count(),
                },
                "pm_schedules": {
                    "total": self.db.query(PMSchedule).count(),
                    "overdue": self.db.query(PMSchedule).filter(
                        PMSchedule.next_due_date < datetime.utcnow()
                    ).count(),
                },
                "active_users": self.db.query(User).filter(User.is_active == True).count(),
                "active_machines": self.db.query(Machine).filter(Machine.is_active == True).count(),
                "total_pm_executions": self.db.query(PMExecution).count(),
                "completed_pm_executions": self.db.query(PMExecution).filter(
                    PMExecution.status == "COMPLETED"
                ).count(),
                "total_inspections": self.db.query(Inspection).count(),
                "failed_inspections": self.db.query(Inspection).filter(
                    Inspection.result == "FAIL"
                ).count(),
                "total_files": self.db.query(PMFile).count(),
                "system_health": "healthy",
                "last_updated": datetime.utcnow().isoformat()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def create_admin_user(self, username: str, email: str, first_name: str, last_name: str, password: str = "admin123") -> User:
        """Create an admin user"""
        try:
            # Check if admin user already exists
            existing_admin = self.db.query(User).filter(User.username == username).first()
            if existing_admin:
                logger.warning(f"Admin user {username} already exists")
                return existing_admin
            
            # Hash the password
            hashed_password = get_password_hash(password)
            
            admin_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.ADMIN,
                is_active=True,
                password_hash=hashed_password
            )
            self.db.add(admin_user)
            self.db.commit()
            self.db.refresh(admin_user)
            logger.info(f"Created admin user: {username}")
            return admin_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating admin user: {e}")
            raise
    
    def create_default_topics(self) -> List[Topic]:
        """Create default maintenance topics"""
        try:
            default_topics = [
                "HVAC Maintenance",
                "Electrical Systems",
                "Plumbing Systems",
                "Mechanical Equipment",
                "Safety Equipment",
                "Building Systems",
                "Preventive Maintenance",
                "Emergency Repairs"
            ]
            
            created_topics = []
            for topic_name in default_topics:
                existing_topic = self.db.query(Topic).filter(Topic.title == topic_name).first()
                if not existing_topic:
                    topic = Topic(
                        title=topic_name,
                        description=f"Default topic for {topic_name}",
                        is_active=True
                    )
                    self.db.add(topic)
                    created_topics.append(topic)
            
            self.db.commit()
            logger.info(f"Created {len(created_topics)} default topics")
            return created_topics
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating default topics: {e}")
            raise
    
    def create_sample_procedures(self) -> List[Procedure]:
        """Create sample maintenance procedures"""
        try:
            sample_procedures = [
                {
                    "title": "HVAC Filter Replacement",
                    "description": "Replace air filters in HVAC system",
                    "instructions": "1. Turn off HVAC system\n2. Remove old filter\n3. Install new filter\n4. Turn system back on",
                    "estimated_minutes": 30,
                    "topic_title": "HVAC Maintenance"
                },
                {
                    "title": "Electrical Panel Inspection",
                    "description": "Inspect electrical panel for safety",
                    "instructions": "1. Check for loose connections\n2. Inspect for signs of overheating\n3. Verify proper labeling\n4. Document findings",
                    "estimated_minutes": 45,
                    "topic_title": "Electrical Systems"
                },
                {
                    "title": "Plumbing Leak Check",
                    "description": "Check for plumbing leaks",
                    "instructions": "1. Inspect all visible pipes\n2. Check for water damage\n3. Test faucets and fixtures\n4. Report any issues",
                    "estimated_minutes": 60,
                    "topic_title": "Plumbing Systems"
                }
            ]
            
            created_procedures = []
            for proc_data in sample_procedures:
                # Find the topic
                topic = self.db.query(Topic).filter(Topic.title == proc_data["topic_title"]).first()
                if topic:
                    existing_proc = self.db.query(Procedure).filter(
                        Procedure.title == proc_data["title"],
                        Procedure.topic_id == topic.id
                    ).first()
                    
                    if not existing_proc:
                        procedure = Procedure(
                            topic_id=topic.id,
                            title=proc_data["title"],
                            description=proc_data["description"],
                            instructions=proc_data["instructions"],
                            estimated_minutes=proc_data["estimated_minutes"],
                            is_active=True
                        )
                        self.db.add(procedure)
                        created_procedures.append(procedure)
            
            self.db.commit()
            logger.info(f"Created {len(created_procedures)} sample procedures")
            return created_procedures
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating sample procedures: {e}")
            raise
    
    def cleanup_old_files(self, days_old: int = 90) -> int:
        """Clean up old file records"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            old_files = self.db.query(PMFile).filter(PMFile.uploaded_at < cutoff_date).all()
            
            for file_record in old_files:
                self.db.delete(file_record)
            
            self.db.commit()
            logger.info(f"Cleaned up {len(old_files)} old file records")
            return len(old_files)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up files: {e}")
            raise
    
    def deactivate_inactive_users(self, days_inactive: int = 365) -> int:
        """Deactivate users who haven't been active for specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
            inactive_users = self.db.query(User).filter(
                User.updated_at < cutoff_date,
                User.is_active == True
            ).all()
            
            for user in inactive_users:
                user.is_active = False
                user.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Deactivated {len(inactive_users)} inactive users")
            return len(inactive_users)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating users: {e}")
            raise
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            info = {
                "database_name": "pm_database",
                "total_tables": 15,  # Count of our models
                "connection_status": "connected",
                "last_backup": None,  # Would be implemented with backup system
                "size_mb": 0,  # Would be calculated from actual database
                "tables": [
                    "users", "properties", "rooms", "machines", "topics", "procedures",
                    "pm_schedules", "pm_executions", "issues", "inspections", 
                    "pm_files", "user_property_access", "work_orders", "notifications", "maintenance_logs"
                ]
            }
            return info
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)} 
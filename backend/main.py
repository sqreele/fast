from fastapi import FastAPI
from routes import users, admin, migrations, files, properties, maintenance, issues, work_orders, notifications, maintenance_logs, jobs
from database import engine, Base, create_tables
from models.models import *
from admin import admin_views
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database tables
try:
    create_tables()
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Continue anyway - tables might already exist

app = FastAPI(title="PM System API", version="1.0.0")

app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(migrations.router, prefix="/api/v1/migrations", tags=["migrations"])
app.include_router(files.router, prefix="/api/v1")
app.include_router(properties.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1")
app.include_router(issues.router, prefix="/api/v1")
app.include_router(work_orders.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(maintenance_logs.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")

# Mount SQLAlchemy Admin
from sqladmin import Admin
admin = Admin(app, engine, title="PM System Admin")

# Add all admin views
for view in admin_views:
    admin.add_view(view)

@app.get("/")
def read_root():
    return {"message": "PM System API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PM System API"}

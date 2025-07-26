from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import users, admin, migrations, files, properties, maintenance, issues, work_orders, notifications, maintenance_logs, jobs, auth
from database import engine, Base, init_database
from models.models import *
from admin import admin_views
import os
import logging
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="PM System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to track database initialization status
database_ready = False

@app.on_event("startup")
async def startup_event():
    """Initialize database in the background"""
    global database_ready
    logger.info("Starting FastAPI application...")
    
    # Start database initialization in background
    asyncio.create_task(initialize_database_background())

async def initialize_database_background():
    """Initialize database in background task"""
    global database_ready
    try:
        logger.info("Starting background database initialization...")
        await asyncio.get_event_loop().run_in_executor(None, init_database)
        database_ready = True
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't set database_ready to True, but don't crash the app

@app.get("/health")
async def health_check():
    """Health check endpoint that responds immediately"""
    return {
        "status": "healthy",
        "service": "FastAPI PM System",
        "database_ready": database_ready
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check that waits for database"""
    if not database_ready:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")
    return {
        "status": "ready",
        "service": "FastAPI PM System",
        "database_ready": database_ready
    }

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(properties.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1")
app.include_router(issues.router, prefix="/api/v1")
app.include_router(work_orders.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(maintenance_logs.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(migrations.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

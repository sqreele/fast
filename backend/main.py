from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app first
app = FastAPI(title="PM System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PM System API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PM System API"}

# Initialize everything else on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and routes on startup"""
    try:
        logger.info("Starting application initialization...")
        
        # Import routes here to avoid circular imports and database connection issues during module loading
        from routes import users, admin, migrations, files, properties, maintenance, issues, work_orders, notifications, maintenance_logs, jobs, auth
        
        # Add routers
        app.include_router(auth.router, prefix="/api/v1")
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
        
        logger.info("Routes added successfully")
        
        # Now try to initialize database
        try:
            from database import engine, Base
            import models.models  # Import the models module instead of using import *
            
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
            # Mount SQLAlchemy Admin after database is ready
            from sqladmin import Admin
            from admin import admin_views
            
            admin = Admin(app, engine, title="PM System Admin")
            
            # Add all admin views
            for view in admin_views:
                admin.add_view(view)
                
            logger.info("Admin interface initialized")
            
        except Exception as db_error:
            logger.error(f"Database initialization failed: {db_error}")
            logger.info("API will work without database features")
        
        logger.info("Application initialization completed")
        
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
        logger.info("Server will continue with minimal functionality")
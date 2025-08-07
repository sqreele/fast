from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import users, admin, migrations, files, properties, maintenance, issues, work_orders, notifications, maintenance_logs, jobs, auth
from database import engine, Base, create_tables
from models.models import *
from admin import admin_views
import os
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import time
from fastapi.responses import Response

# Configure logging
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Create database tables
try:
    create_tables()
    logger.info("Database tables created successfully")
except Exception as e:
    # Handle ENUM type already exists error
    if "duplicate key value violates unique constraint" in str(e) and "userrole" in str(e):
        logger.warning("UserRole enum type already exists, continuing...")
    else:
        logger.error(f"Error creating database tables: {e}")
        # Continue anyway - tables might already exist

app = FastAPI(title="PM System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.observe(duration)
    
    return response

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

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
"""
File management routes for PM System API
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional, Tuple
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import mimetypes
from datetime import datetime, timedelta

from database import get_db
from models.models import PMFile, PMExecution, Issue, Inspection, User, ImageType
from schemas import PMFileCreate, PMFileUpdate, PMFile as PMFileSchema, MessageResponse, PaginatedResponse
from auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

# File storage configuration
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
    'document': {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv'},
    'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv'},
    'audio': {'.mp3', '.wav', '.ogg', '.m4a'}
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)
for subdir in ['images', 'documents', 'videos', 'audio', 'temp']:
    (UPLOAD_DIR / subdir).mkdir(exist_ok=True)

def get_file_category(filename: str) -> str:
    """Determine file category based on extension"""
    ext = Path(filename).suffix.lower()
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'document'

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = Path(file.filename).suffix.lower()
    if not any(ext in exts for exts in ALLOWED_EXTENSIONS.values()):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Check file size (if available)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

def save_file(file: UploadFile, category: str) -> Tuple[str, str]:
    """Save uploaded file and return file path and filename"""
    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # Determine save path
    save_path = UPLOAD_DIR / category / unique_filename
    
    # Save file
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(save_path), unique_filename

@router.post("/upload", response_model=PMFileSchema)
async def upload_file(
    file: UploadFile = File(...),
    pm_execution_id: Optional[int] = Form(None),
    issue_id: Optional[int] = Form(None),
    inspection_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    image_type: Optional[ImageType] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file and associate it with PM execution, issue, or inspection
    """
    # Validate file
    validate_file(file)
    
    # Ensure at least one association is provided
    if not any([pm_execution_id, issue_id, inspection_id]):
        raise HTTPException(
            status_code=400, 
            detail="Must provide pm_execution_id, issue_id, or inspection_id"
        )
    
    # Validate associations exist
    if pm_execution_id:
        execution = db.query(PMExecution).filter(PMExecution.id == pm_execution_id).first()
        if not execution:
            raise HTTPException(status_code=404, detail="PM Execution not found")
    
    if issue_id:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
    
    if inspection_id:
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Determine file category and save file
    category = get_file_category(file.filename)
    file_path, unique_filename = save_file(file, category)
    
    # Create PMFile record
    pm_file = PMFile(
        pm_execution_id=pm_execution_id,
        issue_id=issue_id,
        inspection_id=inspection_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream',
        image_type=image_type if category == 'image' else None,
        description=description,
        uploaded_at=datetime.utcnow()
    )
    
    db.add(pm_file)
    db.commit()
    db.refresh(pm_file)
    
    return pm_file

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a file by ID
    """
    pm_file = db.query(PMFile).filter(PMFile.id == file_id).first()
    if not pm_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if file exists on disk
    if not os.path.exists(pm_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=pm_file.file_path,
        filename=pm_file.file_name,
        media_type=pm_file.file_type
    )

@router.get("/preview/{file_id}")
async def preview_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview a file (for images, PDFs, etc.)
    """
    pm_file = db.query(PMFile).filter(PMFile.id == file_id).first()
    if not pm_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(pm_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # For images and PDFs, return as preview
    if pm_file.file_type.startswith('image/') or pm_file.file_type == 'application/pdf':
        return FileResponse(
            path=pm_file.file_path,
            media_type=pm_file.file_type
        )
    
    # For other files, return as download
    return FileResponse(
        path=pm_file.file_path,
        filename=pm_file.file_name,
        media_type=pm_file.file_type
    )

@router.get("/", response_model=PaginatedResponse)
async def list_files(
    pm_execution_id: Optional[int] = Query(None),
    issue_id: Optional[int] = Query(None),
    inspection_id: Optional[int] = Query(None),
    file_type: Optional[str] = Query(None),
    image_type: Optional[ImageType] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List files with optional filtering
    """
    query = db.query(PMFile)
    
    # Apply filters
    if pm_execution_id:
        query = query.filter(PMFile.pm_execution_id == pm_execution_id)
    if issue_id:
        query = query.filter(PMFile.issue_id == issue_id)
    if inspection_id:
        query = query.filter(PMFile.inspection_id == inspection_id)
    if file_type:
        query = query.filter(PMFile.file_type.contains(file_type))
    if image_type:
        query = query.filter(PMFile.image_type == image_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    files = query.offset((page - 1) * size).limit(size).all()
    
    # Calculate pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=files,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{file_id}", response_model=PMFileSchema)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file details by ID
    """
    pm_file = db.query(PMFile).filter(PMFile.id == file_id).first()
    if not pm_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return pm_file

@router.put("/{file_id}", response_model=PMFileSchema)
async def update_file(
    file_id: int,
    file_update: PMFileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update file metadata
    """
    pm_file = db.query(PMFile).filter(PMFile.id == file_id).first()
    if not pm_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Update fields
    for field, value in file_update.dict(exclude_unset=True).items():
        setattr(pm_file, field, value)
    
    pm_file.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(pm_file)
    
    return pm_file

@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file and its record
    """
    pm_file = db.query(PMFile).filter(PMFile.id == file_id).first()
    if not pm_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from disk
    try:
        if os.path.exists(pm_file.file_path):
            os.remove(pm_file.file_path)
    except OSError:
        # Log error but continue with database deletion
        pass
    
    # Delete database record
    db.delete(pm_file)
    db.commit()
    
    return MessageResponse(message="File deleted successfully")

@router.post("/bulk-upload")
async def bulk_upload_files(
    files: List[UploadFile] = File(...),
    pm_execution_id: Optional[int] = Form(None),
    issue_id: Optional[int] = Form(None),
    inspection_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple files at once
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if not any([pm_execution_id, issue_id, inspection_id]):
        raise HTTPException(
            status_code=400, 
            detail="Must provide pm_execution_id, issue_id, or inspection_id"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate file
            validate_file(file)
            
            # Determine file category and save file
            category = get_file_category(file.filename)
            file_path, unique_filename = save_file(file, category)
            
            # Create PMFile record
            pm_file = PMFile(
                pm_execution_id=pm_execution_id,
                issue_id=issue_id,
                inspection_id=inspection_id,
                file_name=file.filename,
                file_path=file_path,
                file_type=file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream',
                description=None,
                uploaded_at=datetime.utcnow()
            )
            
            db.add(pm_file)
            uploaded_files.append(pm_file)
            
        except Exception as e:
            errors.append(f"Error uploading {file.filename}: {str(e)}")
    
    if uploaded_files:
        db.commit()
        for file in uploaded_files:
            db.refresh(file)
    
    return {
        "message": f"Uploaded {len(uploaded_files)} files successfully",
        "uploaded_files": uploaded_files,
        "errors": errors
    }

@router.get("/stats/summary")
async def get_file_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file statistics summary
    """
    total_files = db.query(PMFile).count()
    
    # Count by file type
    file_types = db.query(PMFile.file_type).distinct().all()
    type_counts = {}
    for file_type in file_types:
        count = db.query(PMFile).filter(PMFile.file_type == file_type[0]).count()
        type_counts[file_type[0]] = count
    
    # Count by association
    pm_execution_files = db.query(PMFile).filter(PMFile.pm_execution_id.isnot(None)).count()
    issue_files = db.query(PMFile).filter(PMFile.issue_id.isnot(None)).count()
    inspection_files = db.query(PMFile).filter(PMFile.inspection_id.isnot(None)).count()
    
    # Recent uploads
    recent_uploads = db.query(PMFile).order_by(PMFile.uploaded_at.desc()).limit(5).all()
    
    return {
        "total_files": total_files,
        "file_types": type_counts,
        "pm_execution_files": pm_execution_files,
        "issue_files": issue_files,
        "inspection_files": inspection_files,
        "recent_uploads": recent_uploads
    }

@router.post("/cleanup", response_model=MessageResponse)
async def cleanup_orphaned_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up orphaned files (files on disk without database records)
    """
    # Get all file paths from database
    db_files = db.query(PMFile.file_path).all()
    db_paths = {file[0] for file in db_files}
    
    # Find orphaned files
    orphaned_files = []
    for category_dir in UPLOAD_DIR.iterdir():
        if category_dir.is_dir() and category_dir.name != 'temp':
            for file_path in category_dir.iterdir():
                if file_path.is_file() and str(file_path) not in db_paths:
                    orphaned_files.append(str(file_path))
    
    # Delete orphaned files
    deleted_count = 0
    for file_path in orphaned_files:
        try:
            os.remove(file_path)
            deleted_count += 1
        except OSError:
            pass
    
    return MessageResponse(
        message=f"Cleaned up {deleted_count} orphaned files"
    ) 
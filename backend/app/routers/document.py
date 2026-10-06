import os
import uuid
import re
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_ROOT = os.getenv("UPLOAD_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads")))
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".csv", ".txt", ".docx", ".xlsx", ".webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

def _sanitize_filename(name: str) -> str:
    # Remove path separators and special characters
    base = os.path.basename(name)
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    return sanitized or "document"

@router.get("", response_model=PaginatedResponseModel[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    related_entity_type: Optional[str] = Query(None),
    related_entity_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    query = db.query(Document).filter(Document.business_id == current_user.business_id)
    if related_entity_type:
        query = query.filter(Document.related_entity_type == related_entity_type)
    if related_entity_id:
        query = query.filter(Document.related_entity_id == related_entity_id)

    total = query.count()
    items = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "data": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

@router.post("/upload", response_model=ResponseModel[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    related_entity_type: Optional[str] = Form(None),
    related_entity_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    original_name = file.filename or "uploaded_file"
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestException(f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Read content and enforce size check
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise BadRequestException(f"File size exceeds maximum allowed size of 10MB")

    # Secure directory structure
    safe_dir = os.path.join(UPLOAD_ROOT, current_user.business_id)
    os.makedirs(safe_dir, exist_ok=True)

    stored_file_id = str(uuid.uuid4())
    safe_name = _sanitize_filename(original_name)
    stored_filename = f"{stored_file_id}_{safe_name}"
    target_path = os.path.join(safe_dir, stored_filename)

    with open(target_path, "wb") as f:
        f.write(contents)

    doc = Document(
        business_id=current_user.business_id,
        name=name or original_name,
        document_type=document_type or "General",
        file_name=original_name,
        file_path=stored_filename,  # store relative safe file identifier
        file_size=len(contents),
        mime_type=file.content_type or "application/octet-stream",
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"data": doc}

@router.get("/{item_id}/download")
def download_document(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    doc = db.query(Document).filter(
        Document.id == item_id,
        Document.business_id == current_user.business_id
    ).first()
    if not doc:
        raise NotFoundException("Document not found")

    file_disk_path = os.path.join(UPLOAD_ROOT, current_user.business_id, doc.file_path)
    if not os.path.exists(file_disk_path):
        raise NotFoundException("Physical file not found on server")

    return FileResponse(
        path=file_disk_path,
        filename=doc.file_name,
        media_type=doc.mime_type or "application/octet-stream"
    )

@router.delete("/{item_id}")
def delete_document(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    doc = db.query(Document).filter(
        Document.id == item_id,
        Document.business_id == current_user.business_id
    ).first()
    if not doc:
        raise NotFoundException("Document not found")

    file_disk_path = os.path.join(UPLOAD_ROOT, current_user.business_id, doc.file_path)
    if os.path.exists(file_disk_path):
        try:
            os.remove(file_disk_path)
        except OSError:
            pass

    db.delete(doc)
    db.commit()
    return {"data": {"message": "Document deleted successfully", "id": item_id}}

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse
from app.schemas.base import PaginatedResponseModel

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=PaginatedResponseModel[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100)
):
    query = db.query(AuditLog, User).outerjoin(
        User, AuditLog.user_id == User.id
    ).filter(AuditLog.business_id == current_user.business_id)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))

    total = query.count()
    records = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    formatted = []
    for log, u in records:
        formatted.append({
            "id": log.id,
            "business_id": log.business_id,
            "user_id": log.user_id,
            "user_name": u.name if (u and u.name) else (u.email if u else "System"),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "metadata_info": log.metadata_info,
            "created_at": log.created_at
        })

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "data": formatted,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

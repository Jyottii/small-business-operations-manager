from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=PaginatedResponseModel[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(Notification).filter(Notification.business_id == current_user.business_id).order_by(Notification.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.post("/{item_id}/read", response_model=ResponseModel[NotificationResponse])
def mark_read(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    notif = db.query(Notification).filter(Notification.id == item_id, Notification.business_id == current_user.business_id).first()
    if not notif:
        raise NotFoundException("Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return {"data": notif}

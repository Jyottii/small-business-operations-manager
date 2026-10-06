from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.business import Business
from app.models.user import User, UserRole
from app.schemas.business import BusinessResponse, BusinessCreate, BusinessUpdate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/businesss", tags=["Businesss"])

@router.get("", response_model=PaginatedResponseModel[BusinessResponse])
def get_businesss(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(Business).filter(Business.id == current_user.business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}
    }

@router.get("/{item_id}", response_model=ResponseModel[BusinessResponse])
def get_business(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    # Enforce tenant boundary
    if item_id != current_user.business_id:
        raise NotFoundException("Business not found")
    item = db.query(Business).filter(Business.id == item_id).first()
    if not item:
        raise NotFoundException("Business not found")
    return {"data": item}

@router.post("", response_model=ResponseModel[BusinessResponse])
def create_business(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER))
):
    item_data = data.model_dump()
    item = Business(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"data": item}

@router.patch("/{item_id}", response_model=ResponseModel[BusinessResponse])
def update_business(
    item_id: str,
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER))
):
    if item_id != current_user.business_id:
        raise NotFoundException("Business not found")
    item = db.query(Business).filter(Business.id == item_id).first()
    if not item:
        raise NotFoundException("Business not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return {"data": item}

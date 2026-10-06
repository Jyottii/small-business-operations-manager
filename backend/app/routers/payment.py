from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import require_roles, get_current_actor
from app.models.user import User, UserRole
from app.models.payment import Payment
from app.schemas.payment import PaymentResponse, PaymentCreate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("", response_model=PaginatedResponseModel[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(Payment).filter(Payment.business_id == current_user.business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.post("", response_model=ResponseModel[PaymentResponse])
def create_payment(
    data: PaymentCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    actor: str = Depends(get_current_actor)
):
    try:
        payment = PaymentService.create_payment(db, current_user.business_id, data, user_id=actor)
        db.commit()
        db.refresh(payment)
        return {"data": payment}
    except Exception as e:
        db.rollback()
        raise e

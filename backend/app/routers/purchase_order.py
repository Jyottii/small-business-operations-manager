from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles, get_current_actor
from app.models.user import User, UserRole
from app.models.purchase_order import PurchaseOrder
from app.models.payment import Payment
from app.schemas.purchase_order import PurchaseOrderResponse, PurchaseOrderCreate, PurchaseOrderReceive
from app.schemas.payment import PaymentResponse, PaymentCreate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.purchase_order_service import PurchaseOrderService
from app.services.payment_service import PaymentService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

class POPaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = "Bank Transfer"
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

@router.get("", response_model=PaginatedResponseModel[PurchaseOrderResponse])
def get_pos(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(PurchaseOrder).filter(PurchaseOrder.business_id == current_user.business_id)
    if search:
        query = query.filter(PurchaseOrder.purchase_order_number.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(PurchaseOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.get("/{item_id}", response_model=ResponseModel[PurchaseOrderResponse])
def get_po(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(PurchaseOrder).filter(PurchaseOrder.id == item_id, PurchaseOrder.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Purchase Order not found")
    return {"data": item}

@router.post("", response_model=ResponseModel[PurchaseOrderResponse])
def create_po(
    data: PurchaseOrderCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    actor: str = Depends(get_current_actor)
):
    try:
        po = PurchaseOrderService.create_po(db, current_user.business_id, data, user_id=actor)
        db.commit()
        db.refresh(po)
        return {"data": po}
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{item_id}/receive", response_model=ResponseModel[PurchaseOrderResponse])
def receive_po(
    item_id: str, 
    data: PurchaseOrderReceive, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    actor: str = Depends(get_current_actor)
):
    try:
        po = PurchaseOrderService.receive_po(db, current_user.business_id, item_id, data, user_id=actor)
        db.commit()
        db.refresh(po)
        return {"data": po}
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{item_id}/cancel", response_model=ResponseModel[PurchaseOrderResponse])
def cancel_po(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    actor: str = Depends(get_current_actor)
):
    try:
        po = PurchaseOrderService.cancel_po(db, current_user.business_id, item_id, user_id=actor)
        db.commit()
        db.refresh(po)
        return {"data": po}
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{item_id}/payments", response_model=ResponseModel[PaymentResponse])
def record_po_payment(
    item_id: str, 
    data: POPaymentRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    actor: str = Depends(get_current_actor)
):
    try:
        pay_data = PaymentCreate(
            purchase_order_id=item_id,
            amount=data.amount,
            payment_method=data.payment_method,
            transaction_reference=data.transaction_reference,
            notes=data.notes
        )
        payment = PaymentService.create_payment(db, current_user.business_id, pay_data, user_id=actor)
        db.commit()
        db.refresh(payment)
        return {"data": payment}
    except Exception as e:
        db.rollback()
        raise e

@router.get("/{item_id}/payments", response_model=PaginatedResponseModel[PaymentResponse])
def get_po_payments(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    # Verify PO belongs to business
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == item_id, PurchaseOrder.business_id == current_user.business_id).first()
    if not po:
        raise NotFoundException("Purchase Order not found")
    payments = db.query(Payment).filter(Payment.purchase_order_id == item_id, Payment.business_id == current_user.business_id).order_by(Payment.payment_date.desc()).all()
    return {"data": payments, "pagination": {"page": 1, "page_size": len(payments), "total": len(payments), "total_pages": 1}}

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles, get_current_actor
from app.models.user import User, UserRole
from app.models.order import Order
from app.models.payment import Payment
from app.schemas.order import OrderResponse, OrderCreate
from app.schemas.payment import PaymentResponse, PaymentCreate
from app.schemas.return_order import ReturnCreate, ReturnResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.order_service import OrderService
from app.services.return_service import ReturnService
from app.services.payment_service import PaymentService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/orders", tags=["Orders"])

class OrderPaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = "Cash"
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

@router.get("", response_model=PaginatedResponseModel[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(Order).filter(Order.business_id == current_user.business_id)
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.get("/{item_id}", response_model=ResponseModel[OrderResponse])
def get_order(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    item = db.query(Order).filter(Order.id == item_id, Order.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Order not found")
    return {"data": item}

@router.post("", response_model=ResponseModel[OrderResponse])
def create_order(
    data: OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    actor: str = Depends(get_current_actor)
):
    try:
        order = OrderService.create_order(db, current_user.business_id, data, data.warehouse_id, user_id=actor)
        db.commit()
        db.refresh(order)
        return {"data": order}
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{item_id}/cancel", response_model=ResponseModel[OrderResponse])
def cancel_order(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    actor: str = Depends(get_current_actor)
):
    try:
        order = OrderService.cancel_order(db, current_user.business_id, item_id, user_id=actor)
        db.commit()
        db.refresh(order)
        return {"data": order}
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{item_id}/return", response_model=ResponseModel[ReturnResponse])
def return_order_items(
    item_id: str, 
    data: ReturnCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    actor: str = Depends(get_current_actor)
):
    try:
        ret = ReturnService.create_return(db, current_user.business_id, item_id, data, user_id=actor)
        db.commit()
        db.refresh(ret)
        return {"data": ret}
    except Exception as e:
        db.rollback()
        raise e

@router.get("/{item_id}/returns", response_model=PaginatedResponseModel[ReturnResponse])
def get_order_returns(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    returns = ReturnService.get_order_returns(db, current_user.business_id, item_id)
    return {"data": returns, "pagination": {"page": 1, "page_size": len(returns), "total": len(returns), "total_pages": 1}}

@router.post("/{item_id}/payments", response_model=ResponseModel[PaymentResponse])
def record_order_payment(
    item_id: str, 
    data: OrderPaymentRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    actor: str = Depends(get_current_actor)
):
    try:
        pay_data = PaymentCreate(
            order_id=item_id,
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
def get_order_payments(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    # Verify order belongs to business
    order = db.query(Order).filter(Order.id == item_id, Order.business_id == current_user.business_id).first()
    if not order:
        raise NotFoundException("Order not found")
    payments = db.query(Payment).filter(Payment.order_id == item_id, Payment.business_id == current_user.business_id).order_by(Payment.payment_date.desc()).all()
    return {"data": payments, "pagination": {"page": 1, "page_size": len(payments), "total": len(payments), "total_pages": 1}}

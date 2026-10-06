from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerUpdate
from app.schemas.order import OrderResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=PaginatedResponseModel[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(Customer).filter(Customer.business_id == current_user.business_id)
    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%") | Customer.phone.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Customer.name.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}
    }

@router.get("/{item_id}", response_model=ResponseModel[CustomerResponse])
def get_customer(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    item = db.query(Customer).filter(Customer.id == item_id, Customer.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Customer not found")
    return {"data": item}

@router.get("/{item_id}/orders", response_model=PaginatedResponseModel[OrderResponse])
def get_customer_orders(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    # Verify customer belongs to business
    cust = db.query(Customer).filter(Customer.id == item_id, Customer.business_id == current_user.business_id).first()
    if not cust:
        raise NotFoundException("Customer not found")
    query = db.query(Order).filter(Order.customer_id == item_id, Order.business_id == current_user.business_id).order_by(Order.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.post("", response_model=ResponseModel[CustomerResponse])
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    item_data = data.model_dump()
    item_data["business_id"] = current_user.business_id
    item = Customer(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"data": item}

@router.patch("/{item_id}", response_model=ResponseModel[CustomerResponse])
def update_customer(
    item_id: str,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(Customer).filter(Customer.id == item_id, Customer.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Customer not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return {"data": item}

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.schemas.supplier import SupplierResponse, SupplierCreate, SupplierUpdate
from app.schemas.purchase_order import PurchaseOrderResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.get("", response_model=PaginatedResponseModel[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(Supplier).filter(Supplier.business_id == current_user.business_id)
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%") | Supplier.company_name.ilike(f"%{search}%") | Supplier.email.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Supplier.name.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}
    }

@router.get("/{item_id}", response_model=ResponseModel[SupplierResponse])
def get_supplier(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(Supplier).filter(Supplier.id == item_id, Supplier.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Supplier not found")
    return {"data": item}

@router.get("/{item_id}/purchase-orders", response_model=PaginatedResponseModel[PurchaseOrderResponse])
def get_supplier_pos(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    # Verify supplier belongs to business
    supp = db.query(Supplier).filter(Supplier.id == item_id, Supplier.business_id == current_user.business_id).first()
    if not supp:
        raise NotFoundException("Supplier not found")
    query = db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == item_id, PurchaseOrder.business_id == current_user.business_id).order_by(PurchaseOrder.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.post("", response_model=ResponseModel[SupplierResponse])
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item_data = data.model_dump()
    item_data["business_id"] = current_user.business_id
    item = Supplier(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"data": item}

@router.patch("/{item_id}", response_model=ResponseModel[SupplierResponse])
def update_supplier(
    item_id: str,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(Supplier).filter(Supplier.id == item_id, Supplier.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Supplier not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return {"data": item}

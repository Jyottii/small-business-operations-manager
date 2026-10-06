from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.warehouse import (
    WarehouseResponse, 
    WarehouseCreate, 
    WarehouseUpdate, 
    WarehouseSummaryResponse
)
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

@router.get("", response_model=PaginatedResponseModel[WarehouseResponse])
def get_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    branch_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    query = db.query(Warehouse).filter(Warehouse.business_id == current_user.business_id)
    if branch_id:
        query = query.filter(Warehouse.branch_id == branch_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items, 
        "pagination": {
            "page": page, 
            "page_size": page_size, 
            "total": total, 
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    }

@router.get("/{item_id}/summary", response_model=ResponseModel[WarehouseSummaryResponse])
def get_warehouse_summary(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    wh = db.query(Warehouse).filter(
        Warehouse.id == item_id, 
        Warehouse.business_id == current_user.business_id
    ).first()
    if not wh:
        raise NotFoundException("Warehouse not found")

    # Aggregate inventory for this warehouse
    inv_records = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.warehouse_id == item_id,
        Product.business_id == current_user.business_id
    ).all()

    total_products = len(inv_records)
    total_stock = 0
    total_valuation = 0.0
    low_stock_count = 0
    out_of_stock_count = 0

    for inv, prod in inv_records:
        qty = float(inv.quantity or 0)
        cost = float(prod.cost_price or 0)
        reorder = float(inv.reorder_level if inv.reorder_level is not None and inv.reorder_level > 0 else (prod.reorder_level or 0))

        total_stock += int(qty)
        total_valuation += (qty * cost)

        if qty <= 0:
            out_of_stock_count += 1
        elif qty <= reorder:
            low_stock_count += 1

    return {
        "data": {
            "warehouse": wh,
            "total_products": total_products,
            "total_stock": total_stock,
            "total_valuation": round(total_valuation, 2),
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count
        }
    }

@router.get("/{item_id}", response_model=ResponseModel[WarehouseResponse])
def get_warehouse(
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    wh = db.query(Warehouse).filter(Warehouse.id == item_id, Warehouse.business_id == current_user.business_id).first()
    if not wh:
        raise NotFoundException("Warehouse not found")
    return {"data": wh}

@router.post("", response_model=ResponseModel[WarehouseResponse])
def create_warehouse(
    data: WarehouseCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))
):
    wh_data = data.model_dump()
    wh_data["business_id"] = current_user.business_id
    wh = Warehouse(**wh_data)
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return {"data": wh}

@router.put("/{item_id}", response_model=ResponseModel[WarehouseResponse])
def update_warehouse(
    item_id: str,
    data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    wh = db.query(Warehouse).filter(
        Warehouse.id == item_id,
        Warehouse.business_id == current_user.business_id
    ).first()
    if not wh:
        raise NotFoundException("Warehouse not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wh, key, value)

    db.commit()
    db.refresh(wh)
    return {"data": wh}

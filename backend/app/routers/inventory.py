from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles, get_current_actor
from app.models.user import User, UserRole
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.schemas.inventory import InventoryResponse, InventoryAdjust
from app.schemas.stock_movement import StockMovementResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=PaginatedResponseModel[InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(Inventory).join(Product).filter(Product.business_id == current_user.business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.get("/low-stock", response_model=PaginatedResponseModel[InventoryResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(Inventory).join(Product).filter(
        Product.business_id == current_user.business_id,
        Inventory.quantity <= Inventory.reorder_level
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.get("/movements", response_model=PaginatedResponseModel[StockMovementResponse])
def get_stock_movements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(StockMovement).filter(StockMovement.business_id == current_user.business_id).order_by(StockMovement.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

@router.post("/adjust", response_model=ResponseModel[InventoryResponse])
def adjust_inventory(
    data: InventoryAdjust, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)),
    actor: str = Depends(get_current_actor)
):
    try:
        inv = InventoryService.adjust_stock(
            db=db, 
            business_id=current_user.business_id, 
            product_id=data.product_id, 
            warehouse_id=data.warehouse_id, 
            quantity_change=data.quantity_change, 
            movement_type=data.movement_type, 
            notes=data.notes, 
            user_id=actor
        )
        db.commit()
        db.refresh(inv)
        return {"data": inv}
    except Exception as e:
        db.rollback()
        raise e

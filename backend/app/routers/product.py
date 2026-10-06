from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.schemas.inventory import InventoryResponse
from app.schemas.stock_movement import StockMovementResponse
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=PaginatedResponseModel[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(Product).filter(Product.business_id == current_user.business_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Product.name.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}
    }

@router.get("/barcode/{barcode}", response_model=ResponseModel[ProductResponse])
def get_product_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    item = db.query(Product).filter(
        Product.barcode == barcode.strip(),
        Product.business_id == current_user.business_id
    ).first()
    if not item:
        raise NotFoundException(f"No product found with barcode '{barcode}'")
    return {"data": item}

@router.get("/{item_id}", response_model=ResponseModel[ProductResponse])
def get_product(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    item = db.query(Product).filter(Product.id == item_id, Product.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Product not found")
    return {"data": item}

@router.post("", response_model=ResponseModel[ProductResponse])
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item_data = data.model_dump()
    item_data["business_id"] = current_user.business_id
    item = Product(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"data": item}

@router.patch("/{item_id}", response_model=ResponseModel[ProductResponse])
def update_product(
    item_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    item = db.query(Product).filter(Product.id == item_id, Product.business_id == current_user.business_id).first()
    if not item:
        raise NotFoundException("Product not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return {"data": item}

@router.get("/{item_id}/inventory", response_model=PaginatedResponseModel[InventoryResponse])
def get_product_inventory(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    # Verify product belongs to user's business
    prod = db.query(Product).filter(Product.id == item_id, Product.business_id == current_user.business_id).first()
    if not prod:
        raise NotFoundException("Product not found")
    items = db.query(Inventory).filter(Inventory.product_id == item_id).all()
    return {"data": items, "pagination": {"page": 1, "page_size": len(items), "total": len(items), "total_pages": 1}}

@router.get("/{item_id}/stock-movements", response_model=PaginatedResponseModel[StockMovementResponse])
def get_product_stock_movements(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(StockMovement).filter(
        StockMovement.product_id == item_id,
        StockMovement.business_id == current_user.business_id
    ).order_by(StockMovement.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size if total > 0 else 1}}

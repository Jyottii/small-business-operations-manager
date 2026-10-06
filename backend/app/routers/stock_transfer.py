import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.stock_transfer import StockTransfer, StockTransferItem, StockTransferStatus
from app.schemas.stock_transfer import (
    StockTransferResponse,
    StockTransferCreate,
    StockTransferStatusUpdate,
    StockTransferItemResponse
)
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/stock-transfers", tags=["Stock Transfers"])

def _format_transfer_response(transfer: StockTransfer, db: Session) -> dict:
    source_wh = db.query(Warehouse).filter(Warehouse.id == transfer.source_warehouse_id).first()
    dest_wh = db.query(Warehouse).filter(Warehouse.id == transfer.destination_warehouse_id).first()
    
    items_data = []
    for item in transfer.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        items_data.append({
            "id": item.id,
            "transfer_id": item.transfer_id,
            "product_id": item.product_id,
            "quantity": float(item.quantity),
            "product_name": prod.name if prod else None,
            "product_sku": prod.sku if prod else None
        })
        
    return {
        "id": transfer.id,
        "business_id": transfer.business_id,
        "transfer_number": transfer.transfer_number,
        "source_warehouse_id": transfer.source_warehouse_id,
        "destination_warehouse_id": transfer.destination_warehouse_id,
        "source_warehouse_name": source_wh.name if source_wh else None,
        "destination_warehouse_name": dest_wh.name if dest_wh else None,
        "status": transfer.status,
        "notes": transfer.notes,
        "created_by": transfer.created_by,
        "requested_date": transfer.requested_date,
        "shipped_date": transfer.shipped_date,
        "received_date": transfer.received_date,
        "created_at": transfer.created_at,
        "updated_at": transfer.updated_at,
        "items": items_data
    }

@router.get("", response_model=PaginatedResponseModel[StockTransferResponse])
def get_stock_transfers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    warehouse_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query(StockTransfer).filter(StockTransfer.business_id == current_user.business_id)
    if warehouse_id:
        query = query.filter(
            or_(
                StockTransfer.source_warehouse_id == warehouse_id,
                StockTransfer.destination_warehouse_id == warehouse_id
            )
        )
    if status_filter:
        query = query.filter(StockTransfer.status.ilike(status_filter))
        
    total = query.count()
    records = query.order_by(StockTransfer.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    formatted = [_format_transfer_response(t, db) for t in records]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "data": formatted,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

@router.get("/{item_id}", response_model=ResponseModel[StockTransferResponse])
def get_stock_transfer(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))
):
    transfer = db.query(StockTransfer).filter(
        StockTransfer.id == item_id,
        StockTransfer.business_id == current_user.business_id
    ).first()
    if not transfer:
        raise NotFoundException("Stock transfer not found")
        
    return {"data": _format_transfer_response(transfer, db)}

@router.post("", response_model=ResponseModel[StockTransferResponse], status_code=status.HTTP_201_CREATED)
def create_stock_transfer(
    data: StockTransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    if data.source_warehouse_id == data.destination_warehouse_id:
        raise BadRequestException("Source and destination warehouses must be different")
        
    source_wh = db.query(Warehouse).filter(
        Warehouse.id == data.source_warehouse_id,
        Warehouse.business_id == current_user.business_id
    ).first()
    if not source_wh:
        raise BadRequestException("Source warehouse not found")
        
    dest_wh = db.query(Warehouse).filter(
        Warehouse.id == data.destination_warehouse_id,
        Warehouse.business_id == current_user.business_id
    ).first()
    if not dest_wh:
        raise BadRequestException("Destination warehouse not found")

    if not data.items:
        raise BadRequestException("At least one product item is required for transfer")

    today_str = datetime.utcnow().strftime("%Y%m%d")
    count_today = db.query(StockTransfer).filter(
        StockTransfer.business_id == current_user.business_id,
        StockTransfer.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count() + 1
    transfer_number = f"TRF-{today_str}-{count_today:04d}"

    transfer = StockTransfer(
        business_id=current_user.business_id,
        transfer_number=transfer_number,
        source_warehouse_id=data.source_warehouse_id,
        destination_warehouse_id=data.destination_warehouse_id,
        status=StockTransferStatus.PENDING.value,
        requested_date=datetime.utcnow(),
        notes=data.notes,
        created_by=current_user.id
    )
    db.add(transfer)
    db.flush()

    for item_data in data.items:
        if item_data.quantity <= 0:
            raise BadRequestException("Item quantity must be greater than zero")
            
        prod = db.query(Product).filter(
            Product.id == item_data.product_id,
            Product.business_id == current_user.business_id
        ).first()
        if not prod:
            raise BadRequestException(f"Product '{item_data.product_id}' not found")

        item = StockTransferItem(
            transfer_id=transfer.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(item)

    db.commit()
    db.refresh(transfer)
    return {"data": _format_transfer_response(transfer, db)}

@router.post("/{item_id}/status", response_model=ResponseModel[StockTransferResponse])
def update_stock_transfer_status(
    item_id: str,
    status_update: StockTransferStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER))
):
    transfer = db.query(StockTransfer).filter(
        StockTransfer.id == item_id,
        StockTransfer.business_id == current_user.business_id
    ).first()
    if not transfer:
        raise NotFoundException("Stock transfer not found")

    input_status = status_update.status.strip().title()
    valid_statuses = [s.value for s in StockTransferStatus]
    matched_status = None
    for s in valid_statuses:
        if s.lower() == input_status.lower():
            matched_status = s
            break

    if not matched_status:
        raise BadRequestException(f"Invalid status: '{status_update.status}'. Allowed: {', '.join(valid_statuses)}")

    if transfer.status in [StockTransferStatus.COMPLETED.value, StockTransferStatus.CANCELLED.value]:
        raise BadRequestException(f"Cannot change status of a {transfer.status.lower()} transfer")

    if matched_status == StockTransferStatus.IN_TRANSIT.value:
        transfer.status = StockTransferStatus.IN_TRANSIT.value
        transfer.shipped_date = datetime.utcnow()
        if status_update.notes:
            transfer.notes = (transfer.notes or "") + f"\n[In Transit]: {status_update.notes}"

    elif matched_status == StockTransferStatus.CANCELLED.value:
        transfer.status = StockTransferStatus.CANCELLED.value
        if status_update.notes:
            transfer.notes = (transfer.notes or "") + f"\n[Cancelled]: {status_update.notes}"

    elif matched_status == StockTransferStatus.COMPLETED.value:
        # Check source inventory availability for all items first
        for item in transfer.items:
            source_inv = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == transfer.source_warehouse_id
            ).first()

            available_qty = float(source_inv.quantity) if source_inv else 0.0
            transfer_qty = float(item.quantity)

            if available_qty < transfer_qty:
                prod = db.query(Product).filter(Product.id == item.product_id).first()
                name = prod.name if prod else item.product_id
                raise BadRequestException(
                    f"Insufficient stock for '{name}' at source warehouse. Available: {available_qty}, required: {transfer_qty}"
                )

        # Apply deductions and additions
        for item in transfer.items:
            transfer_qty = float(item.quantity)
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            cost_price = float(prod.cost_price or 0.0) if prod else 0.0

            # 1. Source warehouse deduction
            source_inv = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == transfer.source_warehouse_id
            ).first()
            prev_src_qty = float(source_inv.quantity)
            res_src_qty = prev_src_qty - transfer_qty
            source_inv.quantity = res_src_qty
            source_inv.last_stock_update = datetime.utcnow()

            out_movement = StockMovement(
                business_id=current_user.business_id,
                product_id=item.product_id,
                warehouse_id=transfer.source_warehouse_id,
                movement_type="TRANSFER_OUT",
                quantity=-transfer_qty,
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id,
                previous_quantity=prev_src_qty,
                resulting_quantity=res_src_qty,
                unit_cost=cost_price,
                notes=f"Stock transfer {transfer.transfer_number} to destination"
            )
            db.add(out_movement)

            # 2. Destination warehouse addition
            dest_inv = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == transfer.destination_warehouse_id
            ).first()

            if not dest_inv:
                dest_inv = Inventory(
                    product_id=item.product_id,
                    warehouse_id=transfer.destination_warehouse_id,
                    quantity=0.0,
                    reserved_quantity=0.0
                )
                db.add(dest_inv)
                db.flush()

            prev_dest_qty = float(dest_inv.quantity or 0.0)
            res_dest_qty = prev_dest_qty + transfer_qty
            dest_inv.quantity = res_dest_qty
            dest_inv.last_stock_update = datetime.utcnow()

            in_movement = StockMovement(
                business_id=current_user.business_id,
                product_id=item.product_id,
                warehouse_id=transfer.destination_warehouse_id,
                movement_type="TRANSFER_IN",
                quantity=transfer_qty,
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id,
                previous_quantity=prev_dest_qty,
                resulting_quantity=res_dest_qty,
                unit_cost=cost_price,
                notes=f"Stock transfer {transfer.transfer_number} from source"
            )
            db.add(in_movement)

        transfer.status = StockTransferStatus.COMPLETED.value
        transfer.received_date = datetime.utcnow()
        if status_update.notes:
            transfer.notes = (transfer.notes or "") + f"\n[Completed]: {status_update.notes}"

    db.commit()
    db.refresh(transfer)
    return {"data": _format_transfer_response(transfer, db)}

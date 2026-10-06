from sqlalchemy.orm import Session
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderReceive
from app.services.inventory_service import InventoryService
from app.services.system_service import AuditService, NotificationService
from app.core.exceptions import NotFoundException, BadRequestException
import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional

class PurchaseOrderService:
    @staticmethod
    def create_po(db: Session, business_id: str, po_data: PurchaseOrderCreate, user_id: str = "SYSTEM") -> PurchaseOrder:
        if not po_data.items:
            raise BadRequestException("Purchase Order must contain at least one item")
            
        po = PurchaseOrder(
            business_id=business_id,
            supplier_id=po_data.supplier_id,
            warehouse_id=po_data.warehouse_id,
            purchase_order_number=f"PO-{uuid.uuid4().hex[:8].upper()}",
            status="Ordered",
            expected_date=po_data.expected_date,
            notes=po_data.notes,
            order_date=datetime.utcnow()
        )
        db.add(po)
        db.flush()
        
        subtotal = Decimal('0.0')
        for item in po_data.items:
            product = db.query(Product).filter(Product.id == item.product_id, Product.business_id == business_id).first()
            if not product:
                raise NotFoundException(f"Product {item.product_id} not found")
                
            line_total = item.unit_cost * item.quantity_ordered
            poi = PurchaseOrderItem(
                purchase_order_id=po.id,
                product_id=product.id,
                quantity_ordered=item.quantity_ordered,
                quantity_received=0,
                unit_cost=item.unit_cost,
                line_total=line_total
            )
            db.add(poi)
            subtotal += line_total
            
        po.subtotal = subtotal
        po.total = subtotal
        po.balance_due = subtotal
        
        supplier = db.query(Supplier).filter(Supplier.id == po.supplier_id).first()
        if supplier:
            supplier.outstanding_balance = (supplier.outstanding_balance or Decimal('0.0')) + po.total
            
        db.flush()
        AuditService.log(db, business_id, "PURCHASE_ORDER_CREATED", "PurchaseOrder", po.id, f"PO {po.purchase_order_number} created for ${po.total:.2f}", user_id=user_id)
        NotificationService.notify(db, business_id, "PO Created", f"Purchase Order {po.purchase_order_number} created.", "INFO", "PurchaseOrder", po.id, user_id=user_id)
        return po

    @staticmethod
    def receive_po(db: Session, business_id: str, po_id: str, receive_data: PurchaseOrderReceive, user_id: str = "SYSTEM") -> PurchaseOrder:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.business_id == business_id).first()
        if not po:
            raise NotFoundException("Purchase Order not found")
            
        if po.status in ["Received", "Cancelled"]:
            raise BadRequestException(f"Cannot receive goods for PO with status '{po.status}'")
            
        for product_id, qty_to_receive in receive_data.items.items():
            qty_to_receive = Decimal(str(qty_to_receive))
            if qty_to_receive <= 0:
                continue
                
            poi = db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.purchase_order_id == po.id,
                PurchaseOrderItem.product_id == product_id
            ).first()
            
            if not poi:
                raise NotFoundException(f"Product {product_id} is not part of this purchase order")
                
            already_received = poi.quantity_received or Decimal('0.0')
            remaining = poi.quantity_ordered - already_received
            if qty_to_receive > remaining:
                raise BadRequestException(f"Cannot receive {qty_to_receive} for product {product_id}. Only {remaining} units remaining.")
                
            poi.quantity_received = already_received + qty_to_receive
            
            InventoryService.adjust_stock(
                db=db,
                business_id=business_id,
                product_id=product_id,
                warehouse_id=po.warehouse_id,
                quantity_change=qty_to_receive,
                movement_type="PURCHASE_RECEIPT",
                reference_type="PURCHASE_ORDER",
                reference_id=po.id,
                notes=receive_data.notes or f"Received for PO {po.purchase_order_number}",
                user_id=user_id
            )
            
        # Recompute status
        all_items = po.purchase_items
        is_fully_received = all((i.quantity_received or Decimal('0')) >= i.quantity_ordered for i in all_items)
        has_partial = any((i.quantity_received or Decimal('0')) > 0 for i in all_items)
        
        if is_fully_received:
            po.status = "Received"
        elif has_partial:
            po.status = "Partially Received"
            
        db.flush()
        
        AuditService.log(db, business_id, "PURCHASE_ORDER_RECEIVED", "PurchaseOrder", po.id, f"Received goods for PO {po.purchase_order_number}. New status: {po.status}", user_id=user_id)
        NotificationService.notify(db, business_id, "Goods Received", f"Goods received for PO {po.purchase_order_number} ({po.status}).", "SUCCESS", "PurchaseOrder", po.id, user_id=user_id)
            
        return po

    @staticmethod
    def cancel_po(db: Session, business_id: str, po_id: str, user_id: str = "SYSTEM") -> PurchaseOrder:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.business_id == business_id).first()
        if not po:
            raise NotFoundException("Purchase Order not found")
        if po.status == "Cancelled":
            raise BadRequestException("Purchase Order is already cancelled")
        if po.status == "Received":
            raise BadRequestException("Cannot cancel a fully received Purchase Order")
        if any((item.quantity_received or Decimal('0')) > 0 for item in po.purchase_items):
            raise BadRequestException("Cannot cancel a Purchase Order that has already received partial goods")
            
        supplier = db.query(Supplier).filter(Supplier.id == po.supplier_id).first()
        if supplier and po.balance_due > 0:
            supplier.outstanding_balance = max(Decimal('0.0'), (supplier.outstanding_balance or Decimal('0.0')) - po.balance_due)
            
        po.status = "Cancelled"
        po.balance_due = Decimal('0.0')
        db.flush()
        AuditService.log(db, business_id, "PURCHASE_ORDER_CANCELLED", "PurchaseOrder", po.id, f"PO {po.purchase_order_number} cancelled", user_id=user_id)
        NotificationService.notify(db, business_id, "PO Cancelled", f"PO {po.purchase_order_number} was cancelled.", "WARNING", "PurchaseOrder", po.id, user_id=user_id)
        return po

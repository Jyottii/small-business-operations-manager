from sqlalchemy.orm import Session
from app.models.return_order import Return, ReturnItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.schemas.return_order import ReturnCreate
from app.services.inventory_service import InventoryService
from app.services.system_service import AuditService, NotificationService
from app.core.exceptions import NotFoundException, BadRequestException
import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Optional

class ReturnService:
    @staticmethod
    def create_return(db: Session, business_id: str, order_id: str, return_data: ReturnCreate, user_id: str = "SYSTEM") -> Return:
        order = db.query(Order).filter(Order.id == order_id, Order.business_id == business_id).first()
        if not order:
            raise NotFoundException("Order not found")
            
        if order.status == "Cancelled":
            raise BadRequestException("Cannot return items from a cancelled order")
            
        if not return_data.items:
            raise BadRequestException("At least one item must be specified for return")

        ret = Return(
            business_id=business_id,
            order_id=order.id,
            return_number=f"RET-{uuid.uuid4().hex[:8].upper()}",
            status="Processed",
            notes=return_data.notes,
            return_date=datetime.utcnow()
        )
        db.add(ret)
        db.flush()
        
        total_refund = Decimal('0.0')
        
        for item in return_data.items:
            qty_to_return = Decimal(str(item.quantity))
            if qty_to_return <= 0:
                continue
                
            oi = db.query(OrderItem).filter(OrderItem.order_id == order.id, OrderItem.product_id == item.product_id).first()
            if not oi:
                raise BadRequestException(f"Product {item.product_id} is not part of this order")
                
            # Check previously returned qty for this order item
            already_returned = sum(
                (ri.quantity or Decimal('0'))
                for ri in db.query(ReturnItem).filter(ReturnItem.order_item_id == oi.id).all()
            )
            
            if already_returned + qty_to_return > oi.quantity:
                remaining_returnable = oi.quantity - already_returned
                raise BadRequestException(f"Cannot return {qty_to_return} units. Only {remaining_returnable} units eligible for return.")
                
            unit_price = oi.unit_price or Decimal('0.0')
            refund_amount = unit_price * qty_to_return
            
            ri = ReturnItem(
                return_id=ret.id,
                order_item_id=oi.id,
                product_id=item.product_id,
                quantity=qty_to_return,
                refund_amount=refund_amount,
                reason=item.reason or "Customer Return"
            )
            db.add(ri)
            total_refund += refund_amount
            
            # Find warehouse for product inventory
            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            wh_id = inv.warehouse_id if inv else None
            if not wh_id:
                from app.models.warehouse import Warehouse
                wh = db.query(Warehouse).filter(Warehouse.business_id == business_id).first()
                wh_id = wh.id if wh else "default-wh"
                
            InventoryService.adjust_stock(
                db=db,
                business_id=business_id,
                product_id=item.product_id,
                warehouse_id=wh_id,
                quantity_change=qty_to_return,
                movement_type="RETURN",
                reference_type="RETURN",
                reference_id=ret.id,
                notes=f"Return {ret.return_number} for Order {order.order_number}"
            )
            
        ret.refund_amount = total_refund
        
        # Adjust customer balance / order balance
        if order.balance_due >= total_refund:
            order.balance_due -= total_refund
            if order.customer_id:
                customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
                if customer:
                    customer.outstanding_balance = max(Decimal('0.0'), (customer.outstanding_balance or Decimal('0.0')) - total_refund)
        else:
            diff = total_refund - order.balance_due
            order.balance_due = Decimal('0.0')
            if order.customer_id:
                customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
                if customer:
                    customer.outstanding_balance = max(Decimal('0.0'), (customer.outstanding_balance or Decimal('0.0')) - total_refund)

        db.flush()
        AuditService.log(db, business_id, "RETURN_PROCESSED", "Return", ret.id, f"Return {ret.return_number} processed for Order {order.order_number} (${total_refund:.2f})", user_id=user_id)
        NotificationService.notify(db, business_id, "Return Processed", f"Return {ret.return_number} processed for Order {order.order_number} (${total_refund:.2f}).", "INFO", "Return", ret.id, user_id=user_id)
        return ret

    @staticmethod
    def get_order_returns(db: Session, business_id: str, order_id: str) -> List[Return]:
        return db.query(Return).filter(Return.order_id == order_id, Return.business_id == business_id).all()

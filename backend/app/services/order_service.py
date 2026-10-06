from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.schemas.order import OrderCreate
from app.services.inventory_service import InventoryService
from app.services.system_service import AuditService, NotificationService
from app.core.exceptions import NotFoundException, BadRequestException
import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional

class OrderService:
    @staticmethod
    def create_order(db: Session, business_id: str, order_data: OrderCreate, warehouse_id: Optional[str] = None, user_id: str = "SYSTEM") -> Order:
        if not order_data.items:
            raise BadRequestException("Order must contain at least one item")
            
        # Determine warehouse
        wh_id = warehouse_id or order_data.warehouse_id
        if not wh_id:
            wh = db.query(Warehouse).filter(Warehouse.business_id == business_id).first()
            if wh:
                wh_id = wh.id
            else:
                raise BadRequestException("No warehouse found. Please configure a warehouse first.")
                
        customer = db.query(Customer).filter(Customer.id == order_data.customer_id, Customer.business_id == business_id).first() if order_data.customer_id else None
        
        # Pre-validate inventory for all items before any changes
        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id, Product.business_id == business_id).first()
            if not product:
                raise NotFoundException(f"Product {item.product_id} not found")
            
            inv = InventoryService.get_inventory(db, business_id, product.id, wh_id)
            available = inv.quantity if inv else Decimal('0')
            if available < item.quantity:
                raise BadRequestException(f"Insufficient stock for Product '{product.name}'. Available: {available}, Requested: {item.quantity}")

        order = Order(
            business_id=business_id,
            customer_id=order_data.customer_id,
            employee_id=order_data.employee_id,
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            status="Completed",
            payment_status="Unpaid",
            notes=order_data.notes,
            order_date=datetime.utcnow()
        )
        db.add(order)
        db.flush()
        
        subtotal = Decimal('0.0')
        total_tax = Decimal('0.0')
        total_discount = Decimal('0.0')
        
        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id, Product.business_id == business_id).first()
                
            # Deduct inventory & create stock movement
            InventoryService.adjust_stock(
                db=db,
                business_id=business_id,
                product_id=product.id,
                warehouse_id=wh_id,
                quantity_change=-item.quantity,
                movement_type="SALE",
                reference_type="ORDER",
                reference_id=order.id,
                notes=f"Sale {order.order_number}"
            )
                
            item_quantity = Decimal(str(item.quantity))
            item_discount = Decimal(str(item.discount or 0.0))
            line_price = Decimal(str(product.selling_price or 0.0))
            line_tax_rate = Decimal(str(product.tax_rate or 0.0))
            
            tax_amount = (line_price * item_quantity - item_discount) * (line_tax_rate / Decimal('100.0'))
            line_total = (line_price * item_quantity) - item_discount + tax_amount
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_quantity,
                unit_price=line_price,
                discount=item_discount,
                tax_rate=line_tax_rate,
                tax_amount=tax_amount,
                line_total=line_total
            )
            db.add(order_item)
            
            subtotal += (line_price * item_quantity)
            total_discount += item_discount
            total_tax += tax_amount
            
        order.subtotal = subtotal
        order.discount = total_discount
        order.tax = total_tax
        order.total = subtotal - total_discount + total_tax
        order.balance_due = order.total
        
        if customer:
            if customer.credit_limit and customer.credit_limit > 0 and ((customer.outstanding_balance or Decimal('0')) + order.balance_due) > customer.credit_limit:
                raise BadRequestException(f"Customer credit limit exceeded. Limit: {customer.credit_limit}, Current Balance: {customer.outstanding_balance or 0}, Order: {order.balance_due}")
            customer.outstanding_balance = (customer.outstanding_balance or Decimal('0')) + order.balance_due
        
        db.flush()
        AuditService.log(db, business_id, "ORDER_CREATED", "Order", order.id, f"Order {order.order_number} created for ${order.total:.2f}", user_id=user_id)
        NotificationService.notify(db, business_id, "Order Completed", f"Order {order.order_number} has been created for ${order.total:.2f}.", "SUCCESS", "Order", order.id, user_id=user_id)
        
        return order

    @staticmethod
    def cancel_order(db: Session, business_id: str, order_id: str, warehouse_id: Optional[str] = None, user_id: str = "SYSTEM") -> Order:
        order = db.query(Order).filter(Order.id == order_id, Order.business_id == business_id).first()
        if not order:
            raise NotFoundException("Order not found")
        if order.status == "Cancelled":
            raise BadRequestException("Order is already cancelled")
        
        # Restore inventory
        for item in order.order_items:
            wh_id = warehouse_id
            if not wh_id:
                inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
                wh_id = inv.warehouse_id if inv else None
            if not wh_id:
                wh = db.query(Warehouse).filter(Warehouse.business_id == business_id).first()
                wh_id = wh.id if wh else "default-wh"
                
            InventoryService.adjust_stock(
                db=db,
                business_id=business_id,
                product_id=item.product_id,
                warehouse_id=wh_id,
                quantity_change=item.quantity,
                movement_type="CANCELLATION",
                reference_type="ORDER_CANCEL",
                reference_id=order.id,
                notes=f"Order {order.order_number} cancelled",
                user_id=user_id
            )
            
        # Reverse customer balance due if unpaid
        if order.customer_id:
            customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
            if customer and order.balance_due > 0:
                customer.outstanding_balance = max(Decimal('0.0'), (customer.outstanding_balance or Decimal('0.0')) - order.balance_due)
                
        order.status = "Cancelled"
        order.balance_due = Decimal('0.0')
        db.flush()
        AuditService.log(db, business_id, "ORDER_CANCELLED", "Order", order.id, f"Order {order.order_number} cancelled and inventory restored", user_id=user_id)
        NotificationService.notify(db, business_id, "Order Cancelled", f"Order {order.order_number} was cancelled.", "WARNING", "Order", order.id, user_id=user_id)
        return order

from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.core.exceptions import NotFoundException, BadRequestException
from decimal import Decimal
from app.services.system_service import AuditService, NotificationService

class InventoryService:
    @staticmethod
    def get_inventory(db: Session, business_id: str, product_id: str, warehouse_id: str):
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        return inv

    @staticmethod
    def adjust_stock(db: Session, business_id: str, product_id: str, warehouse_id: str, quantity_change: Decimal, movement_type: str, reference_type: str = None, reference_id: str = None, notes: str = None, user_id: str = "SYSTEM") -> Inventory:
        inv = InventoryService.get_inventory(db, business_id, product_id, warehouse_id)
        if not inv:
            inv = Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity=0, reorder_level=0, reorder_quantity=0)
            db.add(inv)
        
        prev_qty = inv.quantity
        new_qty = prev_qty + quantity_change
        
        if new_qty < 0:
            raise BadRequestException(f"Insufficient stock for product {product_id}. Available: {prev_qty}, Requested: {abs(quantity_change)}")
            
        inv.quantity = new_qty
        
        movement = StockMovement(
            business_id=business_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            quantity=quantity_change,
            reference_type=reference_type,
            reference_id=reference_id,
            previous_quantity=prev_qty,
            resulting_quantity=new_qty,
            notes=notes
        )
        db.add(movement)
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            AuditService.log(db, business_id, "STOCK_ADJUSTED", "Inventory", inv.id, f"Adjusted {product.name} by {quantity_change}", user_id=user_id)
            
            # Low stock check
            if new_qty <= inv.reorder_level and prev_qty > inv.reorder_level:
                NotificationService.notify(db, business_id, "Low Stock Alert", f"Product {product.name} has fallen to {new_qty} units.", "WARNING", "Product", product.id, user_id=user_id)
                
        db.flush()
        return inv

    @staticmethod
    def get_total_stock(db: Session, product_id: str) -> Decimal:
        inventories = db.query(Inventory).filter(Inventory.product_id == product_id).all()
        return sum(inv.quantity for inv in inventories)

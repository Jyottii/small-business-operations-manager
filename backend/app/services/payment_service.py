from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.order import Order
from app.models.purchase_order import PurchaseOrder
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.schemas.payment import PaymentCreate
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.system_service import AuditService, NotificationService
from datetime import datetime
from decimal import Decimal

class PaymentService:
    @staticmethod
    def create_payment(db: Session, business_id: str, payment_data: PaymentCreate, user_id: str = "SYSTEM") -> Payment:
        payment = Payment(
            business_id=business_id,
            customer_id=payment_data.customer_id,
            supplier_id=payment_data.supplier_id,
            order_id=payment_data.order_id,
            purchase_order_id=payment_data.purchase_order_id,
            payment_method=payment_data.payment_method,
            amount=payment_data.amount,
            transaction_reference=payment_data.transaction_reference,
            notes=payment_data.notes,
            payment_date=datetime.utcnow()
        )
        
        if payment_data.order_id:
            order = db.query(Order).filter(Order.id == payment_data.order_id, Order.business_id == business_id).first()
            if not order:
                raise NotFoundException("Order not found")
            if payment_data.amount > order.balance_due:
                raise BadRequestException(f"Payment amount ${payment_data.amount:.2f} exceeds balance due ${order.balance_due:.2f}")
            
            payment.reference_type = "ORDER"
            payment.reference_id = order.id
            order.amount_paid = (order.amount_paid or Decimal('0.0')) + payment_data.amount
            order.balance_due = max(Decimal('0.0'), (order.balance_due or Decimal('0.0')) - payment_data.amount)
            
            if order.balance_due <= 0:
                order.payment_status = "Paid"
            else:
                order.payment_status = "Partially Paid"
                
            cust_id = payment_data.customer_id or order.customer_id
            payment.customer_id = cust_id
            if cust_id:
                customer = db.query(Customer).filter(Customer.id == cust_id).first()
                if customer:
                    customer.outstanding_balance = max(Decimal('0.0'), (customer.outstanding_balance or Decimal('0.0')) - payment_data.amount)
                    
            AuditService.log(db, business_id, "PAYMENT_RECEIVED", "Order", order.id, f"Payment of ${payment.amount:.2f} received for order {order.order_number}", user_id=user_id)
            NotificationService.notify(db, business_id, "Payment Received", f"Payment of ${payment.amount:.2f} received for order {order.order_number}.", "SUCCESS", "Order", order.id, user_id=user_id)
                
        elif payment_data.purchase_order_id:
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == payment_data.purchase_order_id, PurchaseOrder.business_id == business_id).first()
            if not po:
                raise NotFoundException("Purchase Order not found")
            if payment_data.amount > po.balance_due:
                raise BadRequestException(f"Payment amount ${payment_data.amount:.2f} exceeds balance due ${po.balance_due:.2f}")
                
            payment.reference_type = "PURCHASE_ORDER"
            payment.reference_id = po.id
            po.amount_paid = (po.amount_paid or Decimal('0.0')) + payment_data.amount
            po.balance_due = max(Decimal('0.0'), (po.balance_due or Decimal('0.0')) - payment_data.amount)
            
            supp_id = payment_data.supplier_id or po.supplier_id
            payment.supplier_id = supp_id
            if supp_id:
                supplier = db.query(Supplier).filter(Supplier.id == supp_id).first()
                if supplier:
                    supplier.outstanding_balance = max(Decimal('0.0'), (supplier.outstanding_balance or Decimal('0.0')) - payment_data.amount)
                    
            AuditService.log(db, business_id, "PAYMENT_SENT", "PurchaseOrder", po.id, f"Payment of ${payment.amount:.2f} sent for PO {po.purchase_order_number}", user_id=user_id)
            NotificationService.notify(db, business_id, "Payment Sent", f"Payment of ${payment.amount:.2f} recorded for PO {po.purchase_order_number}.", "INFO", "PurchaseOrder", po.id, user_id=user_id)
            
        db.add(payment)
        db.flush()
        return payment

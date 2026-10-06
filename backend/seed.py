import os
from datetime import datetime, timedelta
import random

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app.core.database import SessionLocal
from app.models import (
    Business, User, Employee, Customer, Supplier, Category, Product,
    Warehouse, Inventory, StockMovement, Order, OrderItem, PurchaseOrder,
    PurchaseOrderItem, Payment, Expense, Notification, AuditLog
)

def seed():
    db = SessionLocal()
    
    # 1. Business
    b1 = Business(name="TechHaven Electronics", legal_name="TechHaven LLC", email="hello@techhaven.com")
    db.add(b1)
    db.commit()
    db.refresh(b1)
    
    # 2. Employees & Users
    e1 = Employee(business_id=b1.id, name="Sarah Connor", email="sarah@techhaven.com", designation="Owner", status="Active", salary=100000)
    e2 = Employee(business_id=b1.id, name="John Smith", email="john@techhaven.com", designation="Manager", status="Active", salary=60000)
    e3 = Employee(business_id=b1.id, name="Mike Ross", email="mike@techhaven.com", designation="Sales Staff", status="Active", salary=45000)
    db.add_all([e1, e2, e3])
    db.commit()
    from app.core.security import hash_password
    pwd = hash_password("Password123!")
    u1 = User(business_id=b1.id, employee_id=e1.id, name="Sarah Connor", email="sarah@techhaven.com", password_hash=pwd, role="Owner")
    u2 = User(business_id=b1.id, employee_id=e2.id, name="John Smith", email="john@techhaven.com", password_hash=pwd, role="Manager")
    u3 = User(business_id=b1.id, employee_id=e3.id, name="Mike Ross", email="mike@techhaven.com", password_hash=pwd, role="Staff")
    db.add_all([u1, u2, u3])
    db.commit()

    # 3. Warehouses
    w1 = Warehouse(business_id=b1.id, name="Main Warehouse", code="WH-MAIN", manager_id=e2.id)
    w2 = Warehouse(business_id=b1.id, name="Retail Store Front", code="WH-RETAIL", manager_id=e3.id)
    db.add_all([w1, w2])
    db.commit()
    
    # 4. Categories
    cat_elec = Category(business_id=b1.id, name="Electronics")
    cat_acc = Category(business_id=b1.id, name="Accessories")
    db.add_all([cat_elec, cat_acc])
    db.commit()
    
    # 5. Suppliers
    s1 = Supplier(business_id=b1.id, name="Global Electronics", company_name="Global Electronics Ltd", email="sales@globalelectronics.com", outstanding_balance=2500.0)
    s2 = Supplier(business_id=b1.id, name="Office Supplies Inc", company_name="OS Inc", email="orders@officesupplies.com")
    s3 = Supplier(business_id=b1.id, name="Tech Components Ltd", company_name="Tech Comp Ltd", email="b2b@techcomp.com", outstanding_balance=1250.0)
    db.add_all([s1, s2, s3])
    db.commit()
    
    # 6. Customers
    c1 = Customer(business_id=b1.id, name="Alice Smith", email="alice@example.com", customer_type="Retail", outstanding_balance=0.0)
    c2 = Customer(business_id=b1.id, name="Bob Johnson", email="bob@example.com", customer_type="Retail")
    c3 = Customer(business_id=b1.id, name="Tech Corp", email="billing@techcorp.com", customer_type="B2B", outstanding_balance=1250.0)
    c4 = Customer(business_id=b1.id, name="Walk-in Customer", customer_type="Retail")
    db.add_all([c1, c2, c3, c4])
    db.commit()
    
    # 7. Products
    p1 = Product(business_id=b1.id, category_id=cat_elec.id, sku="WM-001", name="Wireless Mouse", cost_price=15.0, selling_price=29.99, reorder_level=50, reorder_quantity=100)
    p2 = Product(business_id=b1.id, category_id=cat_elec.id, sku="MK-023", name="Mechanical Keyboard", cost_price=45.0, selling_price=89.99, reorder_level=20, reorder_quantity=30)
    p3 = Product(business_id=b1.id, category_id=cat_acc.id, sku="UH-112", name="USB-C Hub", cost_price=20.0, selling_price=45.0, reorder_level=30, reorder_quantity=50)
    p4 = Product(business_id=b1.id, category_id=cat_acc.id, sku="LS-099", name="Laptop Stand", cost_price=12.5, selling_price=34.5, reorder_level=25, reorder_quantity=40)
    p5 = Product(business_id=b1.id, category_id=cat_elec.id, sku="MN-270", name="27 inch Monitor", cost_price=180.0, selling_price=299.0, reorder_level=10, reorder_quantity=15)
    db.add_all([p1, p2, p3, p4, p5])
    db.commit()
    
    # 8. Inventory & Stock Movement
    inv_data = [
        (p1, w1, 145), (p2, w1, 12), (p3, w2, 0), (p4, w1, 68), (p5, w1, 5)
    ]
    for p, w, qty in inv_data:
        inv = Inventory(product_id=p.id, warehouse_id=w.id, quantity=qty, reorder_level=p.reorder_level)
        sm = StockMovement(business_id=b1.id, product_id=p.id, warehouse_id=w.id, movement_type="INITIAL", quantity=qty, resulting_quantity=qty)
        db.add_all([inv, sm])
    db.commit()
    
    # 9. Orders & Sales
    o1 = Order(business_id=b1.id, customer_id=c1.id, employee_id=e3.id, order_number="ORD-1024", status="Completed", payment_status="Paid", subtotal=94.48, tax=7.56, total=102.04, amount_paid=102.04, order_date=datetime.utcnow())
    db.add(o1)
    db.commit()
    
    oi1 = OrderItem(order_id=o1.id, product_id=p1.id, quantity=2, unit_price=29.99, line_total=59.98)
    oi2 = OrderItem(order_id=o1.id, product_id=p4.id, quantity=1, unit_price=34.50, line_total=34.50)
    db.add_all([oi1, oi2])
    db.commit()
    
    # 10. Purchase Orders
    po1 = PurchaseOrder(business_id=b1.id, supplier_id=s1.id, warehouse_id=w1.id, purchase_order_number="PO-2023", status="Ordered", subtotal=4500.0, total=4500.0, balance_due=4500.0, order_date=datetime.utcnow())
    db.add(po1)
    db.commit()
    
    poi1 = PurchaseOrderItem(purchase_order_id=po1.id, product_id=p5.id, quantity_ordered=20, unit_cost=180.0, line_total=3600.0)
    poi2 = PurchaseOrderItem(purchase_order_id=po1.id, product_id=p2.id, quantity_ordered=20, unit_cost=45.0, line_total=900.0)
    db.add_all([poi1, poi2])
    db.commit()
    
    # 11. Payments & Expenses
    pay1 = Payment(business_id=b1.id, customer_id=c1.id, order_id=o1.id, reference_type="ORDER", amount=102.04, payment_method="Credit Card", payment_date=datetime.utcnow())
    exp1 = Expense(business_id=b1.id, category="Rent", description="Monthly Office Rent", amount=2000.0, payment_method="Bank Transfer", expense_date=datetime.utcnow())
    db.add_all([pay1, exp1])
    db.commit()
    
    print("Database seeded successfully with core realistic mock data!")

if __name__ == "__main__":
    seed()

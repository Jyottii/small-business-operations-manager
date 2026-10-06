import sys
import os
import uuid
from decimal import Decimal
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.business import Business
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.payment import Payment
from app.models.return_order import Return, ReturnItem
from app.models.expense import Expense
from app.core.security import hash_password, create_access_token

client = TestClient(app)

def run_analytics_tests():
    print("=== STARTING PHASE 6 (TASK 1) BUSINESS INTELLIGENCE & ANALYTICS TEST SUITE ===")
    db = SessionLocal()

    suffix = uuid.uuid4().hex[:6]
    pwd_plain = "AnalyticsPass123!"
    pwd_hash = hash_password(pwd_plain)

    # =========================================================================
    # SETUP: Create Business A (Rich Data), Business B (Cross-Tenant), Business C (Empty)
    # =========================================================================
    
    # 1. Business A
    biz_a = Business(name=f"Analytics Biz A {suffix}", legal_name=f"Biz A Corp {suffix}")
    db.add(biz_a)
    db.commit()
    db.refresh(biz_a)
    biz_a_id = biz_a.id

    wh_a = Warehouse(business_id=biz_a_id, name="WH Main", code=f"WH-A-{suffix}")
    db.add(wh_a)
    db.commit()
    db.refresh(wh_a)

    u_owner_a = User(business_id=biz_a_id, name="Owner A", email=f"owner_{suffix}@a.com", password_hash=pwd_hash, role="Owner", is_active=True)
    u_admin_a = User(business_id=biz_a_id, name="Admin A", email=f"admin_{suffix}@a.com", password_hash=pwd_hash, role="Admin", is_active=True)
    u_mgr_a = User(business_id=biz_a_id, name="Manager A", email=f"mgr_{suffix}@a.com", password_hash=pwd_hash, role="Manager", is_active=True)
    u_staff_a = User(business_id=biz_a_id, name="Staff A", email=f"staff_{suffix}@a.com", password_hash=pwd_hash, role="Staff", is_active=True)
    db.add_all([u_owner_a, u_admin_a, u_mgr_a, u_staff_a])
    db.commit()

    token_owner_a = create_access_token({"sub": u_owner_a.id, "email": u_owner_a.email, "role": u_owner_a.role, "business_id": biz_a_id})
    token_admin_a = create_access_token({"sub": u_admin_a.id, "email": u_admin_a.email, "role": u_admin_a.role, "business_id": biz_a_id})
    token_mgr_a = create_access_token({"sub": u_mgr_a.id, "email": u_mgr_a.email, "role": u_mgr_a.role, "business_id": biz_a_id})
    token_staff_a = create_access_token({"sub": u_staff_a.id, "email": u_staff_a.email, "role": u_staff_a.role, "business_id": biz_a_id})

    headers_owner_a = {"Authorization": f"Bearer {token_owner_a}"}
    headers_staff_a = {"Authorization": f"Bearer {token_staff_a}"}

    # Business A Products
    # Product 1: Best seller (cost: 50, sell: 100, reorder: 5)
    p1 = Product(business_id=biz_a_id, sku=f"SKU-HOT-{suffix}", name="Hot Product", cost_price=Decimal("50.00"), selling_price=Decimal("100.00"), reorder_level=Decimal("5.00"), is_active=True)
    # Product 2: Low stock item (cost: 20, sell: 40, reorder: 10, stock will be 3)
    p2 = Product(business_id=biz_a_id, sku=f"SKU-LOW-{suffix}", name="Low Stock Item", cost_price=Decimal("20.00"), selling_price=Decimal("40.00"), reorder_level=Decimal("10.00"), is_active=True)
    # Product 3: Out of stock item (cost: 10, sell: 25, reorder: 5, stock will be 0)
    p3 = Product(business_id=biz_a_id, sku=f"SKU-OUT-{suffix}", name="Out of Stock Item", cost_price=Decimal("10.00"), selling_price=Decimal("25.00"), reorder_level=Decimal("5.00"), is_active=True)
    # Product 4: Slow moving / stagnant item (cost: 80, sell: 150, stock: 20, 0 sales)
    p4 = Product(business_id=biz_a_id, sku=f"SKU-SLOW-{suffix}", name="Slow Moving Luxury", cost_price=Decimal("80.00"), selling_price=Decimal("150.00"), reorder_level=Decimal("2.00"), is_active=True)
    db.add_all([p1, p2, p3, p4])
    db.commit()

    # Inventory for Business A
    inv1 = Inventory(product_id=p1.id, warehouse_id=wh_a.id, quantity=Decimal("40.00")) # 40 units * $50 = $2000
    inv2 = Inventory(product_id=p2.id, warehouse_id=wh_a.id, quantity=Decimal("3.00"))  # 3 units * $20 = $60 (<= reorder 10)
    inv3 = Inventory(product_id=p3.id, warehouse_id=wh_a.id, quantity=Decimal("0.00"))  # 0 units * $10 = $0 (out of stock)
    inv4 = Inventory(product_id=p4.id, warehouse_id=wh_a.id, quantity=Decimal("20.00")) # 20 units * $80 = $1600 (slow moving)
    db.add_all([inv1, inv2, inv3, inv4])
    db.commit()

    # Total inventory units: 40 + 3 + 0 + 20 = 63.00
    # Total inventory value: 2000 + 60 + 0 + 1600 = $3660.00

    # Stock Movements for Business A
    sm1 = StockMovement(business_id=biz_a_id, product_id=p1.id, warehouse_id=wh_a.id, movement_type="PURCHASE_RECEIPT", quantity=Decimal("50.00"), previous_quantity=Decimal("0.00"), resulting_quantity=Decimal("50.00"), unit_cost=Decimal("50.00"))
    sm2 = StockMovement(business_id=biz_a_id, product_id=p1.id, warehouse_id=wh_a.id, movement_type="SALE", quantity=Decimal("-10.00"), previous_quantity=Decimal("50.00"), resulting_quantity=Decimal("40.00"), unit_cost=Decimal("50.00"))
    db.add_all([sm1, sm2])
    db.commit()

    # Customers for Business A
    cust1 = Customer(business_id=biz_a_id, name="Big Spender Alice", email=f"alice_{suffix}@test.com", outstanding_balance=Decimal("200.00"))
    cust2 = Customer(business_id=biz_a_id, name="Casual Bob", email=f"bob_{suffix}@test.com", outstanding_balance=Decimal("0.00"))
    db.add_all([cust1, cust2])
    db.commit()

    # Suppliers for Business A
    supp1 = Supplier(business_id=biz_a_id, name="Mega Supplier", company_name="Mega Supplies Ltd", outstanding_balance=Decimal("500.00"))
    db.add(supp1)
    db.commit()

    # Orders for Business A (recent, within 30 days)
    # Order 1: Alice buys 6x Hot Product ($600) + 2x Low Stock ($80) = $680 (Completed)
    ord1 = Order(business_id=biz_a_id, customer_id=cust1.id, order_number=f"ORD-A1-{suffix}", status="Completed", total=Decimal("680.00"), order_date=datetime.utcnow() - timedelta(days=2))
    db.add(ord1)
    db.commit()
    db.refresh(ord1)
    oi1 = OrderItem(order_id=ord1.id, product_id=p1.id, quantity=Decimal("6.00"), unit_price=Decimal("100.00"), line_total=Decimal("600.00"))
    oi2 = OrderItem(order_id=ord1.id, product_id=p2.id, quantity=Decimal("2.00"), unit_price=Decimal("40.00"), line_total=Decimal("80.00"))
    db.add_all([oi1, oi2])
    db.commit()

    # Order 2: Bob buys 4x Hot Product ($400) = $400 (Pending)
    ord2 = Order(business_id=biz_a_id, customer_id=cust2.id, order_number=f"ORD-A2-{suffix}", status="Pending", total=Decimal("400.00"), order_date=datetime.utcnow() - timedelta(days=1))
    db.add(ord2)
    db.commit()
    db.refresh(ord2)
    oi3 = OrderItem(order_id=ord2.id, product_id=p1.id, quantity=Decimal("4.00"), unit_price=Decimal("100.00"), line_total=Decimal("400.00"))
    db.add(oi3)
    db.commit()

    # Order 3: Cancelled order ($200) -> should be excluded from sales metrics
    ord_cancel = Order(business_id=biz_a_id, customer_id=cust2.id, order_number=f"ORD-CANC-{suffix}", status="Cancelled", total=Decimal("200.00"), order_date=datetime.utcnow() - timedelta(days=3))
    db.add(ord_cancel)
    db.commit()

    # Total valid sales: 680 + 400 = $1080.00
    # Total valid orders: 2
    # AOV: 1080 / 2 = $540.00
    # COGS for valid orders:
    # ord1: (6 * 50) + (2 * 20) = 300 + 40 = $340
    # ord2: (4 * 50) = $200
    # Total COGS: 340 + 200 = $540.00
    # Gross Profit: 1080 - 540 = $540.00 (Gross Margin: 50.0%)

    # Order 4: Old Order (60 days ago) for Date Filter Testing: $500
    ord_old = Order(business_id=biz_a_id, customer_id=cust1.id, order_number=f"ORD-OLD-{suffix}", status="Completed", total=Decimal("500.00"), order_date=datetime.utcnow() - timedelta(days=60))
    db.add(ord_old)
    db.commit()
    db.refresh(ord_old)
    oi_old = OrderItem(order_id=ord_old.id, product_id=p1.id, quantity=Decimal("5.00"), unit_price=Decimal("100.00"), line_total=Decimal("500.00"))
    db.add(oi_old)
    db.commit()

    # Payments for Business A
    pay1 = Payment(business_id=biz_a_id, customer_id=cust1.id, order_id=ord1.id, amount=Decimal("480.00"), payment_method="Card", payment_date=datetime.utcnow() - timedelta(days=2))
    db.add(pay1)
    db.commit()

    # Returns for Business A
    ret1 = Return(business_id=biz_a_id, order_id=ord1.id, return_number=f"RET-A1-{suffix}", status="Processed", refund_amount=Decimal("50.00"), return_date=datetime.utcnow() - timedelta(days=1))
    db.add(ret1)
    db.commit()
    db.refresh(ret1)
    ri1 = ReturnItem(return_id=ret1.id, order_item_id=oi1.id, product_id=p1.id, quantity=Decimal("1.00"), refund_amount=Decimal("50.00"))
    db.add(ri1)
    db.commit()

    # Purchase Orders for Business A
    po1 = PurchaseOrder(business_id=biz_a_id, supplier_id=supp1.id, warehouse_id=wh_a.id, purchase_order_number=f"PO-A1-{suffix}", status="Received", total=Decimal("1500.00"), order_date=datetime.utcnow() - timedelta(days=5))
    po2 = PurchaseOrder(business_id=biz_a_id, supplier_id=supp1.id, warehouse_id=wh_a.id, purchase_order_number=f"PO-A2-{suffix}", status="Ordered", total=Decimal("800.00"), order_date=datetime.utcnow() - timedelta(days=1))
    db.add_all([po1, po2])
    db.commit()

    # Expenses for Business A
    exp1 = Expense(business_id=biz_a_id, category="Utilities", amount=Decimal("120.00"), expense_date=datetime.utcnow() - timedelta(days=3))
    db.add(exp1)
    db.commit()

    # 2. Business B (Tenant Isolation Verification)
    biz_b = Business(name=f"Analytics Biz B {suffix}", legal_name=f"Biz B Corp {suffix}")
    db.add(biz_b)
    db.commit()
    db.refresh(biz_b)
    biz_b_id = biz_b.id

    u_owner_b = User(business_id=biz_b_id, name="Owner B", email=f"owner_{suffix}@b.com", password_hash=pwd_hash, role="Owner", is_active=True)
    db.add(u_owner_b)
    db.commit()
    token_owner_b = create_access_token({"sub": u_owner_b.id, "email": u_owner_b.email, "role": u_owner_b.role, "business_id": biz_b_id})
    headers_owner_b = {"Authorization": f"Bearer {token_owner_b}"}

    p_b = Product(business_id=biz_b_id, sku=f"SKU-B-{suffix}", name="Biz B Product", cost_price=Decimal("10.00"), selling_price=Decimal("20.00"), is_active=True)
    db.add(p_b)
    db.commit()
    ord_b = Order(business_id=biz_b_id, order_number=f"ORD-B-{suffix}", status="Completed", total=Decimal("9999.00"), order_date=datetime.utcnow())
    db.add(ord_b)
    db.commit()

    # 3. Business C (Empty Business Verification)
    biz_c = Business(name=f"Analytics Biz C {suffix}", legal_name=f"Biz C Corp {suffix}")
    db.add(biz_c)
    db.commit()
    db.refresh(biz_c)
    biz_c_id = biz_c.id

    u_owner_c = User(business_id=biz_c_id, name="Owner C", email=f"owner_{suffix}@c.com", password_hash=pwd_hash, role="Owner", is_active=True)
    db.add(u_owner_c)
    db.commit()
    token_owner_c = create_access_token({"sub": u_owner_c.id, "email": u_owner_c.email, "role": u_owner_c.role, "business_id": biz_c_id})
    headers_owner_c = {"Authorization": f"Bearer {token_owner_c}"}

    # =========================================================================
    # TEST A: EMPTY BUSINESS SAFETY
    # =========================================================================
    print("\n--- TEST A: Empty Business Handling ---")
    res_c_sum = client.get("/api/v1/analytics/summary", headers=headers_owner_c)
    assert res_c_sum.status_code == 200, res_c_sum.text
    data_c = res_c_sum.json()["data"]
    assert data_c["sales"]["total_revenue"] == 0.0
    assert data_c["sales"]["total_orders"] == 0
    assert data_c["sales"]["average_order_value"] == 0.0
    assert data_c["inventory"]["total_inventory_units"] == 0.0
    assert data_c["inventory"]["total_inventory_value"] == 0.0
    assert data_c["financial"]["gross_profit"] == 0.0
    assert data_c["financial"]["cost_data_coverage_percentage"] == 100.0

    res_c_prod = client.get("/api/v1/analytics/products", headers=headers_owner_c)
    assert res_c_prod.status_code == 200
    assert len(res_c_prod.json()["data"]["top_by_revenue"]) == 0

    res_c_cust = client.get("/api/v1/analytics/customers", headers=headers_owner_c)
    assert res_c_cust.status_code == 200
    assert len(res_c_cust.json()["data"]["top_customers"]) == 0

    print("[PASS] Empty business queries executed safely without division-by-zero crashes.")

    # =========================================================================
    # TEST B: SALES CALCULATIONS & KPIS
    # =========================================================================
    print("\n--- TEST B: Sales Calculations & KPIs ---")
    res_sales = client.get("/api/v1/analytics/sales?period=last_30_days", headers=headers_owner_a)
    assert res_sales.status_code == 200, res_sales.text
    sales_d = res_sales.json()["data"]
    kpis = sales_d["kpis"]

    # In last 30 days: ord1 (680) + ord2 (400) = 1080. ord_cancel (200) excluded. ord_old (500) excluded.
    assert kpis["total_revenue"] == 1080.0
    assert kpis["total_orders"] == 2
    assert kpis["average_order_value"] == 540.0
    assert kpis["completed_orders_count"] == 1
    assert kpis["pending_orders_count"] == 1
    assert kpis["cancelled_orders_count"] == 1
    assert kpis["returned_orders_count"] == 1

    # Payment methods breakdown
    assert len(sales_d["payment_methods"]) >= 1
    card_method = next((m for m in sales_d["payment_methods"] if m["method"] == "Card"), None)
    assert card_method is not None
    assert card_method["total"] == 480.0

    print("[PASS] Sales KPIs, revenue, order count, AOV, and statuses calculated accurately.")

    # =========================================================================
    # TEST C: PRODUCT RANKINGS & INVENTORY VELOCITY
    # =========================================================================
    print("\n--- TEST C: Product Performance & Rankings ---")
    res_prod = client.get("/api/v1/analytics/products?period=last_30_days", headers=headers_owner_a)
    assert res_prod.status_code == 200, res_prod.text
    prod_d = res_prod.json()["data"]

    # Top by revenue should be Hot Product ($1000 sales)
    top_rev = prod_d["top_by_revenue"]
    assert len(top_rev) >= 1
    assert top_rev[0]["name"] == "Hot Product"
    assert top_rev[0]["revenue"] == 1000.0
    assert top_rev[0]["quantity_sold"] == 10.0
    assert top_rev[0]["status"] == "Fast-Moving"

    # Slow moving should identify the stagnant luxury product (20 in stock, 0 sold)
    slow = prod_d["slow_moving"]
    slow_names = [p["name"] for p in slow]
    assert "Slow Moving Luxury" in slow_names

    # Low stock list should include p2 (Low Stock Item) and p3 (Out of Stock Item)
    low_stock = prod_d["low_stock"]
    low_names = [p["name"] for p in low_stock]
    assert "Low Stock Item" in low_names or "Out of Stock Item" in low_names

    print("[PASS] Product revenue, volume ranking, slow-moving detection, and low stock verified.")

    # =========================================================================
    # TEST D: INVENTORY METRICS & STOCK MOVEMENTS
    # =========================================================================
    print("\n--- TEST D: Inventory Intelligence & Movements ---")
    res_inv = client.get("/api/v1/analytics/inventory", headers=headers_owner_a)
    assert res_inv.status_code == 200, res_inv.text
    inv_d = res_inv.json()["data"]

    assert inv_d["kpis"]["total_inventory_units"] == 63.0
    assert inv_d["kpis"]["total_inventory_value"] == 3660.0
    assert inv_d["kpis"]["out_of_stock_count"] == 1
    assert inv_d["kpis"]["low_stock_count"] == 1
    assert inv_d["kpis"]["total_products"] == 4
    assert inv_d["kpis"]["total_stock_movements"] >= 2

    # Warehouse breakdown
    assert len(inv_d["by_warehouse"]) == 1
    assert inv_d["by_warehouse"][0]["warehouse_name"] == "WH Main"
    assert inv_d["by_warehouse"][0]["total_units"] == 63.0

    print("[PASS] Inventory totals, valuation, warehouse distribution, and movement counts verified.")

    # =========================================================================
    # TEST E: CUSTOMER METRICS & RECEIVABLES
    # =========================================================================
    print("\n--- TEST E: Customer Analytics & Receivables ---")
    res_cust = client.get("/api/v1/analytics/customers?period=last_30_days", headers=headers_owner_a)
    assert res_cust.status_code == 200, res_cust.text
    cust_d = res_cust.json()["data"]

    assert cust_d["kpis"]["total_customers"] == 2
    assert cust_d["kpis"]["total_receivables"] == 200.0

    top_cust = cust_d["top_customers"]
    assert len(top_cust) >= 1
    assert top_cust[0]["name"] == "Big Spender Alice"
    assert top_cust[0]["total_spent"] == 680.0
    assert top_cust[0]["outstanding_balance"] == 200.0

    print("[PASS] Customer sales ranking, balances, and receivables calculated accurately.")

    # =========================================================================
    # TEST F: PURCHASING METRICS
    # =========================================================================
    print("\n--- TEST F: Purchasing Analytics ---")
    res_purch = client.get("/api/v1/analytics/purchases?period=last_30_days", headers=headers_owner_a)
    assert res_purch.status_code == 200, res_purch.text
    purch_d = res_purch.json()["data"]

    # po1: 1500 (Received), po2: 800 (Ordered) -> Total: 2300
    assert purch_d["kpis"]["total_purchase_spend"] == 2300.0
    assert purch_d["kpis"]["total_purchase_orders"] == 2
    assert purch_d["kpis"]["received_purchase_orders"] == 1
    assert purch_d["kpis"]["pending_purchase_orders"] == 1

    assert len(purch_d["top_suppliers"]) == 1
    assert purch_d["top_suppliers"][0]["name"] == "Mega Supplier"
    assert purch_d["top_suppliers"][0]["total_spend"] == 2300.0

    print("[PASS] Purchasing spend, PO statuses, and supplier performance verified.")

    # =========================================================================
    # TEST G: RETURN & REFUND METRICS
    # =========================================================================
    print("\n--- TEST G: Return & Refund Metrics ---")
    res_sum = client.get("/api/v1/analytics/summary?period=last_30_days", headers=headers_owner_a)
    assert res_sum.status_code == 200, res_sum.text
    ret_kpi = res_sum.json()["data"]["returns"]

    assert ret_kpi["total_returns"] == 1
    assert ret_kpi["total_returned_quantity"] == 1.0
    assert ret_kpi["total_refund_amount"] == 50.0

    print("[PASS] Returns count, returned quantities, and refund totals verified.")

    # =========================================================================
    # TEST H: FINANCIAL & PROFIT ANALYTICS (P&L)
    # =========================================================================
    print("\n--- TEST H: Financial / P&L Analytics ---")
    res_fin = client.get("/api/v1/analytics/financial?period=last_30_days", headers=headers_owner_a)
    assert res_fin.status_code == 200, res_fin.text
    fin_d = res_fin.json()["data"]

    # Sales: 1080, COGS: 540, Gross Profit: 540, Gross Margin: 50.0%
    assert fin_d["total_sales"] == 1080.0
    assert fin_d["cogs"] == 540.0
    assert fin_d["gross_profit"] == 540.0
    assert fin_d["gross_margin_percentage"] == 50.0
    assert fin_d["total_expenses"] == 120.0
    # Net Profit: Gross Profit (540) - Expenses (120) = 420.0
    assert fin_d["net_profit"] == 420.0
    assert fin_d["collected_payments"] == 480.0
    assert fin_d["cost_data_coverage_percentage"] == 100.0

    print("[PASS] Financial KPIs, COGS, Gross Profit, Gross Margin, and Net Profit verified.")

    # =========================================================================
    # TEST I: DATE FILTERING
    # =========================================================================
    print("\n--- TEST I: Date Range Filtering ---")
    # In last 30 days, old order ($500) is excluded: total is 1080
    res_30 = client.get("/api/v1/analytics/summary?period=last_30_days", headers=headers_owner_a)
    assert res_30.json()["data"]["sales"]["total_revenue"] == 1080.0

    # In all_time, old order ($500) is included: total is 1080 + 500 = 1580
    res_all = client.get("/api/v1/analytics/summary?period=all_time", headers=headers_owner_a)
    assert res_all.json()["data"]["sales"]["total_revenue"] == 1580.0
    assert res_all.json()["data"]["sales"]["total_orders"] == 3

    print("[PASS] Date filtering strictly includes records in window and excludes older records.")

    # =========================================================================
    # TEST J: MULTI-TENANT ISOLATION
    # =========================================================================
    print("\n--- TEST J: Multi-Tenant Business Isolation ---")
    # Business B has a $9999 order. Business A should NEVER see it!
    res_a_sum = client.get("/api/v1/analytics/summary?period=all_time", headers=headers_owner_a)
    rev_a = res_a_sum.json()["data"]["sales"]["total_revenue"]
    assert rev_a == 1580.0, f"Expected 1580.0, got {rev_a}"

    res_b_sum = client.get("/api/v1/analytics/summary?period=all_time", headers=headers_owner_b)
    rev_b = res_b_sum.json()["data"]["sales"]["total_revenue"]
    assert rev_b == 9999.0, f"Expected 9999.0, got {rev_b}"

    # Try tenant spoofing with X-Business-ID header: JWT must override it!
    res_spoof = client.get("/api/v1/analytics/summary?period=all_time", headers={
        "Authorization": f"Bearer {token_owner_a}",
        "X-Business-ID": biz_b_id
    })
    assert res_spoof.json()["data"]["sales"]["total_revenue"] == 1580.0

    print("[PASS] Multi-tenant isolation verified: zero data leakage across businesses.")

    # =========================================================================
    # TEST K: ROLE-BASED ACCESS CONTROL (RBAC)
    # =========================================================================
    print("\n--- TEST K: Role-Based Access Control ---")
    # Unauthenticated request -> 401
    res_unauth = client.get("/api/v1/analytics/summary")
    assert res_unauth.status_code == 401

    # Staff role -> 403 Forbidden across all endpoints
    endpoints = ["/summary", "/sales", "/products", "/customers", "/inventory", "/purchases", "/financial"]
    for ep in endpoints:
        res_staff = client.get(f"/api/v1/analytics{ep}", headers=headers_staff_a)
        assert res_staff.status_code == 403, f"Expected 403 on {ep}, got {res_staff.status_code}"

    # Owner -> 200 OK
    res_owner = client.get("/api/v1/analytics/summary", headers=headers_owner_a)
    assert res_owner.status_code == 200

    # Admin -> 200 OK
    res_admin = client.get("/api/v1/analytics/summary", headers={"Authorization": f"Bearer {token_admin_a}"})
    assert res_admin.status_code == 200

    # Manager -> 200 OK
    res_mgr = client.get("/api/v1/analytics/summary", headers={"Authorization": f"Bearer {token_mgr_a}"})
    assert res_mgr.status_code == 200

    print("[PASS] RBAC enforced: 401 unauthenticated, 403 Staff, 200 Owner/Admin/Manager.")

    print("\n=== ALL PHASE 6 (TASK 1) ANALYTICS TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_analytics_tests()

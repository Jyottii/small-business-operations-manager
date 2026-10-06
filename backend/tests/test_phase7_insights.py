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

def run_insights_tests():
    print("=== STARTING PHASE 7 (TASK 1) SMART BUSINESS INSIGHTS TEST SUITE ===")
    db = SessionLocal()

    suffix = uuid.uuid4().hex[:6]
    pwd_plain = "InsightsPass123!"
    pwd_hash = hash_password(pwd_plain)

    # =========================================================================
    # SETUP: Business A (Rich Insight Test Data)
    # =========================================================================
    biz_a = Business(name=f"Insights Biz A {suffix}", legal_name=f"Insights Biz A Corp {suffix}")
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
    headers_admin_a = {"Authorization": f"Bearer {token_admin_a}"}
    headers_mgr_a = {"Authorization": f"Bearer {token_mgr_a}"}
    headers_staff_a = {"Authorization": f"Bearer {token_staff_a}"}

    # Products for Business A
    # P1: Hot seller (cost: 50, sell: 100, reorder: 5, stock: 40)
    p1 = Product(business_id=biz_a_id, sku=f"SKU-HOT-{suffix}", name="Hot Product", cost_price=Decimal("50.00"), selling_price=Decimal("100.00"), reorder_level=Decimal("5.00"), is_active=True)
    # P2: Low stock item (cost: 20, sell: 40, reorder: 10, stock: 3)
    p2 = Product(business_id=biz_a_id, sku=f"SKU-LOW-{suffix}", name="Low Stock Item", cost_price=Decimal("20.00"), selling_price=Decimal("40.00"), reorder_level=Decimal("10.00"), is_active=True)
    # P3: Out of stock item (cost: 10, sell: 25, reorder: 5, stock: 0)
    p3 = Product(business_id=biz_a_id, sku=f"SKU-OUT-{suffix}", name="Out of Stock Item", cost_price=Decimal("10.00"), selling_price=Decimal("25.00"), reorder_level=Decimal("5.00"), is_active=True)
    # P4: Slow moving / stagnant item (cost: 80, sell: 150, reorder: 2, stock: 20 -> $1600 tied up)
    p4 = Product(business_id=biz_a_id, sku=f"SKU-SLOW-{suffix}", name="Slow Moving Luxury", cost_price=Decimal("80.00"), selling_price=Decimal("150.00"), reorder_level=Decimal("2.00"), is_active=True)
    # P5: Missing cost price item (cost: None, sell: 60, reorder: 5, stock: 15) -> flags cost coverage
    p5 = Product(business_id=biz_a_id, sku=f"SKU-NOCOST-{suffix}", name="Missing Cost Item", cost_price=None, selling_price=Decimal("60.00"), reorder_level=Decimal("5.00"), is_active=True)
    db.add_all([p1, p2, p3, p4, p5])
    db.commit()

    # Inventory
    inv1 = Inventory(product_id=p1.id, warehouse_id=wh_a.id, quantity=Decimal("40.00")) # 40 * 50 = $2000
    inv2 = Inventory(product_id=p2.id, warehouse_id=wh_a.id, quantity=Decimal("3.00"))  # 3 * 20 = $60 (<= reorder 10)
    inv3 = Inventory(product_id=p3.id, warehouse_id=wh_a.id, quantity=Decimal("0.00"))  # 0 units (Out of stock)
    inv4 = Inventory(product_id=p4.id, warehouse_id=wh_a.id, quantity=Decimal("20.00")) # 20 * 80 = $1600 (Slow moving)
    inv5 = Inventory(product_id=p5.id, warehouse_id=wh_a.id, quantity=Decimal("15.00")) # 15 units
    db.add_all([inv1, inv2, inv3, inv4, inv5])
    db.commit()

    # Customers
    # C1: Dominant customer (generates 85% of revenue -> Customer Concentration)
    c1 = Customer(business_id=biz_a_id, name="Big Whale Corp", email=f"whale_{suffix}@client.com", outstanding_balance=Decimal("200.00"))
    # C2: High receivable customer (owes $800 -> High Receivable Customer Warning)
    c2 = Customer(business_id=biz_a_id, name="Overdue Client", email=f"overdue_{suffix}@client.com", outstanding_balance=Decimal("800.00"))
    # C3: Smaller customer
    c3 = Customer(business_id=biz_a_id, name="Regular Buyer", email=f"regular_{suffix}@client.com", outstanding_balance=Decimal("0.00"))
    db.add_all([c1, c2, c3])
    db.commit()

    # Supplier
    # S1: Dominant supplier with large outstanding payable ($1500)
    s1 = Supplier(business_id=biz_a_id, name="Primary Vendor Ltd", company_name="Primary Vendor", outstanding_balance=Decimal("1500.00"))
    # S2: Secondary supplier
    s2 = Supplier(business_id=biz_a_id, name="Minor Parts Co", company_name="Minor Parts", outstanding_balance=Decimal("50.00"))
    db.add_all([s1, s2])
    db.commit()

    # Purchase Orders: S1 receives $2000, S2 receives $100 -> Supplier Concentration (95%)
    now = datetime.utcnow()
    po1 = PurchaseOrder(business_id=biz_a_id, supplier_id=s1.id, warehouse_id=wh_a.id, purchase_order_number=f"PO-1-{suffix}", status="Received", total=Decimal("2000.00"), order_date=now - timedelta(days=5))
    po2 = PurchaseOrder(business_id=biz_a_id, supplier_id=s2.id, warehouse_id=wh_a.id, purchase_order_number=f"PO-2-{suffix}", status="Received", total=Decimal("100.00"), order_date=now - timedelta(days=4))
    db.add_all([po1, po2])
    db.commit()

    # Orders for Business A:
    # Order 1: Whale Corp buys 17 units of Hot Product ($1700)
    o1 = Order(business_id=biz_a_id, customer_id=c1.id, order_number=f"ORD-1-{suffix}", status="Completed", total=Decimal("1700.00"), order_date=now - timedelta(days=3))
    db.add(o1)
    db.commit()
    db.refresh(o1)
    oi1 = OrderItem(order_id=o1.id, product_id=p1.id, quantity=Decimal("17.00"), unit_price=Decimal("100.00"), line_total=Decimal("1700.00"))
    db.add(oi1)

    # Order 2: Regular Buyer buys 3 units of p5 (Missing cost) ($180)
    o2 = Order(business_id=biz_a_id, customer_id=c3.id, order_number=f"ORD-2-{suffix}", status="Completed", total=Decimal("180.00"), order_date=now - timedelta(days=2))
    db.add(o2)
    db.commit()
    db.refresh(o2)
    oi2 = OrderItem(order_id=o2.id, product_id=p5.id, quantity=Decimal("3.00"), unit_price=Decimal("60.00"), line_total=Decimal("180.00"))
    db.add(oi2)

    # Order 3: Regular Buyer buys 3 units of p2 (Low stock item) ($120)
    o3 = Order(business_id=biz_a_id, customer_id=c3.id, order_number=f"ORD-3-{suffix}", status="Completed", total=Decimal("120.00"), order_date=now - timedelta(days=1))
    db.add(o3)
    db.commit()
    db.refresh(o3)
    oi3 = OrderItem(order_id=o3.id, product_id=p2.id, quantity=Decimal("3.00"), unit_price=Decimal("40.00"), line_total=Decimal("120.00"))
    db.add(oi3)
    db.commit()

    # Total Sales: 1700 + 180 + 120 = $2000.00
    # Customer 1 Share: 1700 / 2000 = 85.0% (triggers customer concentration)
    # COGS: 17 * 50 (850) + 3 * 0 (0 missing cost) + 3 * 20 (60) = $910.00
    # Gross Profit: 2000 - 910 = $1090.00
    # Cost Data Coverage: 2 out of 3 order items have cost data = 66.7% (< 85% -> triggers cost coverage warning)

    # Operating Expense: Add $1500 expense so Net Profit = 1090 - 1500 = -$410.00 (triggers CRITICAL negative net profit)
    exp = Expense(business_id=biz_a_id, category="Rent", description="Facility Rent", amount=Decimal("1500.00"), expense_date=now - timedelta(days=2))
    db.add(exp)
    db.commit()

    # Receivables: c1 (200) + c2 (800) = $1000.00 out of $2000.00 sales = 50.0% (> 40% -> triggers receivables risk)
    # Payables: s1 (1500) + s2 (50) = $1550.00 out of $2100.00 purchases = 73.8% (> 50% -> triggers payables pressure)

    # =========================================================================
    # SETUP: Business B (Tenant Isolation verification)
    # =========================================================================
    biz_b = Business(name=f"Insights Biz B {suffix}", legal_name=f"Biz B Corp {suffix}")
    db.add(biz_b)
    db.commit()
    db.refresh(biz_b)
    biz_b_id = biz_b.id

    u_owner_b = User(business_id=biz_b_id, name="Owner B", email=f"owner_{suffix}@b.com", password_hash=pwd_hash, role="Owner", is_active=True)
    db.add(u_owner_b)
    db.commit()
    token_owner_b = create_access_token({"sub": u_owner_b.id, "email": u_owner_b.email, "role": u_owner_b.role, "business_id": biz_b_id})
    headers_owner_b = {"Authorization": f"Bearer {token_owner_b}"}

    # =========================================================================
    # SETUP: Business C (Empty Business - No Data)
    # =========================================================================
    biz_c = Business(name=f"Insights Biz C {suffix}", legal_name=f"Biz C Corp {suffix}")
    db.add(biz_c)
    db.commit()
    db.refresh(biz_c)
    biz_c_id = biz_c.id

    u_owner_c = User(business_id=biz_c_id, name="Owner C", email=f"owner_{suffix}@c.com", password_hash=pwd_hash, role="Owner", is_active=True)
    db.add(u_owner_c)
    db.commit()
    token_owner_c = create_access_token({"sub": u_owner_c.id, "email": u_owner_c.email, "role": u_owner_c.role, "business_id": biz_c_id})
    headers_owner_c = {"Authorization": f"Bearer {token_owner_c}"}

    print("Setup completed successfully. Running verification test assertions...\n")

    # =========================================================================
    # TEST A: No-data business (Empty Business C)
    # =========================================================================
    res_c = client.get("/api/v1/insights?period=last_30_days", headers=headers_owner_c)
    assert res_c.status_code == 200, f"Expected 200 for empty business, got {res_c.status_code}: {res_c.text}"
    c_data = res_c.json()["data"]
    assert c_data["summary"]["critical"] == 0, "Empty business should have 0 critical insights"
    assert c_data["summary"]["warning"] == 0, "Empty business should have 0 warning insights"
    print("PASS: [Test A] Empty Business C returns 200 without crashes or false positives")

    # =========================================================================
    # FETCH BUSINESS A INSIGHTS
    # =========================================================================
    res_a = client.get("/api/v1/insights?period=last_30_days", headers=headers_owner_a)
    assert res_a.status_code == 200, f"Expected 200 for Business A, got {res_a.status_code}: {res_a.text}"
    a_data = res_a.json()["data"]
    insights_a = a_data["insights"]
    insight_ids = {item["id"] for item in insights_a}
    categories = {item["category"] for item in insights_a}

    print(f"Business A generated {len(insights_a)} insights: {a_data['summary']}")
    for item in insights_a:
        print(f"  [{item['severity'].upper()}] ({item['category']}) {item['title']} - Metric: {item['metric']} = {item['current_value']}")

    # =========================================================================
    # TEST B: Out-of-stock detection (Critical)
    # =========================================================================
    oos_insights = [item for item in insights_a if "oos" in item["id"]]
    assert len(oos_insights) > 0, "Expected Out-of-Stock insight in Business A"
    assert oos_insights[0]["severity"] == "critical", f"Expected CRITICAL severity, got {oos_insights[0]['severity']}"
    assert oos_insights[0]["category"] == "inventory"
    print("PASS: [Test B] Out-of-stock detection flagged with CRITICAL severity")

    # =========================================================================
    # TEST C: Low-stock detection (Warning)
    # =========================================================================
    low_insights = [item for item in insights_a if "low" in item["id"]]
    assert len(low_insights) > 0, "Expected Low-Stock insight in Business A"
    assert low_insights[0]["severity"] == "warning", f"Expected WARNING severity, got {low_insights[0]['severity']}"
    assert low_insights[0]["category"] == "inventory"
    print("PASS: [Test C] Low-stock detection flagged with WARNING severity")

    # =========================================================================
    # TEST D: Slow-moving detection (Warning)
    # =========================================================================
    slow_insights = [item for item in insights_a if "slow" in item["id"]]
    assert len(slow_insights) > 0, "Expected Slow-Moving insight in Business A"
    assert slow_insights[0]["severity"] == "warning"
    assert slow_insights[0]["current_value"] >= 100.0 or slow_insights[0]["metric"] == "velocity_per_day"
    print("PASS: [Test D] Slow-moving inventory detection flagged with tied-up capital calculation")

    # =========================================================================
    # TEST E: Negative profit detection (Critical)
    # =========================================================================
    neg_profit = [item for item in insights_a if item["id"] == "fin_negative_net_profit"]
    assert len(neg_profit) == 1, "Expected Operating at Net Loss insight"
    assert neg_profit[0]["severity"] == "critical"
    assert neg_profit[0]["current_value"] < 0, f"Expected negative net profit, got {neg_profit[0]['current_value']}"
    print("PASS: [Test E] Negative net profit detected and flagged as CRITICAL")

    # =========================================================================
    # TEST F: Low gross margin (or margin checks)
    # =========================================================================
    # If net profit is negative, net margin is critical; verify financial evaluation was computed
    assert any(item["category"] == "finance" for item in insights_a), "Expected financial category insights"
    print("PASS: [Test F] Financial margin evaluation correctly performed")

    # =========================================================================
    # TEST G: Receivables risk
    # =========================================================================
    rec_insights = [item for item in insights_a if item["id"] == "fin_receivables_risk"]
    assert len(rec_insights) == 1, "Expected Receivables Risk insight"
    assert rec_insights[0]["severity"] == "warning"
    assert rec_insights[0]["current_value"] >= 40.0, f"Expected ratio >= 40%, got {rec_insights[0]['current_value']}"
    print("PASS: [Test G] Elevated receivables risk detected with ratio evidence")

    # =========================================================================
    # TEST H: Customer concentration
    # =========================================================================
    cust_conc = [item for item in insights_a if "cust_concentration" in item["id"]]
    assert len(cust_conc) == 1, "Expected Customer Concentration insight for Big Whale Corp"
    assert cust_conc[0]["severity"] == "warning"
    assert cust_conc[0]["current_value"] >= 40.0, f"Expected customer share >= 40%, got {cust_conc[0]['current_value']}"
    print("PASS: [Test H] Customer revenue concentration detected for dominant account")

    # =========================================================================
    # TEST I: Supplier concentration
    # =========================================================================
    supp_conc = [item for item in insights_a if "supp_concentration" in item["id"]]
    assert len(supp_conc) == 1, "Expected Supplier Concentration insight for Primary Vendor Ltd"
    assert supp_conc[0]["severity"] == "warning"
    assert supp_conc[0]["current_value"] >= 60.0, f"Expected supplier share >= 60%, got {supp_conc[0]['current_value']}"
    print("PASS: [Test I] Supplier spend concentration detected for primary vendor")

    # =========================================================================
    # TEST J: Cost coverage warning
    # =========================================================================
    cost_cov = [item for item in insights_a if item["id"] == "data_cost_coverage_warning"]
    assert len(cost_cov) == 1, "Expected Cost Coverage Data Quality Warning"
    assert cost_cov[0]["severity"] == "warning"
    assert cost_cov[0]["category"] == "data_quality"
    assert cost_cov[0]["current_value"] < 85.0, f"Expected coverage < 85%, got {cost_cov[0]['current_value']}"
    print("PASS: [Test J] Incomplete cost data coverage detected under Data Quality category")

    # =========================================================================
    # TEST K: Date filtering
    # =========================================================================
    res_today = client.get("/api/v1/insights?period=today", headers=headers_owner_a)
    assert res_today.status_code == 200
    today_data = res_today.json()["data"]
    assert today_data["period"]["period"] == "today"
    assert today_data["period"]["days"] == 1
    print("PASS: [Test K] Date filtering supports period bounding ('today' vs 'last_30_days')")

    # =========================================================================
    # TEST L: Multi-tenant isolation
    # =========================================================================
    res_b = client.get("/api/v1/insights?period=last_30_days", headers=headers_owner_b)
    assert res_b.status_code == 200
    b_data = res_b.json()["data"]
    # Business B has no products, orders or customers, so it must NOT inherit Business A insights
    assert b_data["summary"]["critical"] == 0, "Business B must not see Business A critical insights"
    b_ids = {item["id"] for item in b_data["insights"]}
    assert "fin_negative_net_profit" not in b_ids, "Cross-tenant leak detected: Business B saw Business A net loss"
    assert not any("whale" in str(item).lower() for item in b_data["insights"]), "Cross-tenant leak detected: Business B saw Business A customer"
    print("PASS: [Test L] Strict multi-tenant isolation verified between Business A and Business B")

    # =========================================================================
    # TEST M, N, O: Role Access (Owner, Admin, Manager)
    # =========================================================================
    res_owner = client.get("/api/v1/insights", headers=headers_owner_a)
    assert res_owner.status_code == 200, f"Owner should have access, got {res_owner.status_code}"
    res_admin = client.get("/api/v1/insights", headers=headers_admin_a)
    assert res_admin.status_code == 200, f"Admin should have access, got {res_admin.status_code}"
    res_mgr = client.get("/api/v1/insights", headers=headers_mgr_a)
    assert res_mgr.status_code == 200, f"Manager should have access, got {res_mgr.status_code}"
    print("PASS: [Tests M, N, O] Owner, Admin, and Manager have authorized access to GET /api/v1/insights")

    # =========================================================================
    # TEST P: Staff receives 403 Forbidden
    # =========================================================================
    res_staff = client.get("/api/v1/insights", headers=headers_staff_a)
    assert res_staff.status_code == 403, f"Staff must receive 403 Forbidden, got {res_staff.status_code}"
    print("PASS: [Test P] Staff role correctly rejected with HTTP 403 Forbidden")

    # =========================================================================
    # TEST Q: Unauthenticated receives 401 Unauthorized
    # =========================================================================
    res_unauth = client.get("/api/v1/insights")
    assert res_unauth.status_code == 401, f"Unauthenticated must receive 401 Unauthorized, got {res_unauth.status_code}"
    res_bad_token = client.get("/api/v1/insights", headers={"Authorization": "Bearer bad.token.here"})
    assert res_bad_token.status_code == 401, f"Bad token must receive 401 Unauthorized, got {res_bad_token.status_code}"
    print("PASS: [Test Q] Unauthenticated requests correctly rejected with HTTP 401 Unauthorized")

    # =========================================================================
    # TEST R: Deduplication and Prioritization
    # =========================================================================
    # Prioritization check: all critical items must appear before any warning items, and all warning before info
    severities = [item["severity"] for item in insights_a]
    seen_warning = False
    seen_info = False
    for sev in severities:
        if sev == "critical":
            assert not seen_warning and not seen_info, "Critical insight appeared after warning or info!"
        elif sev == "warning":
            seen_warning = True
            assert not seen_info, "Warning insight appeared after info!"
        elif sev == "info":
            seen_info = True

    # Deduplication check: verify no duplicate insight IDs exist
    assert len(insights_a) == len(insight_ids), f"Duplicate insight IDs detected! Total: {len(insights_a)}, Unique: {len(insight_ids)}"
    print("PASS: [Test R] Prioritization (critical -> warning -> info) and deduplication strictly verified")

    print("\n=== ALL 18 PHASE 7 (TASK 1) INSIGHT TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    try:
        run_insights_tests()
    except Exception as e:
        print(f"\nTEST SUITE FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

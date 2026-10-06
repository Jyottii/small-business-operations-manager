import sys
import os
import io
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
from app.models.branch import Branch
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.stock_transfer import StockTransfer, StockTransferItem, StockTransferStatus
from app.models.goal import BusinessGoal
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.order import Order
from app.models.purchase_order import PurchaseOrder
from app.models.expense import Expense
from app.models.document import Document
from app.core.security import hash_password, create_access_token

client = TestClient(app)

def run_phase8_tests():
    print("=== STARTING PHASE 8 ADVANCED FEATURES TEST SUITE ===")
    db = SessionLocal()

    suffix = uuid.uuid4().hex[:6]
    pwd_plain = "Phase8Pass123!"
    pwd_hash = hash_password(pwd_plain)

    # 1. SETUP: Businesses A & B
    biz_a = Business(name=f"Phase8 Biz A {suffix}", legal_name=f"Phase8 Biz A Corp {suffix}")
    biz_b = Business(name=f"Phase8 Biz B {suffix}", legal_name=f"Phase8 Biz B Corp {suffix}")
    db.add_all([biz_a, biz_b])
    db.commit()
    db.refresh(biz_a)
    db.refresh(biz_b)

    wh_a1 = Warehouse(business_id=biz_a.id, name="Central Hub", code=f"WH-C-{suffix}")
    wh_a2 = Warehouse(business_id=biz_a.id, name="Downtown Store", code=f"WH-D-{suffix}")
    wh_b = Warehouse(business_id=biz_b.id, name="Biz B Warehouse", code=f"WH-B-{suffix}")
    db.add_all([wh_a1, wh_a2, wh_b])
    db.commit()
    db.refresh(wh_a1)
    db.refresh(wh_a2)
    db.refresh(wh_b)

    # Users
    u_owner_a = User(business_id=biz_a.id, name="Owner A", email=f"owner_{suffix}@a.com", password_hash=pwd_hash, role="Owner", is_active=True)
    u_staff_a = User(business_id=biz_a.id, name="Staff A", email=f"staff_{suffix}@a.com", password_hash=pwd_hash, role="Staff", is_active=True)
    u_owner_b = User(business_id=biz_b.id, name="Owner B", email=f"owner_{suffix}@b.com", password_hash=pwd_hash, role="Owner", is_active=True)
    db.add_all([u_owner_a, u_staff_a, u_owner_b])
    db.commit()
    db.refresh(u_owner_a)
    db.refresh(u_staff_a)
    db.refresh(u_owner_b)

    token_owner_a = create_access_token({"sub": u_owner_a.id})
    token_staff_a = create_access_token({"sub": u_staff_a.id})
    token_owner_b = create_access_token({"sub": u_owner_b.id})

    headers_a = {"Authorization": f"Bearer {token_owner_a}"}
    headers_staff = {"Authorization": f"Bearer {token_staff_a}"}
    headers_b = {"Authorization": f"Bearer {token_owner_b}"}

    # Products & Inventory for Biz A
    prod_a = Product(
        business_id=biz_a.id,
        sku=f"SKU-A-{suffix}",
        barcode=f"BARCODE-{suffix}",
        name=f"Laptop Pro {suffix}",
        cost_price=Decimal("800.00"),
        selling_price=Decimal("1200.00"),
        reorder_level=Decimal("5.0")
    )
    db.add(prod_a)
    db.commit()
    db.refresh(prod_a)

    inv_a1 = Inventory(
        product_id=prod_a.id,
        warehouse_id=wh_a1.id,
        quantity=Decimal("50.0"),
        reserved_quantity=Decimal("0.0"),
        reorder_level=Decimal("5.0")
    )
    db.add(inv_a1)
    db.commit()

    # -------------------------------------------------------------
    # TEST 1: Branches CRUD & Tenant Isolation & RBAC
    # -------------------------------------------------------------
    print("Testing Priority 1: Branches API & Isolation...")
    # Staff cannot create branch (403)
    res_staff = client.post("/api/v1/branches", json={"code": "BR-MAIN", "name": "Main Street Branch"}, headers=headers_staff)
    assert res_staff.status_code == 403, f"Expected 403 for staff, got {res_staff.status_code}"

    # Owner creates branch
    res_create = client.post("/api/v1/branches", json={"code": "BR-MAIN", "name": "Main Street Branch", "city": "Metropolis"}, headers=headers_a)
    assert res_create.status_code == 201, f"Expected 201, got {res_create.status_code}: {res_create.text}"
    branch_id = res_create.json()["data"]["id"]

    # Duplicate code should fail (400)
    res_dup = client.post("/api/v1/branches", json={"code": "BR-MAIN", "name": "Duplicate Branch"}, headers=headers_a)
    assert res_dup.status_code == 400

    # Biz B cannot see Biz A branch (tenant isolation)
    res_get_b = client.get(f"/api/v1/branches/{branch_id}", headers=headers_b)
    assert res_get_b.status_code == 404

    # Biz A can list branches
    res_list = client.get("/api/v1/branches", headers=headers_a)
    assert res_list.status_code == 200
    assert any(b["id"] == branch_id for b in res_list.json()["data"])
    print("[PASS] Branch API & Tenant Isolation passed")

    # -------------------------------------------------------------
    # TEST 2: Warehouse Summary & Stock Transfers
    # -------------------------------------------------------------
    print("Testing Priority 2: Warehouse Improvements & Stock Transfers...")
    # Link warehouse to branch
    res_wh_update = client.put(f"/api/v1/warehouses/{wh_a1.id}", json={"branch_id": branch_id}, headers=headers_a)
    assert res_wh_update.status_code == 200
    assert res_wh_update.json()["data"]["branch_id"] == branch_id

    # Warehouse Summary
    res_summary = client.get(f"/api/v1/warehouses/{wh_a1.id}/summary", headers=headers_a)
    assert res_summary.status_code == 200
    summary_data = res_summary.json()["data"]
    assert summary_data["total_stock"] == 50
    assert summary_data["total_valuation"] == 40000.0  # 50 * 800
    assert summary_data["low_stock_count"] == 0

    # Stock Transfer: create transfer from WH1 to WH2 for 10 units
    res_trf = client.post("/api/v1/stock-transfers", json={
        "source_warehouse_id": wh_a1.id,
        "destination_warehouse_id": wh_a2.id,
        "notes": "Transfer 10 laptops to store",
        "items": [{"product_id": prod_a.id, "quantity": 10.0}]
    }, headers=headers_a)
    assert res_trf.status_code == 201, f"Expected 201, got {res_trf.text}"
    trf_id = res_trf.json()["data"]["id"]
    assert res_trf.json()["data"]["status"] == "Pending"

    # Advance to In Transit
    res_transit = client.post(f"/api/v1/stock-transfers/{trf_id}/status", json={"status": "In Transit"}, headers=headers_a)
    assert res_transit.status_code == 200
    assert res_transit.json()["data"]["status"] == "In Transit"

    # Complete Stock Transfer (atomic inventory updates)
    res_comp = client.post(f"/api/v1/stock-transfers/{trf_id}/status", json={"status": "Completed"}, headers=headers_a)
    assert res_comp.status_code == 200
    assert res_comp.json()["data"]["status"] == "Completed"

    # Verify inventory was adjusted atomically
    db.expire_all()
    inv_src = db.query(Inventory).filter(Inventory.product_id == prod_a.id, Inventory.warehouse_id == wh_a1.id).first()
    inv_dst = db.query(Inventory).filter(Inventory.product_id == prod_a.id, Inventory.warehouse_id == wh_a2.id).first()
    assert float(inv_src.quantity) == 40.0, f"Expected 40.0 at source, got {inv_src.quantity}"
    assert float(inv_dst.quantity) == 10.0, f"Expected 10.0 at destination, got {inv_dst.quantity}"

    # Verify stock movement records created
    movements = db.query(StockMovement).filter(StockMovement.reference_id == trf_id).all()
    assert len(movements) == 2, f"Expected 2 movements (OUT and IN), got {len(movements)}"
    print("[PASS] Warehouse Summary & Atomic Stock Transfer passed")

    # -------------------------------------------------------------
    # TEST 3: Barcode Lookup
    # -------------------------------------------------------------
    print("Testing Priority 4: Barcode Lookup...")
    res_bc = client.get(f"/api/v1/products/barcode/{prod_a.barcode}", headers=headers_a)
    assert res_bc.status_code == 200
    assert res_bc.json()["data"]["sku"] == prod_a.sku

    # Biz B cannot see Biz A barcode
    res_bc_b = client.get(f"/api/v1/products/barcode/{prod_a.barcode}", headers=headers_b)
    assert res_bc_b.status_code == 404
    print("[PASS] Barcode Lookup passed")

    # -------------------------------------------------------------
    # TEST 4: Universal Search
    # -------------------------------------------------------------
    print("Testing Priority 3: Universal Search...")
    res_search = client.get(f"/api/v1/search?q=Laptop", headers=headers_a)
    assert res_search.status_code == 200
    search_data = res_search.json()["data"]
    assert search_data["total_results"] >= 1
    assert any(r["category"] == "product" and r["id"] == prod_a.id for r in search_data["results"])

    # Search isolated from Biz B
    res_search_b = client.get(f"/api/v1/search?q=Laptop", headers=headers_b)
    assert res_search_b.status_code == 200
    assert not any(r["id"] == prod_a.id for r in res_search_b.json()["data"]["results"])
    print("[PASS] Universal Search passed")

    # -------------------------------------------------------------
    # TEST 5: Reports & CSV Export
    # -------------------------------------------------------------
    print("Testing Priority 5: Reports & CSV Export...")
    # Add an order for report verification
    cust = Customer(business_id=biz_a.id, name=f"Alice {suffix}", email=f"alice_{suffix}@test.com")
    db.add(cust)
    db.commit()
    db.refresh(cust)

    ord_test = Order(
        business_id=biz_a.id,
        customer_id=cust.id,
        order_number=f"ORD-REP-{suffix}",
        total_amount=Decimal("1200.00"),
        status="COMPLETED"
    )
    db.add(ord_test)
    db.commit()

    res_rep_sales = client.get("/api/v1/reports/sales", headers=headers_a)
    assert res_rep_sales.status_code == 200
    assert res_rep_sales.json()["data"]["total_revenue"] >= 1200.0

    res_rep_inv = client.get("/api/v1/reports/inventory", headers=headers_a)
    assert res_rep_inv.status_code == 200
    assert res_rep_inv.json()["data"]["total_stock"] == 50

    # CSV Export
    res_csv = client.get("/api/v1/reports/export?report_type=sales", headers=headers_a)
    assert res_csv.status_code == 200
    assert res_csv.headers["content-type"].startswith("text/csv")
    assert f"ORD-REP-{suffix}" in res_csv.text

    # CSV Inventory Export
    res_csv_inv = client.get("/api/v1/reports/export?report_type=inventory", headers=headers_a)
    assert res_csv_inv.status_code == 200
    assert prod_a.sku in res_csv_inv.text
    print("[PASS] Reports & CSV Export passed")

    # -------------------------------------------------------------
    # TEST 6: Document Vault
    # -------------------------------------------------------------
    print("Testing Priority 6: Document Vault...")
    file_content = b"Sample document content for phase 8 verification."
    files = {"file": ("contract.pdf", io.BytesIO(file_content), "application/pdf")}
    res_up = client.post("/api/v1/documents/upload", files=files, data={"name": "Signed Contract", "document_type": "Legal"}, headers=headers_a)
    assert res_up.status_code == 201, f"Expected 201, got {res_up.status_code}: {res_up.text}"
    doc_id = res_up.json()["data"]["id"]

    # Download document
    res_down = client.get(f"/api/v1/documents/{doc_id}/download", headers=headers_a)
    assert res_down.status_code == 200
    assert res_down.content == file_content

    # Biz B cannot download Biz A's document
    res_down_b = client.get(f"/api/v1/documents/{doc_id}/download", headers=headers_b)
    assert res_down_b.status_code == 404

    # Delete document
    res_del = client.delete(f"/api/v1/documents/{doc_id}", headers=headers_a)
    assert res_del.status_code == 200
    print("[PASS] Document Vault passed")

    # -------------------------------------------------------------
    # TEST 7: Goals & Targets
    # -------------------------------------------------------------
    print("Testing Priority 8: Goals & Targets API...")
    res_goal = client.post("/api/v1/goals", json={
        "title": "Q1 Revenue Target",
        "metric": "TOTAL_REVENUE",
        "target_value": 2400.0,
        "period": "QUARTERLY"
    }, headers=headers_a)
    assert res_goal.status_code == 201, f"Expected 201, got {res_goal.text}"
    goal_data = res_goal.json()["data"]
    assert goal_data["current_value"] >= 1200.0
    assert goal_data["progress_percent"] == 50.0  # 1200 / 2400 = 50%
    assert goal_data["status"] == "AT_RISK"  # < 70%

    goal_id = goal_data["id"]
    # Biz B cannot see goal
    res_goal_b = client.get(f"/api/v1/goals/{goal_id}", headers=headers_b)
    assert res_goal_b.status_code == 404
    print("[PASS] Goals & Targets API passed")

    # -------------------------------------------------------------
    # TEST 8: Calendar Events
    # -------------------------------------------------------------
    print("Testing Priority 9: Calendar Events...")
    res_cal = client.get("/api/v1/calendar/events", headers=headers_a)
    assert res_cal.status_code == 200
    events = res_cal.json()["data"]
    assert isinstance(events, list)
    print("[PASS] Calendar Events passed")

    print("\nALL PHASE 8 BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_phase8_tests()

import sys
import os
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.business import Business
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.payment import Payment
from app.models.return_order import Return, ReturnItem
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.services.inventory_service import InventoryService

client = TestClient(app)

def run_tests():
    print("=== STARTING PHASE 4 END-TO-END WORKFLOW TESTS ===")
    db = SessionLocal()
    
    # 1. Get or create seeded business
    biz = db.query(Business).first()
    assert biz is not None, "No business found in database"
    biz_id = biz.id

    # Authenticate as business Owner
    from app.models.user import User
    from app.core.security import hash_password, create_access_token
    owner = db.query(User).filter(User.business_id == biz_id, User.role == "Owner").first()
    if not owner:
        owner = User(
            business_id=biz_id,
            name="Workflow Owner",
            email=f"wf_owner_{biz_id[:8]}@example.com",
            password_hash=hash_password("Password123!"),
            role="Owner",
            is_active=True
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

    token = create_access_token({"sub": owner.id, "business_id": biz_id, "role": owner.role})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Business-ID": biz_id
    }
    print(f"Using business ID: {biz_id} (Authenticated as {owner.name}, Role: {owner.role})")

    # 2. Get or create warehouse
    wh = db.query(Warehouse).filter(Warehouse.business_id == biz_id).first()
    if not wh:
        wh = Warehouse(business_id=biz_id, name="Main Warehouse", code="WH-MAIN")
        db.add(wh)
        db.commit()
        db.refresh(wh)
    wh_id = wh.id
    print(f"Using warehouse ID: {wh_id}")

    # ==========================================
    # TEST A: SALE (Inventory deduction & Stock movement)
    # ==========================================
    print("\n--- TEST A: SALE ---")
    # Create product
    res = client.post("/api/v1/products", json={
        "name": "Test Product A",
        "sku": f"SKU-TEST-A-{os.urandom(3).hex().upper()}",
        "selling_price": 100.0,
        "cost_price": 50.0,
        "tax_rate": 0.0,
        "reorder_level": 2.0
    }, headers=headers)
    assert res.status_code == 200, res.text
    prod_a_id = res.json()["data"]["id"]

    # Set inventory = 10
    res = client.post("/api/v1/inventory/adjust", json={
        "product_id": prod_a_id,
        "warehouse_id": wh_id,
        "quantity_change": 10.0,
        "movement_type": "Stock In",
        "notes": "Initial stock setup"
    }, headers=headers)
    assert res.status_code == 200, res.text
    assert float(res.json()["data"]["quantity"]) == 10.0

    # Create sale qty = 3
    res = client.post("/api/v1/orders", json={
        "warehouse_id": wh_id,
        "items": [{"product_id": prod_a_id, "quantity": 3.0, "discount": 0.0}]
    }, headers=headers)
    assert res.status_code == 200, res.text
    order_a = res.json()["data"]
    order_a_id = order_a["id"]
    assert float(order_a["total"]) == 300.0

    # Verify inventory is 7
    inv = db.query(Inventory).filter(Inventory.product_id == prod_a_id, Inventory.warehouse_id == wh_id).first()
    assert float(inv.quantity) == 7.0, f"Expected 7, got {inv.quantity}"

    # Verify stock movement = -3
    movement = db.query(StockMovement).filter(StockMovement.reference_id == order_a_id).first()
    assert movement is not None
    assert float(movement.quantity) == -3.0
    assert movement.movement_type == "SALE"
    print("[PASS] TEST A PASSED: Inventory reduced from 10 to 7, stock movement created (-3).")

    # ==========================================
    # TEST B: INSUFFICIENT STOCK
    # ==========================================
    print("\n--- TEST B: INSUFFICIENT STOCK ---")
    # Product with inventory = 2
    res = client.post("/api/v1/products", json={
        "name": "Test Product B",
        "sku": f"SKU-TEST-B-{os.urandom(3).hex().upper()}",
        "selling_price": 50.0,
        "cost_price": 25.0,
        "tax_rate": 0.0
    }, headers=headers)
    prod_b_id = res.json()["data"]["id"]

    client.post("/api/v1/inventory/adjust", json={
        "product_id": prod_b_id,
        "warehouse_id": wh_id,
        "quantity_change": 2.0,
        "movement_type": "Stock In"
    }, headers=headers)

    # Attempt sale = 5 (should be rejected)
    res = client.post("/api/v1/orders", json={
        "warehouse_id": wh_id,
        "items": [{"product_id": prod_b_id, "quantity": 5.0, "discount": 0.0}]
    }, headers=headers)
    assert res.status_code == 400, f"Expected 400, got {res.status_code}"
    assert "Insufficient stock" in res.json().get("detail", "")

    # Inventory must remain 2
    inv_b = db.query(Inventory).filter(Inventory.product_id == prod_b_id, Inventory.warehouse_id == wh_id).first()
    assert float(inv_b.quantity) == 2.0

    # No order or stock movement for product B sale
    movements_b = db.query(StockMovement).filter(StockMovement.product_id == prod_b_id, StockMovement.movement_type == "SALE").all()
    assert len(movements_b) == 0
    print("[PASS] TEST B PASSED: Insufficient stock rejected, inventory preserved at 2, no partial order.")

    # ==========================================
    # TEST C: PAYMENT (Partial and Full)
    # ==========================================
    print("\n--- TEST C: PAYMENT ---")
    # Create product for $1000 order
    res = client.post("/api/v1/products", json={
        "name": "Test Product C",
        "sku": f"SKU-TEST-C-{os.urandom(3).hex().upper()}",
        "selling_price": 1000.0,
        "cost_price": 500.0,
        "tax_rate": 0.0
    }, headers=headers)
    prod_c_id = res.json()["data"]["id"]

    client.post("/api/v1/inventory/adjust", json={
        "product_id": prod_c_id,
        "warehouse_id": wh_id,
        "quantity_change": 10.0,
        "movement_type": "Stock In"
    }, headers=headers)

    res = client.post("/api/v1/orders", json={
        "warehouse_id": wh_id,
        "items": [{"product_id": prod_c_id, "quantity": 1.0, "discount": 0.0}]
    }, headers=headers)
    order_c = res.json()["data"]
    order_c_id = order_c["id"]
    assert float(order_c["total"]) == 1000.0

    # Payment = 400
    res = client.post(f"/api/v1/orders/{order_c_id}/payments", json={
        "amount": 400.0,
        "payment_method": "Cash",
        "transaction_reference": "REF-PARTIAL"
    }, headers=headers)
    assert res.status_code == 200, res.text

    # Verify order state: paid = 400, balance = 600, Partially Paid
    res = client.get(f"/api/v1/orders/{order_c_id}", headers=headers)
    order_updated = res.json()["data"]
    assert float(order_updated["amount_paid"]) == 400.0
    assert float(order_updated["balance_due"]) == 600.0
    assert order_updated["payment_status"] == "Partially Paid"

    # Payment = 600
    res = client.post(f"/api/v1/orders/{order_c_id}/payments", json={
        "amount": 600.0,
        "payment_method": "UPI",
        "transaction_reference": "REF-FULL"
    }, headers=headers)
    assert res.status_code == 200, res.text

    # Verify order state: paid = 1000, balance = 0, Paid
    res = client.get(f"/api/v1/orders/{order_c_id}", headers=headers)
    order_updated = res.json()["data"]
    assert float(order_updated["amount_paid"]) == 1000.0
    assert float(order_updated["balance_due"]) == 0.0
    assert order_updated["payment_status"] == "Paid"
    print("[PASS] TEST C PASSED: Partial payment (400) updated balance to 600, full payment (600) updated balance to 0 and status to Paid.")

    # ==========================================
    # TEST D: PURCHASE RECEIVING (Partial and Full)
    # ==========================================
    print("\n--- TEST D: PURCHASE RECEIVING ---")
    # Supplier
    res = client.post("/api/v1/suppliers", json={
        "name": "Supplier D",
        "company_name": "Supplier D Corp",
        "email": "suppd@example.com"
    }, headers=headers)
    supp_d_id = res.json()["data"]["id"]

    # Product D
    res = client.post("/api/v1/products", json={
        "name": "Test Product D",
        "sku": f"SKU-TEST-D-{os.urandom(3).hex().upper()}",
        "selling_price": 50.0,
        "cost_price": 20.0,
        "tax_rate": 0.0
    }, headers=headers)
    prod_d_id = res.json()["data"]["id"]

    # Initial inventory = 0
    inv_d_before = InventoryService.get_inventory(db, biz_id, prod_d_id, wh_id)
    inv_d_qty_before = float(inv_d_before.quantity) if inv_d_before else 0.0

    # PO with 100 units
    res = client.post("/api/v1/purchase-orders", json={
        "supplier_id": supp_d_id,
        "warehouse_id": wh_id,
        "items": [{
            "product_id": prod_d_id,
            "quantity_ordered": 100.0,
            "unit_cost": 20.0
        }]
    }, headers=headers)
    assert res.status_code == 200, res.text
    po_d = res.json()["data"]
    po_d_id = po_d["id"]
    assert po_d["status"] == "Ordered"

    # Receive 40
    res = client.post(f"/api/v1/purchase-orders/{po_d_id}/receive", json={
        "items": {prod_d_id: 40.0},
        "notes": "First partial batch"
    }, headers=headers)
    assert res.status_code == 200, res.text
    po_d_received = res.json()["data"]
    assert po_d_received["status"] == "Partially Received"
    item_d = po_d_received["purchase_items"][0]
    assert float(item_d["quantity_received"]) == 40.0

    # Verify inventory += 40
    db.expire_all()
    inv_d = db.query(Inventory).filter(Inventory.product_id == prod_d_id, Inventory.warehouse_id == wh_id).first()
    assert float(inv_d.quantity) == inv_d_qty_before + 40.0

    # Receive remaining 60
    res = client.post(f"/api/v1/purchase-orders/{po_d_id}/receive", json={
        "items": {prod_d_id: 60.0},
        "notes": "Final batch"
    }, headers=headers)
    assert res.status_code == 200, res.text
    po_d_final = res.json()["data"]
    assert po_d_final["status"] == "Received"
    item_d = po_d_final["purchase_items"][0]
    assert float(item_d["quantity_received"]) == 100.0

    # Verify inventory += 60 (total +100)
    db.expire_all()
    inv_d = db.query(Inventory).filter(Inventory.product_id == prod_d_id, Inventory.warehouse_id == wh_id).first()
    assert float(inv_d.quantity) == inv_d_qty_before + 100.0
    print("[PASS] TEST D PASSED: Partial receive (40) updated PO to 'Partially Received' & inv +40; full receive (60) updated status to 'Received' & inv +60.")

    # ==========================================
    # TEST E: OVER-RECEIVING
    # ==========================================
    print("\n--- TEST E: OVER-RECEIVING ---")
    # PO D is already 100/100 received. Attempt to receive 1 more.
    res = client.post(f"/api/v1/purchase-orders/{po_d_id}/receive", json={
        "items": {prod_d_id: 1.0}
    }, headers=headers)
    assert res.status_code == 400, f"Expected 400, got {res.status_code}"
    print("[PASS] TEST E PASSED: Over-receiving rejected by server.")

    # ==========================================
    # TEST F: RETURN
    # ==========================================
    print("\n--- TEST F: RETURN ---")
    # Product F
    res = client.post("/api/v1/products", json={
        "name": "Test Product F",
        "sku": f"SKU-TEST-F-{os.urandom(3).hex().upper()}",
        "selling_price": 50.0,
        "cost_price": 20.0,
        "tax_rate": 0.0
    }, headers=headers)
    prod_f_id = res.json()["data"]["id"]

    client.post("/api/v1/inventory/adjust", json={
        "product_id": prod_f_id,
        "warehouse_id": wh_id,
        "quantity_change": 10.0,
        "movement_type": "Stock In"
    }, headers=headers)

    # Sell 5
    res = client.post("/api/v1/orders", json={
        "warehouse_id": wh_id,
        "items": [{"product_id": prod_f_id, "quantity": 5.0, "discount": 0.0}]
    }, headers=headers)
    order_f_id = res.json()["data"]["id"]

    # Stock before return = 5
    db.expire_all()
    inv_f_before = db.query(Inventory).filter(Inventory.product_id == prod_f_id, Inventory.warehouse_id == wh_id).first()
    assert float(inv_f_before.quantity) == 5.0

    # Return 2
    res = client.post(f"/api/v1/orders/{order_f_id}/return", json={
        "items": [{"product_id": prod_f_id, "quantity": 2.0, "reason": "Customer Return"}],
        "notes": "Defective box"
    }, headers=headers)
    assert res.status_code == 200, res.text
    ret_f = res.json()["data"]
    assert float(ret_f["refund_amount"]) == 100.0 # 2 * 50.0

    # Verify inventory is now 7 (+2)
    db.expire_all()
    inv_f_after = db.query(Inventory).filter(Inventory.product_id == prod_f_id, Inventory.warehouse_id == wh_id).first()
    assert float(inv_f_after.quantity) == 7.0

    # Attempt another return of 4 (already returned 2, total sold was 5, 2+4 = 6 > 5) -> should reject!
    res = client.post(f"/api/v1/orders/{order_f_id}/return", json={
        "items": [{"product_id": prod_f_id, "quantity": 4.0}]
    }, headers=headers)
    assert res.status_code == 400, f"Expected 400, got {res.status_code}"
    print("[PASS] TEST F PASSED: Return of 2 accepted, inventory +2, refund calculated ($100), excess return of 4 rejected.")

    # ==========================================
    # TEST G: CUSTOMER CREDIT LIMIT VALIDATION
    # ==========================================
    print("\n--- TEST G: CUSTOMER CREDIT LIMIT VALIDATION ---")
    # Customer with credit limit of $150
    res = client.post("/api/v1/customers", json={
        "name": "Credit Customer",
        "email": "credit@example.com",
        "credit_limit": 150.0
    }, headers=headers)
    cust_g_id = res.json()["data"]["id"]

    # Attempt sale of $200 on credit (should fail)
    res = client.post("/api/v1/orders", json={
        "customer_id": cust_g_id,
        "warehouse_id": wh_id,
        "items": [{"product_id": prod_c_id, "quantity": 1.0, "discount": 0.0}] # $1000
    }, headers=headers)
    assert res.status_code == 400
    assert "credit limit exceeded" in res.json().get("detail", "").lower()
    print("[PASS] TEST G PASSED: Sale exceeding credit limit blocked.")

    # ==========================================
    # TEST H: AUDIT LOGS & NOTIFICATIONS
    # ==========================================
    print("\n--- TEST H: AUDIT LOGS & NOTIFICATIONS ---")
    res = client.get("/api/v1/audit-logs", headers=headers)
    assert res.status_code == 200
    logs = res.json()["data"]
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "ORDER_CREATED" in actions
    assert "PURCHASE_ORDER_RECEIVED" in actions
    assert "RETURN_PROCESSED" in actions

    res = client.get("/api/v1/notifications", headers=headers)
    assert res.status_code == 200
    notifs = res.json()["data"]
    assert len(notifs) > 0
    print("[PASS] TEST H PASSED: Audit logs and notifications generated and queried successfully.")

    print("\n=======================================================")
    print("ALL TESTS (A, B, C, D, E, F, G, H) PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == '__main__':
    run_tests()

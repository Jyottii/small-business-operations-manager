import sys
import os
import uuid
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.business import Business
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.core.security import hash_password, create_access_token

client = TestClient(app)

def run_rbac_tests():
    print("=== STARTING PHASE 5 (TASK 2) RBAC TEST SUITE ===")
    db = SessionLocal()

    suffix = uuid.uuid4().hex[:6]
    pwd_plain = "TestPass123!"
    pwd_hash = hash_password(pwd_plain)

    # -------------------------------------------------------------
    # SETUP: Create Business A with Owner, Admin, Manager, Staff
    # -------------------------------------------------------------
    biz_a = Business(name=f"RBAC Biz A {suffix}", legal_name=f"Biz A Corp {suffix}")
    db.add(biz_a)
    db.commit()
    db.refresh(biz_a)
    biz_a_id = biz_a.id

    # Warehouse for Biz A
    wh_a = Warehouse(business_id=biz_a_id, name="Biz A WH", code=f"WH-A-{suffix}")
    db.add(wh_a)
    db.commit()
    db.refresh(wh_a)

    # Users in Biz A
    u_owner = User(business_id=biz_a_id, name=f"Owner A {suffix}", email=f"owner_{suffix}@a.com", password_hash=pwd_hash, role="Owner", is_active=True)
    u_admin = User(business_id=biz_a_id, name=f"Admin A {suffix}", email=f"admin_{suffix}@a.com", password_hash=pwd_hash, role="Admin", is_active=True)
    u_manager = User(business_id=biz_a_id, name=f"Manager A {suffix}", email=f"mgr_{suffix}@a.com", password_hash=pwd_hash, role="Manager", is_active=True)
    u_staff = User(business_id=biz_a_id, name=f"Staff A {suffix}", email=f"staff_{suffix}@a.com", password_hash=pwd_hash, role="Staff", is_active=True)
    u_inactive = User(business_id=biz_a_id, name=f"Inactive A {suffix}", email=f"inact_{suffix}@a.com", password_hash=pwd_hash, role="Staff", is_active=False)
    db.add_all([u_owner, u_admin, u_manager, u_staff, u_inactive])
    db.commit()
    for u in [u_owner, u_admin, u_manager, u_staff, u_inactive]:
        db.refresh(u)

    def auth_headers(user: User):
        t = create_access_token({"sub": user.id, "business_id": user.business_id, "role": user.role})
        return {"Authorization": f"Bearer {t}"}

    owner_h = auth_headers(u_owner)
    admin_h = auth_headers(u_admin)
    mgr_h = auth_headers(u_manager)
    staff_h = auth_headers(u_staff)
    inactive_h = auth_headers(u_inactive)

    # Setup a Product in Biz A
    res_prod = client.post("/api/v1/products", headers=owner_h, json={
        "name": f"Test Prod {suffix}",
        "sku": f"SKU-{suffix}",
        "selling_price": 50.0,
        "cost_price": 25.0
    })
    assert res_prod.status_code == 200, res_prod.text
    prod_id = res_prod.json()["data"]["id"]

    # Stock inventory
    res_stock = client.post("/api/v1/inventory/adjust", headers=owner_h, json={
        "product_id": prod_id,
        "warehouse_id": wh_a.id,
        "quantity_change": 100,
        "movement_type": "INITIAL_STOCK"
    })
    assert res_stock.status_code == 200, res_stock.text

    # Setup Customer in Biz A
    res_cust = client.post("/api/v1/customers", headers=owner_h, json={
        "name": f"Cust A {suffix}",
        "email": f"cust_{suffix}@a.com"
    })
    assert res_cust.status_code == 200, res_cust.text
    cust_id = res_cust.json()["data"]["id"]

    # =============================================================
    # TEST A: AUTHENTICATION (Unauthenticated → 401)
    # =============================================================
    print("\n--- TEST A: Unauthenticated Requests Return 401 ---")
    unauth_endpoints = [
        ("GET", "/api/v1/products", None),
        ("POST", "/api/v1/products", {"name": "Fail", "sku": "FAIL-1", "selling_price": 10.0}),
        ("GET", "/api/v1/orders", None),
        ("POST", "/api/v1/orders", {"customer_id": cust_id, "items": [{"product_id": prod_id, "quantity": 1}]}),
        ("GET", "/api/v1/users", None),
        ("GET", "/api/v1/audit-logs", None),
        ("GET", "/api/v1/warehouses", None),
        ("GET", "/api/v1/suppliers", None),
        ("GET", "/api/v1/purchase-orders", None),
        ("GET", "/api/v1/expenses", None),
    ]
    for method, ep, body in unauth_endpoints:
        if method == "GET":
            r = client.get(ep)
        else:
            r = client.post(ep, json=body)
        assert r.status_code == 401, f"Expected 401 for unauthenticated {method} {ep}, got {r.status_code}"
    print("[PASS] Unauthenticated requests strictly return 401 Unauthorized.")

    # =============================================================
    # TEST F: INACTIVE USER (Token valid but is_active=False → 401)
    # =============================================================
    print("\n--- TEST F: Inactive User Token Rejection ---")
    r_inact = client.get("/api/v1/products", headers=inactive_h)
    assert r_inact.status_code == 401, f"Expected 401 for inactive user, got {r_inact.status_code}"
    assert "inactive" in r_inact.json()["detail"].lower()
    print("[PASS] Inactive user strictly rejected with 401 Unauthorized.")

    # =============================================================
    # TEST B: OWNER PERMISSIONS (Full Access)
    # =============================================================
    print("\n--- TEST B: Owner Allowed Operations ---")
    # 1. Update business settings (Owner only)
    r_biz_patch = client.patch(f"/api/v1/businesss/{biz_a_id}", headers=owner_h, json={"name": f"Renamed Biz {suffix}"})
    assert r_biz_patch.status_code == 200, f"Owner should update business: {r_biz_patch.text}"
    
    # 2. Create an Admin user
    r_create_admin = client.post("/api/v1/users", headers=owner_h, json={
        "name": f"New Admin {suffix}",
        "email": f"new_admin_{suffix}@a.com",
        "password": "Password123!",
        "role": "Admin"
    })
    assert r_create_admin.status_code == 201, f"Owner should create Admin: {r_create_admin.text}"
    created_admin_id = r_create_admin.json()["data"]["id"]

    # 3. Create Warehouse
    r_create_wh = client.post("/api/v1/warehouses", headers=owner_h, json={
        "name": f"Owner WH {suffix}",
        "code": f"WH-OWNER-{suffix}"
    })
    assert r_create_wh.status_code == 200, f"Owner should create warehouse: {r_create_wh.text}"

    # 4. View Audit Logs
    r_audit = client.get("/api/v1/audit-logs", headers=owner_h)
    assert r_audit.status_code == 200
    print("[PASS] Owner has full privileged access.")

    # =============================================================
    # TEST C: ADMIN PERMISSIONS & BOUNDARIES
    # =============================================================
    print("\n--- TEST C: Admin Allowed Operations & Owner-Only Denial ---")
    # Allowed: Create Manager and Staff
    r_admin_create_staff = client.post("/api/v1/users", headers=admin_h, json={
        "name": f"Admin Created Staff {suffix}",
        "email": f"adm_staff_{suffix}@a.com",
        "password": "Password123!",
        "role": "Staff"
    })
    assert r_admin_create_staff.status_code == 201, f"Admin should create staff: {r_admin_create_staff.text}"
    created_staff_id = r_admin_create_staff.json()["data"]["id"]

    # Allowed: Create Warehouse
    r_admin_wh = client.post("/api/v1/warehouses", headers=admin_h, json={
        "name": f"Admin WH {suffix}",
        "code": f"WH-ADM-{suffix}"
    })
    assert r_admin_wh.status_code == 200, f"Admin should create warehouse: {r_admin_wh.text}"

    # Allowed: View Audit Logs
    r_admin_audit = client.get("/api/v1/audit-logs", headers=admin_h)
    assert r_admin_audit.status_code == 200

    # DENIED (403): Admin cannot update business settings (Owner only)
    r_admin_biz_patch = client.patch(f"/api/v1/businesss/{biz_a_id}", headers=admin_h, json={"name": "Hacked Name"})
    assert r_admin_biz_patch.status_code == 403, f"Expected 403 for Admin business patch, got {r_admin_biz_patch.status_code}"

    # DENIED (403): Admin cannot create an Owner account
    r_admin_create_owner = client.post("/api/v1/users", headers=admin_h, json={
        "name": f"Hacked Owner {suffix}",
        "email": f"hacked_owner_{suffix}@a.com",
        "password": "Password123!",
        "role": "Owner"
    })
    assert r_admin_create_owner.status_code == 403, f"Expected 403 for Admin creating Owner, got {r_admin_create_owner.status_code}"

    # DENIED (403): Admin cannot promote another user to Owner
    r_admin_promote = client.patch(f"/api/v1/users/{created_staff_id}", headers=admin_h, json={"role": "Owner"})
    assert r_admin_promote.status_code == 403, f"Expected 403 for Admin promoting to Owner, got {r_admin_promote.status_code}"

    # DENIED (403): Admin cannot modify Owner account
    r_admin_edit_owner = client.patch(f"/api/v1/users/{u_owner.id}", headers=admin_h, json={"name": "Changed Owner"})
    assert r_admin_edit_owner.status_code == 403, f"Expected 403 for Admin modifying Owner, got {r_admin_edit_owner.status_code}"
    print("[PASS] Admin operational access allowed, Owner-only actions strictly denied (403).")

    # =============================================================
    # TEST D: MANAGER PERMISSIONS & BOUNDARIES
    # =============================================================
    print("\n--- TEST D: Manager Allowed Operations & Admin/Owner Denial ---")
    # Allowed: Create product
    r_mgr_prod = client.post("/api/v1/products", headers=mgr_h, json={
        "name": f"Manager Prod {suffix}",
        "sku": f"SKU-MGR-{suffix}",
        "selling_price": 75.0,
        "cost_price": 40.0
    })
    assert r_mgr_prod.status_code == 200, f"Manager should create product: {r_mgr_prod.text}"

    # Allowed: Adjust inventory
    r_mgr_adj = client.post("/api/v1/inventory/adjust", headers=mgr_h, json={
        "product_id": prod_id,
        "warehouse_id": wh_a.id,
        "quantity_change": 10,
        "movement_type": "ADJUSTMENT"
    })
    assert r_mgr_adj.status_code == 200, f"Manager should adjust inventory: {r_mgr_adj.text}"

    # Allowed: View audit logs
    r_mgr_audit = client.get("/api/v1/audit-logs", headers=mgr_h)
    assert r_mgr_audit.status_code == 200, f"Manager should view audit logs: {r_mgr_audit.text}"

    # DENIED (403): Manager cannot create user
    r_mgr_user = client.post("/api/v1/users", headers=mgr_h, json={
        "name": "Unauthorized User",
        "email": f"unauth_user_{suffix}@a.com",
        "password": "Password123!",
        "role": "Staff"
    })
    assert r_mgr_user.status_code == 403, f"Expected 403 for Manager creating user, got {r_mgr_user.status_code}"

    # DENIED (403): Manager cannot create warehouse (Owner/Admin only)
    r_mgr_wh = client.post("/api/v1/warehouses", headers=mgr_h, json={
        "name": "Manager WH",
        "code": "WH-MGR"
    })
    assert r_mgr_wh.status_code == 403, f"Expected 403 for Manager creating warehouse, got {r_mgr_wh.status_code}"

    # DENIED (403): Manager cannot update business settings
    r_mgr_biz = client.patch(f"/api/v1/businesss/{biz_a_id}", headers=mgr_h, json={"name": "Mgr Renamed"})
    assert r_mgr_biz.status_code == 403, f"Expected 403 for Manager updating business, got {r_mgr_biz.status_code}"
    print("[PASS] Manager operational access allowed, privileged actions strictly denied (403).")

    # =============================================================
    # TEST E: STAFF PERMISSIONS & PRIVILEGE BARRIERS
    # =============================================================
    print("\n--- TEST E: Staff Operations & Denied Privileged Endpoints ---")
    # Allowed: View products and inventory
    assert client.get("/api/v1/products", headers=staff_h).status_code == 200
    assert client.get("/api/v1/inventory", headers=staff_h).status_code == 200
    assert client.get("/api/v1/notifications", headers=staff_h).status_code == 200

    # Allowed: Create Customer at POS
    r_staff_cust = client.post("/api/v1/customers", headers=staff_h, json={
        "name": f"POS Customer {suffix}",
        "email": f"pos_cust_{suffix}@a.com"
    })
    assert r_staff_cust.status_code == 200, f"Staff should create customer: {r_staff_cust.text}"
    pos_cust_id = r_staff_cust.json()["data"]["id"]

    # Allowed: Create Order
    r_staff_order = client.post("/api/v1/orders", headers=staff_h, json={
        "customer_id": pos_cust_id,
        "items": [{"product_id": prod_id, "quantity": 1, "discount": 0.0}]
    })
    assert r_staff_order.status_code == 200, f"Staff should create order: {r_staff_order.text}"
    staff_order_id = r_staff_order.json()["data"]["id"]

    # Allowed: Record Payment for Order
    r_staff_pay = client.post(f"/api/v1/orders/{staff_order_id}/payments", headers=staff_h, json={
        "amount": 50.0,
        "payment_method": "Cash"
    })
    assert r_staff_pay.status_code == 200, f"Staff should record order payment: {r_staff_pay.text}"

    # Allowed: Process Return
    r_staff_ret = client.post(f"/api/v1/orders/{staff_order_id}/return", headers=staff_h, json={
        "items": [{"product_id": prod_id, "quantity": 1}],
        "reason": "Customer change of mind"
    })
    assert r_staff_ret.status_code == 200, f"Staff should process return: {r_staff_ret.text}"

    # DENIED (403): Staff cannot manually adjust inventory
    r_staff_adj = client.post("/api/v1/inventory/adjust", headers=staff_h, json={
        "product_id": prod_id,
        "warehouse_id": wh_a.id,
        "quantity_change": 5,
        "movement_type": "THEFT"
    })
    assert r_staff_adj.status_code == 403, f"Expected 403 for Staff inventory adjustment, got {r_staff_adj.status_code}"

    # DENIED (403): Staff cannot view audit logs
    r_staff_audit = client.get("/api/v1/audit-logs", headers=staff_h)
    assert r_staff_audit.status_code == 403, f"Expected 403 for Staff audit log read, got {r_staff_audit.status_code}"

    # DENIED (403): Staff cannot cancel finalized order
    r_staff_cancel = client.post(f"/api/v1/orders/{staff_order_id}/cancel", headers=staff_h)
    assert r_staff_cancel.status_code == 403, f"Expected 403 for Staff order cancel, got {r_staff_cancel.status_code}"

    # DENIED (403): Staff cannot view or create suppliers
    assert client.get("/api/v1/suppliers", headers=staff_h).status_code == 403
    assert client.post("/api/v1/suppliers", headers=staff_h, json={"name": "Sup"}).status_code == 403

    # DENIED (403): Staff cannot create or view purchase orders
    assert client.get("/api/v1/purchase-orders", headers=staff_h).status_code == 403
    assert client.post("/api/v1/purchase-orders", headers=staff_h, json={"items": []}).status_code == 403

    # DENIED (403): Staff cannot view expenses
    assert client.get("/api/v1/expenses", headers=staff_h).status_code == 403

    # DENIED (403): Staff cannot create product
    r_staff_prod = client.post("/api/v1/products", headers=staff_h, json={"name": "P", "sku": "P", "selling_price": 10.0})
    assert r_staff_prod.status_code == 403

    # DENIED (403): Staff cannot create user or warehouse
    assert client.post("/api/v1/users", headers=staff_h, json={"name": "U"}).status_code == 403
    assert client.post("/api/v1/warehouses", headers=staff_h, json={"name": "W"}).status_code == 403
    print("[PASS] Staff permissions correctly scoped to sales/POS; all privileged actions denied (403).")

    # =============================================================
    # TEST H: PRIVILEGE ESCALATION GUARDS
    # =============================================================
    print("\n--- TEST H: Privilege Escalation Prevention ---")
    # 1. Staff attempts to promote self to Admin via PATCH /api/v1/users/{id}
    r_self_promo = client.patch(f"/api/v1/users/{u_staff.id}", headers=staff_h, json={"role": "Admin"})
    assert r_self_promo.status_code == 403, f"Staff should get 403 modifying user: {r_self_promo.status_code}"

    # 2. Manager attempts to promote self to Owner via PATCH /api/v1/users/{id}
    r_mgr_promo = client.patch(f"/api/v1/users/{u_manager.id}", headers=mgr_h, json={"role": "Owner"})
    assert r_mgr_promo.status_code == 403, f"Manager should get 403 modifying user: {r_mgr_promo.status_code}"

    # 3. Admin attempts to modify own role to Owner
    r_adm_promo = client.patch(f"/api/v1/users/{u_admin.id}", headers=admin_h, json={"role": "Owner"})
    assert r_adm_promo.status_code == 403, f"Admin should get 403 promoting self to Owner: {r_adm_promo.status_code}"

    # 4. Public registration attempting to join existing business as Owner
    r_pub_owner = client.post("/api/v1/auth/register", json={
        "name": "Public Attacker",
        "email": f"attacker_{suffix}@domain.com",
        "password": "Password123!",
        "business_id": biz_a_id,
        "role": "Owner"
    })
    assert r_pub_owner.status_code == 403, f"Public registration for existing business as Owner must be rejected: {r_pub_owner.status_code}"

    # 5. Public registration attempting to join existing business as Admin
    r_pub_admin = client.post("/api/v1/auth/register", json={
        "name": "Public Attacker Admin",
        "email": f"attacker_admin_{suffix}@domain.com",
        "password": "Password123!",
        "business_id": biz_a_id,
        "role": "Admin"
    })
    assert r_pub_admin.status_code == 403, f"Public registration for existing business as Admin must be rejected: {r_pub_admin.status_code}"
    print("[PASS] Privilege escalation paths blocked across all vector points.")

    # =============================================================
    # TEST G: CROSS-BUSINESS ISOLATION
    # =============================================================
    print("\n--- TEST G: Cross-Business Tenant Isolation ---")
    # Create Business B with separate Owner
    biz_b = Business(name=f"RBAC Biz B {suffix}")
    db.add(biz_b)
    db.commit()
    db.refresh(biz_b)
    biz_b_id = biz_b.id

    u_owner_b = User(business_id=biz_b_id, name=f"Owner B {suffix}", email=f"owner_b_{suffix}@b.com", password_hash=pwd_hash, role="Owner", is_active=True)
    db.add(u_owner_b)
    db.commit()
    db.refresh(u_owner_b)
    owner_b_h = auth_headers(u_owner_b)

    # In Biz B, create a secret product
    r_prod_b = client.post("/api/v1/products", headers=owner_b_h, json={
        "name": f"Secret Product B {suffix}",
        "sku": f"SKU-B-{suffix}",
        "selling_price": 999.0
    })
    assert r_prod_b.status_code == 200
    prod_b_id = r_prod_b.json()["data"]["id"]

    # Owner A attempts to access Biz B product directly (even spoofing X-Business-ID: biz_b_id)
    r_leak_get = client.get(
        f"/api/v1/products/{prod_b_id}",
        headers={
            **owner_h,
            "X-Business-ID": biz_b_id
        }
    )
    assert r_leak_get.status_code == 404, f"Expected 404 accessing Biz B product from Biz A, got {r_leak_get.status_code}"

    # Owner A attempts to list products with X-Business-ID: biz_b_id spoofed
    r_leak_list = client.get(
        "/api/v1/products",
        headers={
            **owner_h,
            "X-Business-ID": biz_b_id
        }
    )
    assert r_leak_list.status_code == 200
    listed_prods = r_leak_list.json().get("data", [])
    assert not any(p["id"] == prod_b_id for p in listed_prods), "Cross-business product leak in listing!"

    # Owner A attempts to update Biz B product
    r_leak_patch = client.patch(
        f"/api/v1/products/{prod_b_id}",
        headers=owner_h,
        json={"name": "Hacked Product Name"}
    )
    assert r_leak_patch.status_code == 404
    print("[PASS] Cross-business isolation fully enforced against all token/header attacks.")

    db.close()
    print("\n=== ALL PHASE 5 (TASK 2) RBAC TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_rbac_tests()

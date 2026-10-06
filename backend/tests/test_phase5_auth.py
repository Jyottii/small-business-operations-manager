import sys
import os
import uuid

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.business import Business
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.customer import Customer
from app.models.audit_log import AuditLog

client = TestClient(app)

def run_tests():
    print("=== STARTING PHASE 5 (TASK 1) AUTH & USER FOUNDATION TESTS ===")
    db = SessionLocal()

    # -------------------------------------------------------------
    # 1. USER CREATION VIA REGISTRATION
    # -------------------------------------------------------------
    print("\n--- TEST 1: User Registration ---")
    unique_suffix = uuid.uuid4().hex[:6]
    owner_email = f"owner_{unique_suffix}@example.com"
    owner_password = "SecurePassword123!"

    # 1a. Register with business_name (New business, role Owner)
    res_reg_owner = client.post("/api/v1/auth/register", json={
        "name": f"Owner {unique_suffix}",
        "email": owner_email,
        "password": owner_password,
        "business_name": f"Test Business {unique_suffix}"
    })
    assert res_reg_owner.status_code == 201, f"Owner registration failed: {res_reg_owner.text}"
    owner_reg_data = res_reg_owner.json()
    assert "access_token" in owner_reg_data, "access_token expected in register response"
    owner_data = owner_reg_data["user"]
    biz_a_id = owner_data["business_id"]
    owner_user_id = owner_data["id"]
    assert owner_data["role"] == "Owner", f"Expected role Owner, got {owner_data['role']}"
    assert "password_hash" not in owner_data, "Password hash must not be in registration response"
    print(f"Registered owner: {owner_data['email']}, Biz: {biz_a_id}, Role: {owner_data['role']}")

    # 1b. Register staff member for existing business
    staff_email = f"staff_{unique_suffix}@example.com"
    staff_password = "StaffPassword123!"
    res_reg_staff = client.post("/api/v1/auth/register", json={
        "name": f"Staff {unique_suffix}",
        "email": staff_email,
        "password": staff_password,
        "business_id": biz_a_id,
        "role": "Staff"
    })
    assert res_reg_staff.status_code == 201, f"Staff registration failed: {res_reg_staff.text}"
    staff_reg_data = res_reg_staff.json()
    staff_data = staff_reg_data["user"]
    assert staff_data["business_id"] == biz_a_id
    assert staff_data["role"] == "Staff"
    print(f"Registered staff: {staff_data['email']}, Biz: {staff_data['business_id']}, Role: {staff_data['role']}")

    # -------------------------------------------------------------
    # 2. VERIFY PASSWORD HASH IN DB IS ARGON2 (NOT PLAINTEXT)
    # -------------------------------------------------------------
    print("\n--- TEST 2: Password Hashing Verification ---")
    user_db = db.query(User).filter(User.email == owner_email).first()
    assert user_db is not None, "Owner user not found in database"
    assert user_db.password_hash != owner_password, "Password stored as plaintext!"
    assert user_db.password_hash.startswith("$argon2id$"), f"Password hash is not Argon2id: {user_db.password_hash[:15]}..."
    print(f"Password correctly hashed with Argon2id: {user_db.password_hash[:30]}...")

    # -------------------------------------------------------------
    # 3. SUCCESSFUL LOGIN (JWT & COOKIE)
    # -------------------------------------------------------------
    print("\n--- TEST 3: Successful Login ---")
    res_login = client.post("/api/v1/auth/login", json={
        "email": owner_email,
        "password": owner_password
    })
    assert res_login.status_code == 200, f"Login failed: {res_login.text}"
    login_data = res_login.json()
    assert "access_token" in login_data, "No access_token in login response"
    assert login_data["token_type"].lower() == "bearer"
    assert "user" in login_data
    assert "password_hash" not in login_data["user"]
    assert "access_token" in res_login.cookies, "access_token cookie not set in login response"
    owner_token = login_data["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    print(f"Login successful, access token acquired, cookie verified.")

    # -------------------------------------------------------------
    # 4. WRONG PASSWORD REJECTION
    # -------------------------------------------------------------
    print("\n--- TEST 4: Wrong Password Rejection ---")
    res_wrong_pw = client.post("/api/v1/auth/login", json={
        "email": owner_email,
        "password": "WrongPassword_999!"
    })
    assert res_wrong_pw.status_code == 401, f"Expected 401, got {res_wrong_pw.status_code}"
    print(f"Wrong password rejected with 401 Unauthorized: {res_wrong_pw.json()}")

    # -------------------------------------------------------------
    # 5. NONEXISTENT USER REJECTION
    # -------------------------------------------------------------
    print("\n--- TEST 5: Nonexistent User Rejection ---")
    res_nonexistent = client.post("/api/v1/auth/login", json={
        "email": f"nonexistent_{uuid.uuid4().hex}@domain.com",
        "password": "AnyPassword123!"
    })
    assert res_nonexistent.status_code == 401, f"Expected 401, got {res_nonexistent.status_code}"
    print(f"Nonexistent user rejected with 401 Unauthorized: {res_nonexistent.json()}")

    # -------------------------------------------------------------
    # 6. INACTIVE USER REJECTION
    # -------------------------------------------------------------
    print("\n--- TEST 6: Inactive User Rejection ---")
    inactive_email = f"inactive_{unique_suffix}@example.com"
    inactive_password = "InactivePass123!"
    res_inactive_reg = client.post("/api/v1/auth/register", json={
        "name": f"Inactive User {unique_suffix}",
        "email": inactive_email,
        "password": inactive_password,
        "business_id": biz_a_id
    })
    assert res_inactive_reg.status_code == 201
    
    # Deactivate in database
    inactive_user_db = db.query(User).filter(User.email == inactive_email).first()
    inactive_user_db.is_active = False
    db.commit()

    res_inactive_login = client.post("/api/v1/auth/login", json={
        "email": inactive_email,
        "password": inactive_password
    })
    assert res_inactive_login.status_code == 401, f"Expected 401 for inactive user, got {res_inactive_login.status_code}"
    assert "inactive" in res_inactive_login.json()["detail"].lower()
    print(f"Inactive user rejected with 401 Unauthorized: {res_inactive_login.json()['detail']}")

    # -------------------------------------------------------------
    # 7. AUTHENTICATED /ME ENDPOINT
    # -------------------------------------------------------------
    print("\n--- TEST 7: Authenticated /api/v1/auth/me ---")
    res_me = client.get("/api/v1/auth/me", headers=owner_headers)
    assert res_me.status_code == 200, f"/me failed: {res_me.text}"
    me_data = res_me.json()
    assert me_data["id"] == owner_user_id
    assert me_data["email"] == owner_email
    assert me_data["role"] == "Owner"
    assert me_data["business_id"] == biz_a_id
    print(f"Successfully retrieved authenticated profile for {me_data['name']}")

    # -------------------------------------------------------------
    # 8. LOGOUT (CLEARS COOKIE)
    # -------------------------------------------------------------
    print("\n--- TEST 8: Logout ---")
    res_logout = client.post("/api/v1/auth/logout")
    assert res_logout.status_code == 200
    logout_cookie = res_logout.headers.get("set-cookie", "")
    assert "access_token=" in logout_cookie or "Max-Age=0" in logout_cookie
    print("Logout successfully cleared access_token cookie.")

    # -------------------------------------------------------------
    # 9. AUTH-REQUIRED REJECTION WITHOUT TOKEN
    # -------------------------------------------------------------
    print("\n--- TEST 9: Auth-Required Endpoint Rejection ---")
    res_unauth = client.get("/api/v1/auth/me")
    assert res_unauth.status_code == 401, f"Expected 401 without auth, got {res_unauth.status_code}"
    print(f"Unauthenticated request to /me rejected with 401 Unauthorized.")

    # -------------------------------------------------------------
    # 10. CROSS-BUSINESS ISOLATION ENFORCEMENT
    # -------------------------------------------------------------
    print("\n--- TEST 10: Strict Cross-Business Isolation ---")
    # Create Business B with a different owner
    owner_b_email = f"owner_b_{unique_suffix}@example.com"
    res_reg_b = client.post("/api/v1/auth/register", json={
        "name": f"Owner B {unique_suffix}",
        "email": owner_b_email,
        "password": "PasswordBizB123!",
        "business_name": f"Business B {unique_suffix}"
    })
    assert res_reg_b.status_code == 201
    biz_b_id = res_reg_b.json()["user"]["business_id"]
    owner_b_token = client.post("/api/v1/auth/login", json={
        "email": owner_b_email,
        "password": "PasswordBizB123!"
    }).json()["access_token"]
    owner_b_headers = {"Authorization": f"Bearer {owner_b_token}"}

    # In Business B, create a customer
    res_cust_b = client.post("/api/v1/customers", headers=owner_b_headers, json={
        "name": f"Secret Customer B {unique_suffix}",
        "email": f"custb_{unique_suffix}@b.com"
    })
    assert res_cust_b.status_code in (200, 201), f"Cust B creation failed: {res_cust_b.text}"
    cust_b_id = res_cust_b.json()["data"]["id"]

    # Now, Owner A attempts to access or query with X-Business-ID: biz_b_id spoofed in header
    # User A token MUST override X-Business-ID and use biz_a_id!
    res_spoof_list = client.get(
        "/api/v1/customers",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Business-ID": biz_b_id  # Attempting to spoof Business B!
        }
    )
    assert res_spoof_list.status_code == 200
    customers_visible_to_a = res_spoof_list.json().get("data", [])
    # Customer B MUST NOT appear in User A's response!
    assert not any(c["id"] == cust_b_id for c in customers_visible_to_a), "Cross-business leak! User A saw User B's customer!"

    # Also, User A attempting to get Customer B by ID directly:
    res_cust_get = client.get(
        f"/api/v1/customers/{cust_b_id}",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Business-ID": biz_b_id
        }
    )
    # Must be 404 Not Found (isolated to Business A)
    assert res_cust_get.status_code == 404, f"Expected 404 for cross-business customer access, got {res_cust_get.status_code}"
    print("Strict cross-business isolation confirmed! Spoofed X-Business-ID overridden by JWT.")

    # -------------------------------------------------------------
    # 11. PASSWORD HASH NEVER EXPOSED IN ANY RESPONSE PAYLOAD
    # -------------------------------------------------------------
    print("\n--- TEST 11: Security - No Password Hash In Responses ---")
    for res_name, payload in [
        ("Register Owner", res_reg_owner.json()),
        ("Register Staff", res_reg_staff.json()),
        ("Login Response User", login_data["user"]),
        ("Me Response", me_data)
    ]:
        assert "password_hash" not in payload, f"Security violation: password_hash exposed in {res_name}"
        assert "password" not in payload, f"Security violation: password exposed in {res_name}"
    print("Verified: password_hash and plaintext passwords are never exposed in any responses.")

    # -------------------------------------------------------------
    # 12. AUDIT LOGGING WITH AUTHENTICATED USER ACTOR
    # -------------------------------------------------------------
    print("\n--- TEST 12: Audit Logging with Authenticated Actor ---")
    # Create warehouse for Business A if not exists
    wh_a = db.query(Warehouse).filter(Warehouse.business_id == biz_a_id).first()
    if not wh_a:
        wh_a = Warehouse(business_id=biz_a_id, name="Biz A Warehouse", code="WH-A")
        db.add(wh_a)
        db.commit()
        db.refresh(wh_a)

    # User A creates a product
    res_prod = client.post("/api/v1/products", headers=owner_headers, json={
        "name": f"Product Auth Actor {unique_suffix}",
        "sku": f"SKU-ACTOR-{unique_suffix}",
        "selling_price": 50.0,
        "cost_price": 25.0,
        "min_stock_level": 5,
        "reorder_quantity": 10
    })
    assert res_prod.status_code in (200, 201), f"Product creation failed: {res_prod.text}"
    prod_a_id = res_prod.json()["data"]["id"]

    # Stock in inventory as User A
    res_stock = client.post("/api/v1/inventory/adjust", headers=owner_headers, json={
        "product_id": prod_a_id,
        "warehouse_id": wh_a.id,
        "quantity_change": 20,
        "movement_type": "INITIAL_STOCK",
        "notes": "Initial stock by owner"
    })
    assert res_stock.status_code == 200, f"Inventory adjust failed: {res_stock.text}"

    # User A creates customer
    res_cust_a = client.post("/api/v1/customers", headers=owner_headers, json={
        "name": f"Customer A {unique_suffix}",
        "email": f"cust_a_{unique_suffix}@example.com"
    })
    assert res_cust_a.status_code in (200, 201), f"Customer creation failed: {res_cust_a.text}"
    cust_a_id = res_cust_a.json()["data"]["id"]

    # User A creates an order
    res_order = client.post("/api/v1/orders", headers=owner_headers, json={
        "customer_id": cust_a_id,
        "payment_method": "Cash",
        "notes": "Authenticated order test",
        "items": [
            {
                "product_id": prod_a_id,
                "quantity": 2,
                "unit_price": 50.0
            }
        ]
    })
    assert res_order.status_code in (200, 201), f"Order creation failed: {res_order.text}"
    order_a_id = res_order.json()["data"]["id"]

    # Check the AuditLog entry for this order creation
    audit_entry = db.query(AuditLog).filter(
        AuditLog.business_id == biz_a_id,
        AuditLog.entity_type == "Order",
        AuditLog.entity_id == order_a_id,
        AuditLog.action == "ORDER_CREATED"
    ).first()
    assert audit_entry is not None, "Audit log entry not found for Order creation"
    print(f"Audit log actor/user_id recorded: {audit_entry.user_id}")
    assert audit_entry.user_id != "SYSTEM", "Audit log actor was 'SYSTEM', expected authenticated user!"
    assert owner_data["name"] in audit_entry.user_id, f"Expected actor to contain '{owner_data['name']}', got '{audit_entry.user_id}'"
    print(f"Audit log correctly recorded real authenticated actor: {audit_entry.user_id}")

    db.close()
    print("\n=== ALL PHASE 5 (TASK 1) AUTH & USER FOUNDATION TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()

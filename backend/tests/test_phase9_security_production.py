import sys
import os
import io
import uuid
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.business import Business
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.branch import Branch
from app.models.order import Order
from app.models.document import Document
from app.core.security import hash_password, create_access_token

client = TestClient(app)

def test_phase9_security_and_production_readiness():
    print("=== STARTING PHASE 9 SECURITY & PRODUCTION READINESS TEST SUITE ===")
    db = SessionLocal()

    suffix = uuid.uuid4().hex[:6]
    pwd_plain = "Phase9SecurePass123!"
    pwd_hash = hash_password(pwd_plain)

    # -------------------------------------------------------------
    # 1. HEALTH CHECK & DATABASE CONNECTIVITY
    # -------------------------------------------------------------
    print("\n--- 1. Testing System & DB Health Endpoint ---")
    resp_health_root = client.get("/health")
    assert resp_health_root.status_code == 200, f"Root /health failed: {resp_health_root.text}"
    data_health_root = resp_health_root.json()
    assert data_health_root.get("status") == "ok"
    assert data_health_root.get("database") == "connected"
    assert data_health_root.get("app") == "healthy"

    resp_health_api = client.get("/api/v1/health")
    assert resp_health_api.status_code == 200, f"/api/v1/health failed: {resp_health_api.text}"
    data_health_api = resp_health_api.json()
    assert data_health_api.get("status") == "ok"
    assert data_health_api.get("database") == "connected"
    print("PASSED: Health check verifies app is healthy and DB is connected.")

    # -------------------------------------------------------------
    # 2. CORS RESTRICTIONS
    # -------------------------------------------------------------
    print("\n--- 2. Testing Strict Production CORS Policy ---")
    # Allowed origin test
    resp_cors_allowed = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp_cors_allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Disallowed / Attacker origin test
    resp_cors_disallowed = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://malicious-attacker.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    # The header should NOT match the malicious origin
    assert resp_cors_disallowed.headers.get("access-control-allow-origin") != "http://malicious-attacker.com"
    print("PASSED: CORS policy permits configured origins and denies unauthorized origins.")

    # -------------------------------------------------------------
    # 3. MULTI-TENANT ISOLATION & IDOR ATTACK PREVENTION
    # -------------------------------------------------------------
    print("\n--- 3. Setting Up Two Separate Isolated Tenants ---")
    # Create Tenant A
    biz_a = Business(name=f"Tenant A Org {suffix}", legal_name=f"Tenant A Org LLC {suffix}")
    # Create Tenant B
    biz_b = Business(name=f"Tenant B Org {suffix}", legal_name=f"Tenant B Org LLC {suffix}")
    db.add_all([biz_a, biz_b])
    db.commit()
    db.refresh(biz_a)
    db.refresh(biz_b)

    user_a = User(
        business_id=biz_a.id,
        name="Owner A",
        email=f"owner_a_{suffix}@secure.com",
        password_hash=pwd_hash,
        role="Owner",
        is_active=True
    )
    user_b = User(
        business_id=biz_b.id,
        name="Owner B",
        email=f"owner_b_{suffix}@secure.com",
        password_hash=pwd_hash,
        role="Owner",
        is_active=True
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    # Auth headers
    token_a = create_access_token({"sub": str(user_a.id), "business_id": str(biz_a.id), "role": "Owner"})
    token_b = create_access_token({"sub": str(user_b.id), "business_id": str(biz_b.id), "role": "Owner"})
    auth_a = {"Authorization": f"Bearer {token_a}"}
    auth_b = {"Authorization": f"Bearer {token_b}"}

    # Populate Tenant A with proprietary resources
    cust_a = Customer(business_id=biz_a.id, name=f"Confidential Client A {suffix}", email=f"client_a_{suffix}@test.com")
    prod_a = Product(business_id=biz_a.id, name=f"Proprietary Widget A {suffix}", sku=f"SKU-A-{suffix}", selling_price=Decimal("99.99"), cost_price=Decimal("49.99"))
    wh_a = Warehouse(business_id=biz_a.id, name=f"Warehouse A {suffix}", code=f"WH-A-{suffix}")
    branch_a = Branch(business_id=biz_a.id, name=f"Branch A {suffix}", code=f"BR-A-{suffix}")
    
    db.add_all([cust_a, prod_a, wh_a, branch_a])
    db.commit()
    db.refresh(cust_a)
    db.refresh(prod_a)
    db.refresh(wh_a)
    db.refresh(branch_a)

    order_a = Order(
        business_id=biz_a.id,
        order_number=f"ORD-A-{suffix}",
        customer_id=cust_a.id,
        status="CONFIRMED",
        subtotal=Decimal("99.99"),
        total=Decimal("99.99")
    )
    db.add(order_a)
    db.commit()
    db.refresh(order_a)

    doc_bytes = b"Confidential financial statement 2026 for Tenant A"
    files = {"file": ("tax_2026.pdf", io.BytesIO(doc_bytes), "application/pdf")}
    res_doc_up = client.post(
        "/api/v1/documents/upload",
        files=files,
        data={"name": f"Confidential Financials A {suffix}", "document_type": "Financial"},
        headers=auth_a
    )
    assert res_doc_up.status_code == 201, f"Failed document upload: {res_doc_up.text}"
    doc_a_id = res_doc_up.json()["data"]["id"]

    print("Tenant A resources created. Now executing IDOR probes from Tenant B context:")

    # IDOR Check 1: Tenant B attempting to read Tenant A Customer
    idor_cust_get = client.get(f"/api/v1/customers/{cust_a.id}", headers=auth_b)
    assert idor_cust_get.status_code in (404, 403), f"IDOR Vulnerability on Customer GET! Got {idor_cust_get.status_code}"

    # IDOR Check 2: Tenant B attempting to update Tenant A Customer
    idor_cust_patch = client.patch(f"/api/v1/customers/{cust_a.id}", json={"name": "Hacked Name"}, headers=auth_b)
    assert idor_cust_patch.status_code in (404, 403), f"IDOR Vulnerability on Customer PATCH! Got {idor_cust_patch.status_code}"

    # IDOR Check 3: Tenant B attempting to update Tenant A Product
    idor_prod_patch = client.patch(f"/api/v1/products/{prod_a.id}", json={"name": "Hacked Product"}, headers=auth_b)
    assert idor_prod_patch.status_code in (404, 403), f"IDOR Vulnerability on Product PATCH! Got {idor_prod_patch.status_code}"

    # IDOR Check 4: Tenant B attempting to read Tenant A Product
    idor_prod_get = client.get(f"/api/v1/products/{prod_a.id}", headers=auth_b)
    assert idor_prod_get.status_code in (404, 403), f"IDOR Vulnerability on Product GET! Got {idor_prod_get.status_code}"

    # IDOR Check 5: Tenant B attempting to read Tenant A Order
    idor_order_get = client.get(f"/api/v1/orders/{order_a.id}", headers=auth_b)
    assert idor_order_get.status_code in (404, 403), f"IDOR Vulnerability on Order GET! Got {idor_order_get.status_code}"

    # IDOR Check 6: Tenant B attempting to download Tenant A Document
    idor_doc_get = client.get(f"/api/v1/documents/{doc_a_id}/download", headers=auth_b)
    assert idor_doc_get.status_code in (404, 403), f"IDOR Vulnerability on Document Download! Got {idor_doc_get.status_code}"

    # IDOR Check 7: Tenant B attempting to read Tenant A Warehouse
    idor_wh_get = client.get(f"/api/v1/warehouses/{wh_a.id}", headers=auth_b)
    assert idor_wh_get.status_code in (404, 403), f"IDOR Vulnerability on Warehouse GET! Got {idor_wh_get.status_code}"

    # IDOR Check 8: Tenant B attempting to read Tenant A Branch
    idor_branch_get = client.get(f"/api/v1/branches/{branch_a.id}", headers=auth_b)
    assert idor_branch_get.status_code in (404, 403), f"IDOR Vulnerability on Branch GET! Got {idor_branch_get.status_code}"

    print("PASSED: All 8 IDOR probes blocked. Resources are strictly isolated per tenant.")

    # -------------------------------------------------------------
    # 4. TENANT LEAKAGE PREVENTION ON LIST ENDPOINTS
    # -------------------------------------------------------------
    print("\n--- 4. Testing List Endpoints for Tenant Leakage ---")
    list_cust_b = client.get("/api/v1/customers", headers=auth_b).json()
    cust_ids_b = [c["id"] for c in list_cust_b.get("data", [])]
    assert cust_a.id not in cust_ids_b, "Tenant A customer leaked to Tenant B list!"

    list_prod_b = client.get("/api/v1/products", headers=auth_b).json()
    prod_ids_b = [p["id"] for p in list_prod_b.get("data", [])]
    assert prod_a.id not in prod_ids_b, "Tenant A product leaked to Tenant B list!"

    list_order_b = client.get("/api/v1/orders", headers=auth_b).json()
    order_ids_b = [o["id"] for o in list_order_b.get("data", [])]
    assert order_a.id not in order_ids_b, "Tenant A order leaked to Tenant B list!"

    print("PASSED: No cross-tenant data leakage detected in listing endpoints.")

    # -------------------------------------------------------------
    # 5. TOKEN AUTHENTICATION & TAMPERING GUARDS
    # -------------------------------------------------------------
    print("\n--- 5. Testing Token Authentication & Tampering Defenses ---")
    # No token
    resp_no_token = client.get("/api/v1/customers")
    assert resp_no_token.status_code == 401, f"Expected 401 for missing token, got {resp_no_token.status_code}"

    # Malformed token
    resp_malformed = client.get("/api/v1/customers", headers={"Authorization": "Bearer not-a-valid-jwt-token"})
    assert resp_malformed.status_code == 401, f"Expected 401 for malformed token, got {resp_malformed.status_code}"

    # Forged signature token
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTYiLCJleHAiOjE5OTk5OTk5OTl9.FakeSignatureInvalidToken123456789"
    resp_fake_sig = client.get("/api/v1/customers", headers={"Authorization": f"Bearer {fake_token}"})
    assert resp_fake_sig.status_code == 401, f"Expected 401 for forged token signature, got {resp_fake_sig.status_code}"

    print("PASSED: Unauthenticated, malformed, and forged tokens rejected with 401.")

    # -------------------------------------------------------------
    # 6. INPUT VALIDATION & NEGATIVE BOUNDS
    # -------------------------------------------------------------
    print("\n--- 6. Testing Data Validation & Negative Bounds ---")
    # Negative product price
    resp_neg_price = client.post(
        "/api/v1/products",
        json={"name": "Invalid Product", "sku": f"INV-1-{suffix}", "selling_price": -50.0, "cost_price": 10.0},
        headers=auth_a
    )
    assert resp_neg_price.status_code == 422, f"Expected 422 for negative price, got {resp_neg_price.status_code}"

    # Negative product cost
    resp_neg_cost = client.post(
        "/api/v1/products",
        json={"name": "Invalid Product", "sku": f"INV-2-{suffix}", "selling_price": 50.0, "cost_price": -10.0},
        headers=auth_a
    )
    assert resp_neg_cost.status_code == 422, f"Expected 422 for negative cost, got {resp_neg_cost.status_code}"

    # Missing mandatory name
    resp_missing_name = client.post(
        "/api/v1/products",
        json={"sku": f"INV-3-{suffix}", "selling_price": 50.0, "cost_price": 10.0},
        headers=auth_a
    )
    assert resp_missing_name.status_code == 422, f"Expected 422 for missing name, got {resp_missing_name.status_code}"

    print("PASSED: Input validation rejects negative values and malformed payloads.")

    print("\n=== PHASE 9 SECURITY & PRODUCTION READINESS TEST SUITE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_phase9_security_and_production_readiness()

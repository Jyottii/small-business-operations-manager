import sys
import os
import uuid

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserRole

client = TestClient(app)

def test_frontend_auth_and_user_management():
    # 1. Login as Sarah (Owner)
    login_res = client.post("/api/v1/auth/login", json={
        "email": "sarah@techhaven.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200, login_res.text
    owner_token = login_res.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # 2. Get Me as Owner
    me_res = client.get("/api/v1/auth/me", headers=owner_headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    if "data" in me_data:
        me_data = me_data["data"]
    assert me_data["email"] == "sarah@techhaven.com"
    assert me_data["role"] == "Owner"
    biz_id = me_data["business_id"]

    # 3. Owner list users
    users_res = client.get("/api/v1/users", headers=owner_headers)
    assert users_res.status_code == 200
    assert len(users_res.json()["data"]) >= 3

    # 4. Owner creates a new staff member
    unique_suffix = uuid.uuid4().hex[:6]
    new_user_res = client.post("/api/v1/users", json={
        "name": f"Test Staff {unique_suffix}",
        "email": f"test_staff_{unique_suffix}@techhaven.com",
        "password": "Password123!",
        "role": "Staff"
    }, headers=owner_headers)
    assert new_user_res.status_code == 201
    created_user = new_user_res.json()["data"]
    assert created_user["role"] == "Staff"
    assert created_user["is_active"] is True

    # 5. Owner toggles status
    toggle_res = client.patch(f"/api/v1/users/{created_user['id']}", json={
        "is_active": False
    }, headers=owner_headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["data"]["is_active"] is False

    # 6. Login as Mike (Staff)
    staff_login = client.post("/api/v1/auth/login", json={
        "email": "mike@techhaven.com",
        "password": "Password123!"
    })
    assert staff_login.status_code == 200
    staff_headers = {"Authorization": f"Bearer {staff_login.json()['access_token']}"}

    # 7. Staff denied user list (403)
    staff_users = client.get("/api/v1/users", headers=staff_headers)
    assert staff_users.status_code == 403

    # 8. Staff denied user creation (403)
    staff_create = client.post("/api/v1/users", json={
        "name": "Hacker",
        "email": "hacker@evil.com",
        "password": "Password123!",
        "role": "Owner"
    }, headers=staff_headers)
    assert staff_create.status_code == 403

    # 9. Manager access check
    mgr_login = client.post("/api/v1/auth/login", json={
        "email": "john@techhaven.com",
        "password": "Password123!"
    })
    assert mgr_login.status_code == 200
    mgr_headers = {"Authorization": f"Bearer {mgr_login.json()['access_token']}"}

    # Manager CAN view users
    mgr_view_users = client.get("/api/v1/users", headers=mgr_headers)
    assert mgr_view_users.status_code == 200

    # Manager CANNOT create users (403)
    mgr_create = client.post("/api/v1/users", json={
        "name": "New Person",
        "email": "new@techhaven.com",
        "password": "Password123!",
        "role": "Staff"
    }, headers=mgr_headers)
    assert mgr_create.status_code == 403

    # 10. Logout
    logout_res = client.post("/api/v1/auth/logout", headers=owner_headers)
    assert logout_res.status_code == 200

    print("ALL FRONTEND AUTH & USER MANAGEMENT TESTS PASSED!")

if __name__ == "__main__":
    test_frontend_auth_and_user_management()

# Small Business Operations Management Platform

A modern, production-ready, full-stack ERP and Business Operations platform designed specifically for small businesses. Built with **FastAPI**, **SQLAlchemy**, **PostgreSQL** (production target) / **SQLite** (local development), **React 18**, and **Tailwind CSS**.

---

## 🌟 Key Features & Capabilities

### 1. Robust Authentication & Role-Based Access Control (RBAC)
- **Multi-Tenant Architecture**: Strict organizational isolation across all database queries, services, and APIs. Client-provided `business_id` is never trusted; identity is enforced server-side from cryptographically signed JWT tokens.
- **Enterprise Password Security**: Modern **Argon2id** password hashing (`m=65536, t=2, p=2`).
- **Granular Roles**:
  - 👑 **Owner**: Unrestricted administrative, financial, employee, branch, and configuration rights.
  - 🛡️ **Admin**: High-level operational management, inventory, purchases, expenses, and user supervision.
  - 💼 **Manager**: Operational control over sales, purchasing, inventory, and reporting without user role elevation.
  - 🏷️ **Staff / Cashier**: Fast POS transactions, order lookup, and customer assistance with privileged routes strictly blocked (HTTP 403).
- **Demo Mode**: Instant 1-click credential switching for all four roles on the login page.

### 2. Operations & Multi-Store Management
- **Point of Sale (POS) & Barcode Lookup**: High-speed checkout interface with barcode scanner support, real-time stock deduction, tax calculation, and order generation.
- **Multi-Store & Branch Switching**: Contextual branch switching across stores with branch-specific sales tracking and staff assignment.
- **Multi-Warehouse & Atomic Stock Transfers**: Manage multiple storage facilities with atomic 2-phase stock transfers (`TRANSFER_OUT` and `TRANSFER_IN` movements) ensuring zero inventory loss.
- **Comprehensive Inventory Control**: Real-time quantity tracking, minimum reorder thresholds, out-of-stock alarms, and complete stock movement audit trails.
- **Purchasing & Supplier Management**: Full purchase order lifecycle with partial and complete goods receiving, over-receiving guards, and supplier payment balances.
- **Sales Returns & Refunds**: Order item returns with automatic stock replenishment, refund calculation, and credit tracking.

### 3. Business Intelligence & Deterministic Smart Insights
- **Advanced Analytics**: Real-time sales summaries, Average Order Value (AOV), revenue over time, gross margins, Accounts Receivable (AR), Accounts Payable (AP), and category breakdowns.
- **Explainable Smart Insights Engine**: 12 deterministic rules evaluating operational health without non-deterministic AI halluncinations:
  - Stock alerts (critical stockouts, low-stock warnings, stagnant/slow-moving inventory).
  - Margin & Profitability checks (operating loss warnings, compressed margins).
  - Risk & Concentration flags (dominant customer revenue concentration, supplier spend dependency, elevated AR/AP ratios).
  - Data Quality audits (incomplete product cost coverage).
- **Operational Reporting & CSV Streaming**: Real-time reports for Sales, Inventory, Purchases, Expenses, and Customers with live preview and downloadable CSV exports.

### 4. Productivity & Enterprise Tools
- **Universal Search**: Debounced global search across products, customers, suppliers, orders, purchase orders, warehouses, and branches.
- **Document Vault**: Multi-tenant document repository with secure per-tenant filesystem isolation, MIME validation, and access control.
- **Business Calendar & Milestones**: Unified calendar aggregating purchase order delivery estimates, invoice due dates, and operational deadlines.
- **Goals & Performance Tracking**: Set business targets (Revenue, Orders, Net Profit) with live progress computation from database metrics.
- **Immutable Audit Trail**: Chronological event logging recording every critical mutation with authenticated user attribution.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend API** | Python 3.12, FastAPI, Pydantic v2, Starlette, Uvicorn |
| **Database & ORM** | SQLAlchemy 2.0, Alembic migrations, PostgreSQL (Prod) / SQLite (Dev) |
| **Authentication** | OAuth2 Bearer JWT (HS256), Argon2id (`passlib` + `argon2-cffi`) |
| **Frontend UI** | React 18, React Router v6, Vite 5, Tailwind CSS, Lucide Icons |
| **Testing** | FastAPI TestClient, Pytest-compatible suites (8 regression suites) |

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# (Optional) Seed demo data
python seed_data.py

# Launch development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API will be available at: `http://127.0.0.1:8000`  
Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`  
Health check endpoint: `http://127.0.0.1:8000/api/v1/health`

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
The frontend application will be available at: `http://localhost:5173`

---

## 🔑 Demo Credentials

When running with seeded data or exploring the application, use these pre-configured accounts (or click any of the **Demo Quick-Fill** buttons on the Login page):

| Role | Email | Password | Scope & Access |
|---|---|---|---|
| **Owner** | `owner@apexoperations.com` | `OwnerPass123!` | Complete access to all features, finances & settings |
| **Admin** | `admin@apexoperations.com` | `AdminPass123!` | Operations, inventory, purchases & management |
| **Manager** | `manager@apexoperations.com` | `ManagerPass123!` | Sales, inventory, purchase orders & insights |
| **Staff / Cashier** | `cashier@apexoperations.com` | `CashierPass123!` | POS, sales checkout & customer lookup |

---

## 🧪 Comprehensive Test Suites

The repository contains 8 automated end-to-end regression test suites covering 100% of critical paths:

```bash
cd backend

# Phase 4: Business Workflows (POS, Inventory, POs, Returns, Payments)
python tests/test_phase4_workflows.py

# Phase 5: Authentication Foundation (Argon2id, JWT, Session)
python tests/test_phase5_auth.py

# Phase 5: Role-Based Access Control (Owner, Admin, Manager, Staff)
python tests/test_phase5_rbac.py

# Phase 5: Frontend Auth API Endpoints
python tests/test_phase5_frontend_auth_api.py

# Phase 6: Business Intelligence & Analytics Calculations
python tests/test_phase6_analytics.py

# Phase 7: Explainable Smart Insights Rules Engine
python tests/test_phase7_insights.py

# Phase 8: Advanced Operational Features (Warehouses, Transfers, Search, Reports, Vault)
python tests/test_phase8_advanced.py

# Phase 9: Security, IDOR Cross-Tenant Isolation, CORS, & Production Readiness
python tests/test_phase9_security_production.py
```

---

## 🔒 Security & Tenant Isolation Architecture

1. **Zero Trust Tenant Isolation**:
   Every database query filters by `business_id == current_user.business_id`. Attempting to access an entity belonging to another organization yields an immediate `404 Not Found` / `403 Forbidden` response.
2. **CORS Restrictions**:
   CORS origins are strictly validated using environment variables (`CORS_ORIGINS`). Wildcard origin reflection with credentials is explicitly forbidden.
3. **Database Health Monitoring**:
   The `/api/v1/health` endpoint performs a live query (`SELECT 1`) to distinguish between application container health and database connectivity health.
4. **Data Integrity Guards**:
   All numeric fields (prices, costs, stock levels, reorder quantities) enforce non-negative bounds (`ge=0`) at the Pydantic schema level.

---

## 🚢 Deployment Guide

For comprehensive instructions on deploying to cloud infrastructure (such as Vercel, Render, Railway, Supabase, or AWS), consult the dedicated guide:  
👉 [Deployment Guide](docs/DEPLOYMENT.md)

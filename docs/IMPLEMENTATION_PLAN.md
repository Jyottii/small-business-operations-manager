# Implementation Plan

## PHASE 0 — UI FOUNDATION

### Goal
Build the complete frontend information architecture and UI.

### Deliverables
* Application shell
* Sidebar
* Top navigation
* Responsive layout
* Dashboard
* Inventory pages
* Product pages
* Sales/POS UI
* Orders
* Customers
* Suppliers
* Purchase Orders
* Payments
* Expenses
* Analytics
* Employees
* Reports
* Settings
* Notifications
* Reusable components
* Mock data

NO backend.

---

## PHASE 1 — CORE DATA & DATABASE [COMPLETE]

### Implement
* [x] PostgreSQL
* [x] SQLAlchemy models
* [x] Database relationships
* [x] Migrations
* [x] Seed/demo data

### Core Entities Created
* [x] User
* [x] Business
* [x] Product
* [x] Category
* [x] Inventory
* [x] Warehouse
* [x] Customer
* [x] Supplier
* [x] Sale (Order)
* [x] SaleItem (OrderItem)
* [x] PurchaseOrder
* [x] PurchaseOrderItem
* [x] Payment
* [x] Expense
* [x] Employee
* [x] Document, Notification, AuditLog

---

## PHASE 2 — BACKEND/API [COMPLETE]

### Implement FastAPI APIs for:
* [x] Products
* [x] Inventory
* [x] Customers
* [x] Suppliers
* [x] Sales (Orders)
* [x] Purchases
* [x] Payments
* [x] Expenses
* [x] Employees (Not actively used, reserved for future Auth)
* [x] Service layer for business logic separations

### Add
* [x] Pydantic Validation
* [x] Error handling (Custom exception dependencies)
* [x] Pagination & Responses structure
* [x] Filtering (Handled modularly via ORM mapping logic)
* [x] Sorting & Search parameters prep

---

## PHASE 3 — CONNECT FRONTEND TO BACKEND [COMPLETE]

Replace mock data with APIs.

### API Client
* [x] Central HTTP Client (etch wrapper)
* [x] Environment Variables (VITE_API_BASE_URL)
* [x] Temporary Mock Auth Header (X-Business-ID)
* [x] Reusable Data Fetching Hooks (useApi)

### Replace Mock Data (List Views)
* [x] Products, Orders, POs, Customers, Suppliers, Payments, Expenses, Employees

### Integrate Workflows (Detail Views)
* [x] Loading states, Empty states, Error states
* [x] Product Detail (Price, Stock, Inventory Location data)
* [x] Order Detail (Totals, Balances, Items)
* [x] Purchase Order Detail (Expected vs Received, Totals)
* [x] Server-side filtering & Pagination routed to API

---

## PHASE 4 — BUSINESS WORKFLOWS [COMPLETE]

### Sales Workflow
* [x] Create Sale with Customer, Warehouse, Products, Quantities
* [x] Atomic Inventory pre-validation (insufficient stock rejection)
* [x] Automatic inventory deduction and `SALE` stock movement
* [x] Customer credit limit enforcement and balance tracking
* [x] Immediate payment recording (Cash, Card, UPI) and On-Credit support
* [x] Safe Order cancellation with automatic inventory restoration

### Purchases Workflow
* [x] Create Purchase Order with Supplier, Warehouse, line items
* [x] Partial and full receiving of goods
* [x] Over-receiving prevention
* [x] Automatic inventory increase and `PURCHASE_RECEIPT` movements
* [x] Supplier payable tracking on PO creation and reduction on payment
* [x] PO cancellation with supplier balance adjustment

### Returns & Refunds Workflow
* [x] Dedicated `Return` and `ReturnItem` models & Alembic migration
* [x] Return quantity validation (cannot return > sold quantity)
* [x] Automatic inventory restoration with `RETURN` stock movement
* [x] Refund calculation and customer/order balance reconciliation

### Payments & Financial Workflows
* [x] Order payments (`POST /orders/{id}/payments`)
* [x] Supplier PO payments (`POST /purchase-orders/{id}/payments`)
* [x] Balance reconciliation (`amount_paid`, `balance_due`, `payment_status`)
* [x] Payment history displays on Order and PO detail views

### Inventory & Ledger
* [x] Controlled manual stock adjustment modal and validation
* [x] Unified stock movement ledger view (`/inventory/movement`)
* [x] Centralized low stock detection and alerts

### Audit & Notifications
* [x] Real-time operational notification generation
* [x] Comprehensive immutable audit logging across all state changes
* [x] Connected UI views for Audit Logs and Notifications

---

## PHASE 5 — AUTHENTICATION, USERS & RBAC [COMPLETE]

### Task 1 — User & Authentication Foundation [COMPLETE]
* [x] Argon2id password hashing (`argon2-cffi`)
* [x] User model with `role` column (`Owner`, `Admin`, `Manager`, `Staff`)
* [x] Alembic migration `12307a99b475_add_role_column_to_users.py`
* [x] Short-lived JWT access token generation & verification (`pyjwt`)
* [x] Dual-transport authentication: Bearer header and secure HttpOnly cookie
* [x] Endpoints:
  * `POST /api/v1/auth/register` (supports business creation as Owner or joining existing business)
  * `POST /api/v1/auth/login` (verifies active status, Argon2 hash, issues JWT + sets cookie)
  * `POST /api/v1/auth/logout` (clears cookie)
  * `GET /api/v1/auth/me` (retrieves current authenticated profile)
* [x] Strict tenant isolation (reject client `X-Business-ID` when user is authenticated)
* [x] Password hash exclusion in all response payloads (`UserResponse`, `TokenResponse`)
* [x] Audit log actor injection (replace `"SYSTEM"` placeholder with authenticated user)
* [x] Frontend API client auth token attachment & credentials support
* [x] Automated test suite: `test_phase5_auth.py` (12/12 passed) & `test_phase4_workflows.py` (8/8 passed)

### Task 2 — Role-Based Access Control (RBAC) [COMPLETE]
* [x] Centralized `require_roles(*allowed_roles)` dependency factory with 401 unauthenticated and 403 unauthorized semantics
* [x] Inactive account rejection (401 Unauthorized)
* [x] Least-privilege route protection across business, users, products, customers, suppliers, orders, POs, payments, expenses, warehouses, inventory, and audit logs
* [x] Scoped permissions: Owner (full/settings/users), Admin (operations/staff-mgr users), Manager (day-to-day operations), Staff (POS/sales/order/return)
* [x] User management router (`/api/v1/users`) with privilege escalation guards (no self-promotion, Admins cannot create/promote Owners)
* [x] Prevention of public registration privilege escalation for existing businesses
* [x] Comprehensive RBAC test suite: `backend/tests/test_phase5_rbac.py` passing 100%
* [x] Full regression verification: `test_phase5_auth.py` and `test_phase4_workflows.py` passing 100%
* [x] Frontend build verification: `npm run build` succeeds cleanly

### Task 3 — Frontend Authentication & RBAC UI [COMPLETE]
* [x] Auth context and token management in React (`src/context/AuthContext.jsx`)
* [x] Authoritative session restoration via `GET /api/v1/auth/me` and global 401 event listener
* [x] Polished Login and Registration UI forms with quick demo credentials (`Login.jsx`, `Register.jsx`)
* [x] Unauthenticated route protection (`ProtectedRoute.jsx`) with clean loading state
* [x] Role-restricted route protection (`RoleRoute.jsx`) and Forbidden feedback (`AccessDenied.jsx`)
* [x] Role-aware navigation and layout adaptations in `MainLayout.jsx` for Owner, Admin, Manager, and Staff
* [x] Top header user badge, initials avatar, and immediate Sign Out capability
* [x] Complete User Management dashboard view (`Users.jsx`) with Add User modal and toggle activation for Owner/Admin
* [x] Clean API client error handling with distinct 401 redirect and 403 authorization error handling
* [x] Automated test suite: `test_phase5_frontend_auth_api.py` passing 100%
* [x] Production build verification: `npm run build` passing cleanly with 0 errors
---

## PHASE 6 — BUSINESS INTELLIGENCE & ADVANCED ANALYTICS

### Task 1 — Analytics Foundation [COMPLETE]
* [x] Reusable Analytics Service (`app/services/analytics_service.py`) using performant database aggregations
* [x] Consistent date range filtering (`today`, `last_7_days`, `last_30_days`, `current_month`, `previous_month`, `all_time`, `custom`)
* [x] Core KPIs: Sales revenue, orders, AOV, order statuses, inventory units & valuation, low/out-of-stock counts, receivables, payables, PO counts & spend, returns & refunds
* [x] Financial & P&L intelligence: Sales, COGS, Gross Profit, Gross Margin %, Expenses, Net Profit, Net Margin %, and cost data coverage %
* [x] Product performance & inventory velocity ($V = \text{quantity\_sold} / \text{days}$): Top revenue, top volume, slow-moving/stagnant, low-stock
* [x] Customer analytics: Top customers by revenue, order counts, balances, AOV
* [x] Supplier & purchasing intelligence: Top suppliers by spend, PO statuses
* [x] Time-series timeline: Daily trends for sales, purchases, payments collected, refunds, expenses
* [x] REST API endpoints (`/api/v1/analytics/...`) with strict multi-tenant isolation and RBAC (`Owner`, `Admin`, `Manager`)
* [x] Comprehensive test suite (`tests/test_phase6_analytics.py`) with 11/11 passing tests
* [x] Regression testing: Phase 4 workflows, Phase 5 Auth, Phase 5 RBAC, frontend build all passing

### Task 2 — Business Intelligence Dashboard UI [COMPLETE]
* [x] Executive BI Dashboard (`Dashboard.jsx`) with 8 KPI cards, Recharts timeline, payment distribution, P&L hierarchy
* [x] Product performance & inventory velocity views (fast vs slow-moving with tied-up capital)
* [x] Customer & supplier intelligence rankings
* [x] Actionable low-stock & stockout table with reorder links
* [x] Role-aware Staff operational hub (POS, orders, lookup) preventing 403 errors
* [x] Connected live `ProfitLoss.jsx` and updated report routing

---

## PHASE 7 — SMART BUSINESS INSIGHTS ENGINE

### Task 1 — Deterministic Smart Insights Engine [COMPLETE]
* [x] Deterministic, rules-based business intelligence layer detecting operational conditions across 6 domains (inventory, sales, finance, customer, supplier, data quality)
* [x] Explainable insights with title, message, metric, current value, threshold, actionable recommendation, and supporting evidence
* [x] Prioritization (critical -> warning -> info) and deduplication (aggregating bulk alerts)
* [x] Centralized, explicit configuration (`InsightThresholds`) with documented defaults
* [x] API endpoint `GET /api/v1/insights` guarded by RBAC (`Owner`, `Admin`, `Manager`; Staff gets 403)
* [x] Multi-tenant isolation enforced on every query
* [x] Comprehensive test suite `tests/test_phase7_insights.py` (18/18 tests pass)
* [x] Regression testing: Phase 4 workflows, Phase 5 Auth, Phase 5 RBAC, Phase 6 Analytics, and frontend build all passing

### Task 2 — Smart Business Insights Frontend Integration [COMPLETE]
* [x] Enhanced `apiClient` with automatic query param serialization and upgraded `useApi` with race-condition prevention and real network refetching
* [x] Created `src/api/insights.js` for centralized period options, `getInsights`, `useInsights`, and route navigation mapping
* [x] Integrated Smart Business Insights section into the executive Dashboard with summary metric cards, severity filtering, and top prioritized alerts
* [x] Built full dedicated console at `/smart-insights` (`pages/Insights/SmartInsights.jsx`) supporting period filters, domain filters, search, and evidence breakdowns
* [x] Created reusable components: `InsightsSummaryCards.jsx`, `InsightsList.jsx` with expandable evidence tables and direct navigation links
* [x] Production build and all regression test suites pass 100%

---

## PHASE 8 — ADVANCED FEATURES & OPERATIONAL DEPTH [COMPLETE]

### Implemented
* [x] Multi-Store & Multi-Branch Architecture (`Branch` model, `/branches` CRUD, `/branches` management page, and header branch selector)
* [x] Advanced Warehouse Management (`GET /warehouses/{id}/summary`, facility valuation cards, and `/warehouses` management console)
* [x] Atomic Stock Transfers (`StockTransfer` & `StockTransferItem` models, `/stock-transfers` API, atomic multi-warehouse inventory deductions/additions, and `TRANSFER_OUT`/`TRANSFER_IN` movements)
* [x] Universal Search (`/search?q=...` covering products, customers, suppliers, orders, POs, warehouses, and branches, debounced header popover)
* [x] Barcode & QR POS scanning (`/products/barcode/{barcode}`, POS barcode scan bar with instant cart add and feedback)
* [x] Reports Center & Live CSV Export (`/reports/sales`, `/inventory`, `/purchases`, `/expenses`, `/customers`, live preview drawer, and streaming CSV export)
* [x] Document Vault (`Document` model, `/documents` API with safe upload, file extension/size validation, download, and delete)
* [x] Goals & Targets System (`BusinessGoal` model, `/goals` API calculating real-time progress percentages against live orders, and dashboard widget)
* [x] Business Calendar & Operational Milestones (`/calendar/events` aggregating PO deliveries, order dues, and goal deadlines, displayed on dashboard schedule)
* [x] Demo Mode & Seeded Access (quick-fill logins in `Login.jsx` and header demo mode badge)
* [x] Comprehensive test suite `tests/test_phase8_advanced.py` and 100% passing regressions across Phases 4–7.

---

## PHASE 9 — POLISH & PRODUCTION READINESS [COMPLETE]

### Implemented
* [x] Environment configuration audit & standardized production templates (`backend/.env.example`, `frontend/.env.example`).
* [x] Security improvements: Strict CORS origins enforcement (`settings.cors_origins_list`), removal of wildcard origin reflection.
* [x] Database operational health check endpoint (`/api/v1/health` and `/health`) performing live connectivity tests (`SELECT 1`).
* [x] Frontend performance & code splitting: Configured manual vendor/icon chunks in `vite.config.js` and `React.lazy` + `Suspense` in `App.jsx`, reducing bundle chunk sizes below 380 kB with zero build warnings.
* [x] Schema data integrity: Added non-negative bounds (`ge=0`) to numeric product price/cost models in `ProductBase`.
* [x] Multi-tenant isolation & IDOR verification: Comprehensive test suite in `tests/test_phase9_security_production.py` verifying cross-tenant barriers on customers, products, orders, warehouses, branches, and documents.
* [x] Production documentation: Created comprehensive project `README.md` and detailed `docs/DEPLOYMENT.md` covering architecture, PostgreSQL migrations, hosting workflows, and pre-flight checklists.
* [x] Full regression verification: 100% pass rate across all 8 backend test suites (Phases 4 through 9).

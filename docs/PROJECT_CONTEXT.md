# Project Context

## Project Identity

**Name:** Small Business Operations Manager

**Purpose:**
A unified platform that helps small businesses manage daily operations from one place.

## Core Modules

1. Dashboard
2. Inventory
3. Products
4. Stock Movement
5. Sales / POS
6. Orders
7. Customers
8. Suppliers
9. Purchase Orders
10. Payments
11. Expenses
12. Profit & Loss
13. Cash Flow
14. Analytics
15. Smart Insights
16. Employees
17. Warehouses
18. Returns & Refunds
19. Reports
20. Notifications
21. Documents
22. Audit Logs
23. Business Settings

## Product Philosophy

The application should prioritize:
* clarity
* operational usefulness
* connected workflows
* discoverability
* scalability
* responsive design
* realistic business workflows

## Important Architectural Principles

* **Frontend/Backend Separation:** Clear separation for scalability and independent deployments.
* **Reusable Components:** Building a robust component library (buttons, tables, modals) to ensure consistency and speed up development.
* **Modular Feature Structure:** Grouping logic by features (e.g., inventory, sales, finance) rather than technical layers.
* **API-Ready Frontend:** Structuring the frontend UI (state, hooks, components) so it can seamlessly integrate with real APIs in later phases.
* **Role-Aware Architecture:** Designing the UI to adapt based on user roles and permissions (Owner, Manager, Staff, etc.).
* **Centralized Routing:** Managing all application routes in a single, coherent structure.
* **Consistent Data Models:** Ensuring uniform data structures across the application.
* **Reusable Tables & Forms:** Creating standardized data tables and forms for consistency.
* **Reusable Status Indicators & Dashboard Cards:** Establishing standard visual patterns for statuses and metrics.

## Technical Decisions
* **Phase 0:** Focus entirely on Frontend UI (React + Vite + Tailwind + React Router + Recharts). State is mocked.
* **Phase 1 (Backend Architecture):** FastAPI, Python 3.12+, SQLAlchemy ORM. SQLite fallback used due to local Postgres unavailability, keeping models agnostic.
* **Phase 1 (Database Strategy):** PostgreSQL natively designed (using UUIDs and strict business-level boundaries), but utilizing generic SQLAlchemy types where possible to allow SQLite as a headless local fallback during development. Alembic is configured to handle migrations.
* **Phase 2 (REST API Layer):** Introduced `/api/v1` routes utilizing layered architecture. FastAPI routes handle HTTP serialization and Pydantic validation. Business logic (like transaction handling, inventory deductions, order cost calculations) operates in modular `app/services` implementations.
* **Phase 3 (Frontend ↔ Backend Integration):** Integrated the React UI with the FastAPI backend using a centralized API client (`src/api/client.js`) and reusable React Hooks (`src/api/hooks.js`). Removed static `mockData` from lists and detail screens. Added loading, error, and empty states. Preserved N+1 query limits and utilized API-driven pagination/search.
* **Phase 4 (Complete Business Workflows):** Implemented atomic database transactions and end-to-end operational workflows:
  - *Sales Workflow:* Atomic inventory pre-validation, stock deduction, `SALE` stock movement creation, customer credit limit verification, customer balance update, order item snapshotting, audit logging, and notifications.
  - *Purchases Workflow:* PO creation with supplier balance tracking, partial/full receiving (`PURCHASE_RECEIPT` movements), automatic PO status recalculation (`Ordered` -> `Partially Received` -> `Received`), and excess receiving prevention.
  - *Returns & Refunds:* Dedicated `Return` and `ReturnItem` models with Alembic migration (`7466fde0ae5c`), inventory restoration (`RETURN` movements), order and customer balance adjustments, and maximum returnable quantity enforcement.
  - *Payments Workflow:* Order and PO payment tracking (`POST /orders/{id}/payments`, `POST /purchase-orders/{id}/payments`), balance reconciliation (`amount_paid`, `balance_due`, `payment_status`), and customer/supplier balance reductions.
  - *Inventory Adjustments:* Controlled stock adjustments with positive/negative quantity validation, historical tracking in `StockMovement`, and low stock alert notifications.
  - *Audit & System Notifications:* Automatic audit logs on state-altering actions (`ORDER_CREATED`, `ORDER_CANCELLED`, `PURCHASE_ORDER_RECEIVED`, `RETURN_PROCESSED`, `STOCK_ADJUSTED`, `PAYMENT_RECEIVED`) and real-time operational notifications.
* **Multi-Tenant Foundation & Authentication (Phase 5):** All primary entities strictly include a `business_id` for multi-tenant isolation. Authentication is governed by Argon2id password hashing and PyJWT tokens transmitted via Bearer headers and HttpOnly cookies. In authenticated contexts, the user's token identity is authoritative and completely overrides any client-supplied `X-Business-ID` header, preventing tenant spoofing. Unauthenticated requests retain `X-Business-ID` support strictly for headless tests and backward compatibility.
* **Audit Actor Attribution:** Replaced generic `"SYSTEM"` actor defaults in audit logs with authenticated user identity (`user.name or user.id`).
* **Role-Based Access Control (Phase 5 RBAC):** Centralized via `require_roles(...)` dependency enforcing least-privilege access across Owner, Admin, Manager, and Staff roles. Unauthenticated requests receive HTTP 401, inactive users receive HTTP 401, and unauthorized roles receive HTTP 403. Privilege escalation guards prevent users from self-promoting and prevent Admins from creating or promoting Owners.
* **Frontend Authentication & RBAC UI (Phase 5 UI):** Centralized `AuthContext` managing authoritative user profile and session states restored via `GET /api/v1/auth/me`. Protected routes enforce login redirection (`ProtectedRoute`), while role-gated routes enforce permission boundaries without logging users out (`RoleRoute`, `AccessDenied`). Dynamic navigation adapts visible items to user roles (Owner, Admin, Manager, Staff), while top header displays user profile, role badge, initials, and logout. Dedicated User Management view (`/users`) allows Owner/Admin to manage accounts, enforce role limits, and toggle activation status.
* **Immutability Principle:** Key transactional metadata (like `unit_price`, `tax_rate`, `quantity`) is hard-copied into line items (`OrderItem`, `PurchaseOrderItem`) rather than referenced, guaranteeing historical ledger immutability if product master data changes.
* **Business Intelligence & Analytics Engine (Phase 6):** Centralized analytics calculation service (`analytics_service.py`) executing performant database-level SQL aggregations across existing transactional records (orders, inventories, movements, payments, returns, expenses). Strictly multi-tenant isolated by deriving `business_id` exclusively from JWT tokens. Enforces role-based access control allowing `Owner`, `Admin`, and `Manager` while forbidding `Staff` (403). Deterministic product velocity rules classify fast-moving ($V \ge 0.2$ units/day) versus slow-moving/stagnant inventory. COGS and Gross Profit are calculated directly from recorded unit selling prices and product purchase cost prices, with transparent coverage percentage reporting.
* **Smart Business Insights Engine (Phase 7):** Deterministic, rules-based business intelligence layer (`insights_service.py`) operating without external LLMs or black-box dependencies. Evaluates operational health across inventory (out-of-stock, low-stock, slow-moving capital, capital concentration), sales (revenue concentration, return rates, activity levels), finance (net losses, compressed gross/net margins, accounts receivable risk, payables pressure), customer relationships (account concentration, large overdue balances, inactive key accounts), supplier relationships (spend concentration, large payables, pending PO backlog), and data quality (cost price completeness). Every insight is explainable (title, message, metric, current value, threshold, action recommendation, evidence) and prioritized by urgency (Critical, Warning, Info). Centralized, documented configuration dataclass (`InsightThresholds`) governs all deterministic rule boundaries. Strictly guarded for `Owner`, `Admin`, and `Manager` roles with automated cross-tenant isolation.
* **Smart Business Insights Frontend Integration (Phase 7 Task 2):** Connects `GET /api/v1/insights` to the React client via an upgraded API client layer supporting parameter serialization and race-condition prevention (`useApi`). Prominently features an automated Smart Business Insights section on the main executive Dashboard (`Dashboard.jsx`) with dynamic summary metric cards (`InsightsSummaryCards.jsx`), severity filtering, and top prioritized cards (`InsightsList.jsx`) displaying actionable recommendations and expandable evidence drawers. A dedicated management console at `/smart-insights` (`SmartInsights.jsx`) provides full domain category tabs (Inventory, Finance, Sales, Customers, Suppliers, Data Quality), date period bounding, and direct one-click navigation links to underlying modules (`/inventory`, `/products`, `/customers`, `/suppliers`, `/purchase-orders`, `/profit-loss`).
* **Advanced Features & Operational Depth (Phase 8):**
  - *Multi-Store / Multi-Branch:* `Branch` entity enables multi-location retail/branch management, warehouse-to-branch linkage, order branch attribution, dedicated `/branches` management console, and a global header branch selector.
  - *Advanced Warehouse Management & Stock Transfers:* Facility summary endpoint (`GET /warehouses/{id}/summary`) computes aggregate stock units, total facility valuation, low-stock, and out-of-stock items. Full warehouse console (`/warehouses`) supports interactive facility analytics and warehouse-to-warehouse stock transfers. Transfer status lifecycle (`Pending` -> `In Transit` -> `Completed`) atomically decreases source inventory, increases destination inventory, and writes immutable `TRANSFER_OUT` and `TRANSFER_IN` `StockMovement` records.
  - *Universal Search:* `/api/v1/search?q=...` searches products (name, sku, barcode), customers, suppliers, orders, purchase orders, warehouses, and branches with multi-tenant scoping and a debounced header popover.
  - *Barcode / QR POS Scanner:* Direct product barcode resolution (`/api/v1/products/barcode/{barcode}`) and a dedicated POS scanner input supporting instant Enter-to-cart workflows with audible/visual feedback.
  - *Reports Center & Live CSV Export:* `/api/v1/reports/*` generates live operational calculations for Sales, Inventory, Purchases, Expenses, and Customers with live modal preview inspection and streaming CSV file export.
  - *Document Vault:* Secure file archive supporting multipart uploads (`/api/v1/documents/upload`), mime/size enforcement, tenant folder isolation, safe file streaming download, and deletion.
  - *Goals & Targets:* Operational goals system (`BusinessGoal`) tracking Revenue, Order Volume, Customer Count, and Net Profit, computing real-time progress percentages against live orders, displayed via a dedicated widget on the executive dashboard.
  - *Business Calendar & Operational Milestones:* Uniform timeline endpoint (`/api/v1/calendar/events`) tracking supplier PO deliveries, order fulfillment dues, and goal deadlines.
  - *Demo Mode & Seeded Access:* Instant test logins for Owner (`sarah@techhaven.com`), Manager (`john@techhaven.com`), and Staff (`mike@techhaven.com`), plus header demo badge.
* **Production Readiness & Hardening (Phase 9):**
  - *Strict CORS Security:* Removed wildcard origin reflection (`allow_origins=["*"]`) with credentials. Origin access is strictly checked against parsed `CORS_ORIGINS` settings from environment variables.
  - *Operational Health Check:* Upgraded `/health` and `/api/v1/health` with live `SELECT 1` database query ping to provide deep visibility to orchestrators into application versus database health.
  - *Frontend Bundle Optimization:* Implemented Rollup `manualChunks` in `vite.config.js` and route-level `React.lazy` with `Suspense` in `App.jsx`, eliminating chunk warnings and code-splitting the application into chunks under 380 kB.
  - *Negative Numeric Bounds:* Enforced non-negative validation (`Field(..., ge=0)`) on product prices, costs, and thresholds.
  - *IDOR Prevention:* Automated security test suite in `tests/test_phase9_security_production.py` verifies cross-tenant isolation and 404/403 responses across all entities.
  - *Production Documentation:* Created root `README.md` and complete `docs/DEPLOYMENT.md` detailing PostgreSQL migration procedures and cloud infrastructure deployment (Render, Vercel, Supabase, Neon).



# Production Deployment Guide

This guide describes the recommended production architecture, environment configuration, database migration process, and deployment procedures for the **Small Business Operations Management Platform**.

---

## 🏛️ Recommended Production Architecture

```
                       +---------------------------------------+
                       |              End Users                |
                       +---------------------------------------+
                                           |
                                  HTTPS / TLS 1.3
                                           |
             +-----------------------------+-----------------------------+
             |                                                           |
             v                                                           v
+-----------------------------+                             +-----------------------------+
|    Frontend SPA (Vite)      |                             |   Backend API (FastAPI)     |
|  Hosted on Vercel / Netlify | ---- REST API (JWT auth) -> |   Hosted on Render / Railway|
|   or AWS CloudFront + S3    |                             |      or AWS ECS / Fly.io    |
+-----------------------------+                             +-----------------------------+
                                                                           |
                                                                   SQLAlchemy 2.0 Pool
                                                                           |
                                                            +-----------------------------+
                                                            |     Managed PostgreSQL      |
                                                            |  Neon / Supabase / AWS RDS  |
                                                            +-----------------------------+
```

| Component | Recommended Platform | Notes |
|---|---|---|
| **Frontend** | Vercel, Netlify, or Cloudflare Pages | Static single-page application with client-side routing fallback |
| **Backend** | Render Web Service, Railway, AWS ECS, or Fly.io | Python 3.12 container running Gunicorn + Uvicorn workers |
| **Database** | Managed PostgreSQL (Neon, Supabase, AWS RDS, Railway) | PostgreSQL 14+ with connection pooling enabled |
| **Storage** | Persistent Block Storage or AWS S3 | Used for document vault uploads |

---

## 🔐 Environment Variables

### Backend Configuration

Set these variables in your production container environment (e.g., Render Dashboard, Railway Variables, or `.env` in production):

```ini
# Environment mode
ENVIRONMENT=production

# Database Connection (Target: PostgreSQL)
DATABASE_URL=postgresql://sbm_user:SuperSecurePassword123!@db-host.supabase.co:5432/sbm_production

# JWT Authentication
# IMPORTANT: Generate a 256-bit random hex key: openssl rand -hex 32
JWT_SECRET_KEY=e83a7f920bc481239c0f0a41d957ba5e839174bb7c4e519c2ef3840134bc893a
SECRET_KEY=e83a7f920bc481239c0f0a41d957ba5e839174bb7c4e519c2ef3840134bc893a
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Allowed CORS Origins (comma-separated, no trailing slashes)
# Set strictly to your production frontend domains
CORS_ORIGINS=https://app.yourdomain.com,https://pos.yourdomain.com
```

### Frontend Configuration

Set these variables prior to running `npm run build`:

```ini
# Base URL for API requests (must include /api/v1)
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

---

## 🗄️ Database Provisioning & Migrations

The application uses SQLAlchemy with standard PostgreSQL-compatible data types (`Numeric(12, 2)`, `String`, `DateTime`, `Boolean`, `Text`, `JSON`).

### 1. Connecting to PostgreSQL
In production, supply a PostgreSQL connection URL:
```bash
DATABASE_URL=postgresql+psycopg2://username:password@hostname:5432/databasename
```

### 2. Running Migrations
Run Alembic migrations during the deployment build phase or pre-deploy hook:

```bash
cd backend
alembic upgrade head
```

All 9 migrations will execute in order, establishing the complete relational schema with tenant-scoped indexes and unique constraints:
- `1a2b3c4d5e6f` (Base operational tables)
- `2b3c4d5e6f7a` (Return orders and refunds)
- `3c4d5e6f7a8b` (Users, authentication, and RBAC)
- `4d5e6f7a8b9c` (Branches and multi-store support)
- `5e6f7a8b9c0d` (Stock transfers)
- `6f7a8b9c0d1e` (Business goals and KPIs)
- `7a8b9c0d1e2f` (Audit log actor indices)
- `8a1b2c3d4e5f` (Document vault metadata)

### 3. (Optional) Initializing Seed Data
To populate demo users, demo branches, initial product catalog, and categories:
```bash
python seed_data.py
```

---

## 🚀 Step-by-Step Deployment Walkthrough

### Option A: Render + Supabase / Neon (Recommended for Ease)

1. **Database Setup**:
   - Create a free PostgreSQL instance on [Neon](https://neon.tech) or [Supabase](https://supabase.com).
   - Copy the connection string (e.g. `postgresql://...`).

2. **Backend Deployment (Render)**:
   - Create a new **Web Service** pointing to your Git repository.
   - **Root Directory**: `backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 4`
   - **Environment Variables**: Add `ENVIRONMENT`, `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`.
   - **Health Check Path**: `/api/v1/health`

3. **Frontend Deployment (Vercel / Netlify)**:
   - Create a new project pointing to your Git repository.
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**: Set `VITE_API_BASE_URL=https://<your-render-app>.onrender.com/api/v1`.
   - **SPA Routing**: Add a rewrite rule for single page apps:
     - For Vercel, `vercel.json`:
       ```json
       {
         "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
       }
       ```
     - For Netlify, `_redirects` in `frontend/public/`:
       ```
       /*  /index.html  200
       ```

---

## 🩺 Health Check & Monitoring

The backend exposes an operational health endpoint at both `/health` and `/api/v1/health`.

### Expected Healthy Response (HTTP 200)
```json
{
  "status": "ok",
  "app": "healthy",
  "database": "connected"
}
```

### Degraded State (Database Unavailable)
```json
{
  "status": "degraded",
  "app": "healthy",
  "database": "error: connection to server was lost"
}
```

Configure your container orchestrator (e.g., Kubernetes, AWS ECS, or Render) to monitor `/api/v1/health` with:
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Unhealthy threshold**: 3 consecutive failures

---

## 🛡️ Pre-Flight Production Checklist

Before announcing general availability:

- [x] **Strict CORS**: `CORS_ORIGINS` contains only verified production frontend domain(s).
- [x] **Secret Keys**: `JWT_SECRET_KEY` is set to a cryptographically strong 256-bit secret.
- [x] **SSL / HTTPS**: Enforce HTTPS on both API and Web domains.
- [x] **Migrations**: `alembic upgrade head` verified against production database.
- [x] **Bundle Optimization**: Verified bundle splitting produces chunks `< 400 kB`.
- [x] **Regression Suite**: All 8 backend test suites execute and pass.
- [x] **Storage Volume**: Document vault destination directory has persistent write permissions.
- [x] **Database Backups**: Automated daily snapshots enabled on managed PostgreSQL instance.

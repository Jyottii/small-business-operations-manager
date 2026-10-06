# Production Deployment Guide

This guide describes the production architecture, environment configuration, database migration process, and deployment procedures for the **Small Business Operations Management Platform** using the target architecture:

```text
GitHub
   │
   ├── Frontend → Vercel
   │
   └── Backend → Render
                    │
                    └── PostgreSQL → Neon
```

---

## 🏛️ Target Production Architecture

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
|      Hosted on Vercel       | ---- REST API (JWT auth) -> |      Hosted on Render       |
|    (SPA rewrite fallback)   |                             |  (Uvicorn / Gunicorn ASGI)  |
+-----------------------------+                             +-----------------------------+
                                                                           |
                                                                   SQLAlchemy 2.0 Pool
                                                                           |
                                                            +-----------------------------+
                                                            |     Managed PostgreSQL      |
                                                            |        Hosted on Neon       |
                                                            +-----------------------------+
```

| Layer | Provider | Configuration |
|---|---|---|
| **Source Control** | GitHub | Main branch, clean working tree, secrets excluded |
| **Frontend SPA** | Vercel | Root `frontend`, framework `Vite`, build `npm run build`, output `dist` |
| **Backend API** | Render | Root `backend`, Python 3.12, host `0.0.0.0`, port `$PORT` |
| **Database** | Neon PostgreSQL | Serverless PostgreSQL with SSL connection pooling |
| **Document Storage** | Local / Persistent Volume | Configurable via `UPLOAD_DIR` environment variable |

---

## 📦 Step 1: Push Repository to GitHub

The repository is already initialized with a clean commit, with all sensitive files, SQLite databases, node_modules, and uploads strictly excluded by `.gitignore`.

To push to your GitHub account:

```bash
# 1. Create a new repository on https://github.com/new (do NOT initialize with README/license)

# 2. Add remote origin (replace with your GitHub repository URL):
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 3. Push to main:
git branch -M main
git push -u origin main
```

---

## 🐘 Step 2: Provision Neon PostgreSQL

1. Log in to [Neon Console](https://console.neon.tech).
2. Create a new project (e.g. `small-business-manager-db`).
3. Under **Connection Details**, select **Pooled connection** and copy your connection string:
   ```text
   postgresql://<user>:<password>@<ep-xyz>.neon.tech/<dbname>?sslmode=require
   ```
4. Run Alembic migrations against your Neon database from your local machine or CI/CD:
   ```bash
   cd backend
   # Set the database URL temporarily in your shell
   $env:DATABASE_URL="postgresql://<user>:<password>@<ep-xyz>.neon.tech/<dbname>?sslmode=require"
   alembic upgrade head
   ```
   *(All 9 migrations will execute in order, establishing all tables, foreign keys, unique constraints, and indexes.)*

5. (Optional) Seed initial demo accounts and business catalog:
   ```bash
   python seed.py
   ```
   *(Creates demo business "TechHaven Electronics", Owner, Manager, Staff accounts, products, warehouses, and branches.)*

---

## ⚡ Step 3: Deploy Backend to Render

### Option A: Automatic Deployment using Render Blueprint (`render.yaml`)
The repository includes a root `render.yaml` Blueprint file:
1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Blueprint**.
3. Select your GitHub repository.
4. Render will automatically detect `render.yaml` and prompt you for:
   - `DATABASE_URL`: Paste your Neon connection string.
   - `CORS_ORIGINS`: Set to your Vercel frontend domain (or temporary `http://localhost:5173` until Vercel URL is generated).
5. Render will automatically generate `JWT_SECRET_KEY` and trigger the build.

### Option B: Manual Web Service Setup
1. In Render Dashboard, click **New +** > **Web Service**.
2. Connect your GitHub repository.
3. Configure the service settings:
   - **Name**: `small-business-manager-api`
   - **Root Directory**: `backend`
   - **Language**: `Python 3`
   - **Python Version**: `3.12.7` (or configured via `backend/.python-version`)
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/v1/health`
4. Add Environment Variables:
   - `ENVIRONMENT` = `production`
   - `PYTHON_VERSION` = `3.12.7`
   - `DATABASE_URL` = `<your-neon-connection-string>`
   - `JWT_SECRET_KEY` = `<secure-random-32-byte-hex-string>` *(generate with `openssl rand -hex 32`)*
   - `CORS_ORIGINS` = `<your-vercel-domain>` *(e.g. `https://small-business-manager.vercel.app`)*
5. Click **Create Web Service**.

Once deployed, copy your Render Web Service URL (e.g. `https://small-business-manager-api.onrender.com`).

---

## 🌐 Step 4: Deploy Frontend to Vercel

1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** > **Project**.
3. Import your GitHub repository.
4. In the **Configure Project** screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click `Edit` and select `frontend`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL` = `https://<your-render-app>.onrender.com/api/v1`
   *(Important: Ensure the URL ends with `/api/v1` as required by the API client).*
6. Click **Deploy**.

Vercel will build the frontend and assign a production URL (e.g. `https://small-business-manager.vercel.app`).

### SPA Routing & Direct URL Navigation
The file [`frontend/vercel.json`](file:///C:/Users/Jyoti%20Varma/.gemini/antigravity/scratch/small-business-manager/frontend/vercel.json) is pre-configured with rewrite rules ensuring direct browser navigation and page reloads on routes like `/dashboard`, `/inventory`, `/orders`, and `/smart-insights` resolve cleanly to `/index.html`.

---

## 🔄 Step 5: Finalize CORS Configuration

Now that your production Vercel frontend URL is known:
1. Return to the **Render Dashboard** > **small-business-manager-api** > **Environment**.
2. Update `CORS_ORIGINS` to match your Vercel domain:
   ```text
   CORS_ORIGINS=https://<your-project>.vercel.app
   ```
   *(If you have custom domains, separate them with commas without spaces: `https://app.yourdomain.com,https://<your-project>.vercel.app`)*
3. Render will redeploy with strict CORS filtering.

---

## 📁 Important: Document Storage in Production

The application's **Document Vault** stores uploaded files locally in `UPLOAD_ROOT`:
- **Development Default**: `backend/uploads/`
- **Configurable Location**: Override via the `UPLOAD_DIR` environment variable.

### Ephemeral Storage Advisory:
On standard cloud container deployments (such as Render Free / Starter instances), the container filesystem is **ephemeral**. Files written to the local disk are reset upon new deployments or container restarts.

**Recommendations for Production Document Persistence**:
1. **Render Persistent Disk**:
   - In Render, add a **Disk** to your Web Service (e.g., Mount Path `/var/data/uploads`).
   - Set the environment variable: `UPLOAD_DIR=/var/data/uploads`.
2. **Object Storage Integration**:
   - For high-scale deployments, connect an AWS S3, Cloudflare R2, or Supabase Storage bucket.
3. **Honest Operational Notice**:
   - The application does not silently imply that documents uploaded to an ephemeral container will persist indefinitely across redeployments without persistent volume backing.

---

## 🩺 Operational Health Checks & Verification

### 1. Backend Health Check
```bash
curl -s https://<your-render-app>.onrender.com/api/v1/health
```
**Expected Response (HTTP 200)**:
```json
{
  "status": "ok",
  "app": "healthy",
  "database": "connected"
}
```

### 2. OpenAPI / Swagger Documentation
Navigate to:
```text
https://<your-render-app>.onrender.com/docs
```

### 3. Authentication Smoke Test
```bash
curl -X POST https://<your-render-app>.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sarah@techhaven.com","password":"Password123!"}'
```
**Expected Response (HTTP 200)**:
Returns JSON containing JWT access token, token expiration, and user object.

---

## 🛡️ Production Pre-Flight Checklist

- [x] **Strict CORS**: `CORS_ORIGINS` restricts requests exclusively to verified frontend origins.
- [x] **Secret Keys**: `JWT_SECRET_KEY` uses a cryptographically random 256-bit key; no development secrets in production.
- [x] **PostgreSQL Target**: PostgreSQL connection string with SSL (`sslmode=require`) configured.
- [x] **Migrations**: Alembic migration sequence verified from empty database to head.
- [x] **Code Splitting**: Frontend bundles split into chunks `< 380 kB` with zero bundle warnings.
- [x] **Tenant Scoping**: All queries filter strictly by `business_id == current_user.business_id`.
- [x] **Zero Secrets in Git**: Verified that `.env`, `.db`, `node_modules`, and uploaded files are excluded from git.

# Project Setup Guide

## Prerequisites

| Tool | Version | Used By |
|---|---|---|
| Python | 3.12+ | pms-backend |
| PostgreSQL | 16+ | pms-backend |
| Node.js | 24+ | pms-frontend |
| Android Studio | Ladybug 2024.2+ | pms-android |
| JDK | 17+ | pms-android |
| Git | 2.x | All |

## Clone All Repos

```bash
git clone --recurse-submodules git@github.com:utexas-demo/pms-backend.git
git clone --recurse-submodules git@github.com:utexas-demo/pms-frontend.git
git clone --recurse-submodules git@github.com:utexas-demo/pms-android.git
```

## Backend Setup

```bash
cd pms-backend

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env: set DATABASE_URL, SECRET_KEY, ENCRYPTION_KEY

# Run migrations (requires PostgreSQL)
alembic upgrade head

# Start server
python -m uvicorn pms.main:app --reload
# → http://localhost:8000/docs
```

## Frontend Setup

```bash
cd pms-frontend

# Install
npm install

# Configure
cp .env.example .env.local
# Edit .env.local: set NEXT_PUBLIC_API_URL if not localhost:8000

# Start dev server
npm run dev
# → http://localhost:3000
```

## Android Setup

```bash
cd pms-android

# Open in Android Studio
# File → Open → select pms-android/

# Sync Gradle
# Run on emulator (connects to backend at 10.0.2.2:8000)
```

## Docker Compose (Full Stack)

Run all services (backend, frontend, PostgreSQL) with a single command:

```bash
cd pms-backend

# Configure environment
cp .env.example .env
# Edit .env: set SECRET_KEY and ENCRYPTION_KEY to real values
# Generate an encryption key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Generate a secret key:      python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start all services
docker compose up --build -d
```

| Service | URL | Notes |
| --- | --- | --- |
| Backend API | `http://localhost:8000` | FastAPI + Swagger docs at `/docs` |
| Frontend | `http://localhost:3000` | Next.js |
| PostgreSQL | `localhost:5432` | User: `postgres`, Password: `postgres`, DB: `pms` |

> **Note:** The `.env` file must use `postgres` (the Docker service name) as the database host, not `localhost`:
> `DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/pms`

To stop all services:

```bash
docker compose down        # stop containers
docker compose down -v     # stop and remove volumes (resets database)
```

## Authentication (Dev Workaround)

The login endpoint (`POST /auth/token`) is currently a stub — it does not issue real JWTs. Two options exist for development:

### Option A: Frontend Auth Bypass (Recommended for UI Work)

Enable auth bypass mode to skip the login page and inject a mock user. Add to `pms-frontend/.env.local`:

```bash
NEXT_PUBLIC_AUTH_BYPASS_ENABLED=true
NEXT_PUBLIC_AUTH_BYPASS_ROLE=admin        # admin | physician | nurse
NEXT_PUBLIC_AUTH_BYPASS_EMAIL=dev@localhost
NEXT_PUBLIC_AUTH_BYPASS_NAME=Dev User
```

This injects a mock user into the AuthProvider and displays a **non-dismissible yellow warning banner** at the top of every page. The banner disappears when bypass mode is disabled.

> **Warning:** Never enable auth bypass outside local development. The `NEXT_PUBLIC_` prefix exposes these values in the browser bundle.

### Option B: Manual JWT Token (for API Testing)

Generate a valid token from the backend to test protected API routes:

```bash
# From inside the running backend container:
docker compose exec backend python -c "
from pms.services.auth_service import create_access_token
print(create_access_token('dev-admin-id', 'admin'))
"
```

Use the token in API requests:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/patients/
```

Valid roles for RBAC: `admin`, `physician`, `nurse`.

## Running Tests

```bash
# Backend
cd pms-backend && pytest

# Frontend
cd pms-frontend && npm run test:run

# Android
cd pms-android && ./gradlew test
```

## Updating Shared Docs

When docs change in the `demo` repo, update the submodule in each project:

```bash
cd pms-backend/docs && git pull origin main && cd .. && git add docs && git commit -m "Update docs submodule"
cd pms-frontend/docs && git pull origin main && cd .. && git add docs && git commit -m "Update docs submodule"
cd pms-android/docs && git pull origin main && cd .. && git add docs && git commit -m "Update docs submodule"
```

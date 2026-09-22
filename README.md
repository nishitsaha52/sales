# TCG Partner Portal

Phase 0 establishes the local development foundation for the Partner Portal:

- React, TypeScript, Vite, React Router, and TanStack Query
- FastAPI, SQLAlchemy 2, Pydantic, and Alembic
- PostgreSQL with pgvector
- Private MinIO object storage
- JWT authentication, roles, permissions, audit events, structured logs, and request IDs
- Idempotent master-data seeds and Docker Compose

Phase 1A adds partner access and management:

- Public partner self-registration with pending approval
- TCG-created active partners and primary administrators
- Partner type, tier, and country master data
- Approval, rejection, suspension, reactivation, and rejection reasons
- Partner profiles and partner-user administration
- Backend-enforced TCG/partner role checks and partner data isolation

## Prerequisites

- Python 3.12 or newer
- Node.js 22 or newer
- Docker Desktop (only needed when PostgreSQL and MinIO are not already running)

## Environment

Copy `.env.example` to `.env`, then adjust the database credentials, MinIO credentials, and
`JWT_SECRET_KEY` for your local services. `MINIO_ENDPOINT` is an SDK endpoint such as
`localhost:9000`; it must not include `http://`.

The checked-in defaults expect:

| Service | Address | Development credentials |
| --- | --- | --- |
| PostgreSQL | `localhost:5432` | `partner_portal` / `partner_portal` |
| MinIO API | `localhost:9000` | `minioadmin` / `minioadmin` |
| MinIO console (Compose) | `http://localhost:9001` | same as above |

Never reuse these development credentials outside local development.

## Use the existing PostgreSQL and MinIO services

From PowerShell:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[dev]"
Set-Location backend
alembic upgrade head
python -m app.db.seed
python -m app.storage.bootstrap
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`. API documentation is at `http://localhost:8000/docs`.

## Start with Docker Compose

If ports 5432 and 9000 are free, infrastructure only can be started with:

```powershell
docker compose up -d postgres minio minio-init
```

To build and run the complete stack:

```powershell
docker compose --profile app up --build
```

The full stack exposes the frontend on port 5173 and the API on port 8000. Compose maps the
MinIO S3 API to port 9000 and its administrative console to port 9001.

## Verification

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/live
Invoke-RestMethod http://localhost:8000/api/v1/health/ready

Set-Location backend
ruff check .
pytest

Set-Location ..\frontend
npm run lint
npm run build
```

The seed command is safe to rerun. It creates the six agreed roles, their initial permissions,
and a local administrator from `SEED_ADMIN_*`. The default local login is
`admin@tcgdigital.com` / `ChangeMe123!`; change it in `.env` before first use.

After pulling a new phase, apply its migration and master data before restarting the API:

```powershell
Set-Location backend
python -m alembic upgrade head
python -m app.db.seed
```

## API conventions

- All public API routes start with `/api/v1`.
- Identifiers are UUIDs and timestamps are UTC.
- Errors use `{ "error": { "code", "message", "details", "request_id" } }`.
- Clients may send `X-Request-ID`; otherwise the API creates one and returns it.
- Protected routes use a bearer access token from `POST /api/v1/auth/token`.

Phase 1A routes are documented interactively at `http://localhost:8000/docs`. The public
registration entry point is `http://localhost:5173/register`; authenticated users are routed to
their role-aware workspace after login.


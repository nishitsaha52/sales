# TCG Partner Portal

Phase 0 establishes the local development foundation for the Partner Portal:

- React, TypeScript, Vite, React Router, and TanStack Query
- FastAPI, SQLAlchemy 2, Pydantic, and Alembic
- PostgreSQL with pgvector
- Private MinIO object storage
- JWT authentication, roles, permissions, audit events, structured logs, and request IDs
- Idempotent master-data seeds and integration with existing PostgreSQL and MinIO services

Phase 1 adds partner access and management:

- Public partner self-registration with pending approval
- TCG-created active partners and primary administrators
- Partner type, tier, and country master data
- Approval, rejection, suspension, reactivation, and rejection reasons
- Partner profiles and partner-user administration
- Backend-enforced TCG/partner role checks and partner data isolation

Product and pricing management includes:

- Extensible product and SKU master data
- Effective-dated USD list prices
- Configurable partner-type commercial rules and tier benefits
- Effective-dated partner/SKU overrides
- Deterministic partner price resolution with an admin-only calculation breakdown
- Restricted partner pricing that never exposes another partner's terms

The remaining Phase 1 workflows add private documents, customers and protected deals, pipeline
history, quote revisions and price snapshots, MAF review/issuance, and orders through activation
with a durable `ORDER_CONFIRMED` event. Migration, seed, verification, and end-to-end smoke-test
instructions are consolidated in [Phase 1 Implementation and Operations Guide](docs/Phase1-Implementation.md).

## Prerequisites

- Python 3.12 or newer
- Node.js 22 or newer
- Running PostgreSQL and MinIO containers, reachable on the ports configured in `.env`
- The PostgreSQL database named by `DATABASE_URL` already exists
- The MinIO bucket named by `MINIO_BUCKET` already exists and is private

## Environment

Copy `.env.example` to `.env` only when `.env` does not already exist. Configure the PostgreSQL
URL, MinIO endpoint and bucket, JWT secret, CORS origins, and seed administrator for your local
services. `MINIO_ENDPOINT` is the MinIO S3 API endpoint, such as `localhost:9000`; it must not
include `http://` or a path. Do not commit `.env`.

## Use the existing PostgreSQL and MinIO services

From the repository root, first confirm that both containers are running and exposing the expected
ports:

```powershell
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
```

Confirm that the output contains the PostgreSQL and MinIO containers and that their status is
healthy/running. Then prepare the local Python environment:

```powershell
Set-Location C:\Users\nishi\Desktop\sales
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path .venv)) { python -m venv .venv }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[dev]"
```

Verify the resources configured in `.env` before applying changes:

```powershell
# A successful response confirms that the configured PostgreSQL database exists and is reachable.
alembic current

# True confirms that the configured MinIO bucket exists.
python -c "from app.core.config import settings; from app.storage.client import get_minio_client; print(get_minio_client().bucket_exists(settings.MINIO_BUCKET))"
```

If either check fails, correct `.env` or create the missing database/private bucket before
continuing. Apply the schema and idempotent application setup from the repository root:

```powershell
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

## Verification

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/live
Invoke-RestMethod http://localhost:8000/api/v1/health/ready

python -m ruff check backend\app backend\tests backend\alembic
python -m mypy --config-file backend\pyproject.toml backend\app
python -m pytest -q backend

Set-Location frontend
npm run lint
npm run build
```

The seed command is safe to rerun. It creates the agreed roles, their initial permissions, and a
local administrator from the `SEED_ADMIN_*` values configured in `.env`.

After pulling a new phase, apply its migration and master data before restarting the API:

```powershell
alembic upgrade head
python -m app.db.seed
```

## API conventions

- All public API routes start with `/api/v1`.
- Identifiers are UUIDs and timestamps are UTC.
- Errors use `{ "error": { "code", "message", "details", "request_id" } }`.
- Clients may send `X-Request-ID`; otherwise the API creates one and returns it.
- Protected routes use a bearer access token from `POST /api/v1/auth/token`.

All Phase 1 routes are documented interactively at `http://localhost:8000/docs`. The public
registration entry point is `http://localhost:5173/register`; authenticated users are routed to
their role-aware workspace after login.

The Phase 1B seed creates mcube and LVA with the suggested development SKUs and configurable
placeholder commercial rules. It deliberately does not invent list prices; TCG Admin sets those
from **Products & SKUs** before resolved partner pricing appears.

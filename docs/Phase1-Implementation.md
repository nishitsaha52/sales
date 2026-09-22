# Phase 1 Implementation and Operations Guide

This guide is the operational reference for the Phase 1 implementation. Product requirements
remain in [PRD.md](PRD.md), confirmed decisions and current gaps remain in
[Memory.md](Memory.md), and the delivery roadmap remains in [Phases.md](Phases.md).

## 1. Delivered Scope

### Phase 1A — Partner Access and Management

- Public partner registration with TCG approval or rejection
- TCG-created partners and primary Partner Admin users
- Partner types, tiers, countries, profiles, users, roles, and permissions
- Suspension/reactivation controls and backend-enforced partner isolation

### Phase 1B — Product and Pricing

- Product and SKU masters with active/inactive lifecycle
- Effective-dated USD list prices
- Partner-type rules, tier adjustments, and partner/SKU overrides
- Deterministic partner pricing with an internal calculation breakdown
- mcube and LVA development catalog seeds; authoritative list prices are not seeded

Pricing resolves in this order:

1. Active SKU list price
2. Partner-type commercial rule
3. Tier adjustment
4. Partner-specific override
5. Final USD partner price

### Phase 1C — Content Repository

- Private MinIO object storage and PostgreSQL metadata
- Categories, product association, versions, SHA-256 checksums, and search filters
- All Partner, Partner Type, Partner Tier, Specific Partner, and TCG Internal visibility
- Authorized ten-minute presigned downloads

### Phase 1D–1E — Customers, Deals, and Pipeline

- Customer capture and partner-scoped deal registration
- Submit, reject, resubmit, and approve workflow
- Transaction-safe same-customer/product protection conflict check
- 90-day protection from approval, excluding terminal Won/Lost deals
- Pipeline stage history
- Won requires actual contract value and close date; Lost requires a reason

### Phase 1F — Quotes

- Quote creation from approved deals
- SKU pricing, quantities, line discounts, commercial model, and validity
- Line-level pricing snapshots and numbered final revisions
- TCG finalization, revision reopening, and partner acceptance

### Phase 1G — MAF

- MAF request linked to an approved deal
- Tender details and supporting attachments
- Review, return, approval, rejection, issue, and expiry workflow
- Issued-document requirement and protected downloads

### Phase 1H — Orders

- One order per accepted quote
- Immutable quote snapshot, billing details, and PO/signed-contract attachment
- Review, return, confirmation, provisioning, activation, and status history
- Durable `ORDER_CONFIRMED` record in `domain_events`

## 2. Prerequisites

- PostgreSQL is running and the configured database already exists.
- The PostgreSQL account can create tables and the `vector` extension.
- MinIO is running and reachable through the SDK endpoint in `MINIO_ENDPOINT`.
- The repository `.env` has the intended database, MinIO, JWT, CORS, and seed-admin values.
- Backend and frontend dependencies have been installed.

Do not put `http://` in `MINIO_ENDPOINT`; use an SDK endpoint such as `localhost:9000`. The MinIO
administrative console may use a different port depending on the local deployment.

Before applying a migration outside disposable local development, take an appropriate database
backup and verify the target `.env`.

## 3. Database Migrations

The migration chain is:

| Revision | Scope |
| --- | --- |
| `20260922_0001` | Foundation, identity, roles/permissions, audit, seed tracking, pgvector |
| `20260923_0002` | Partner types, tiers, countries, partners, and partner users |
| `20260923_0003` | Products, SKUs, prices, commercial terms, tier adjustments, overrides |
| `20260923_0004` | Documents, customers, deals, pipeline, quotes, MAF, orders, domain events |

To inspect the generated SQL without connecting to PostgreSQL:

```powershell
Set-Location C:\Users\nishi\Desktop\sales
python -m alembic upgrade head --sql
```

To apply the migration after verifying `.env`:

```powershell
Set-Location C:\Users\nishi\Desktop\sales
python -m alembic current
python -m alembic upgrade head
python -m alembic current
```

The final command should report revision `20260923_0004`.

## 4. Seeds and Object Storage

Run the idempotent seeds after migrating:

```powershell
python -m app.db.seed
```

Seed keys:

- `foundation-identity-v1`
- `phase-1a-partner-master-data-v1`
- `phase-1b-product-pricing-v1`
- `phase-1-remaining-permissions-v1`
- `phase-1-mcube-display-name-v1`

The seed creates the agreed roles, permissions, partner master data, development products/SKUs,
and provisional configurable commercial rules. It does not seed SKU list-price amounts.

Ensure the configured private bucket exists:

```powershell
python -m app.storage.bootstrap
```

Both commands are safe to rerun. An applied seed is skipped and an existing bucket is reused.
Bootstrap does not audit or replace an existing bucket policy, so verify that a pre-existing bucket
is private.

## 5. Start the Application

Start the API from the repository root:

```powershell
python -m uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```powershell
Set-Location C:\Users\nishi\Desktop\sales\frontend
npm run dev
```

Local entry points:

- Frontend: `http://localhost:5173`
- API documentation: `http://localhost:8000/docs`
- OpenAPI document: `http://localhost:8000/openapi.json`
- Liveness: `http://localhost:8000/api/v1/health/live`
- Readiness: `http://localhost:8000/api/v1/health/ready`

## 6. Automated Verification

Backend:

```powershell
Set-Location C:\Users\nishi\Desktop\sales
python -m ruff check backend\app backend\tests backend\alembic
python -m mypy --config-file backend\pyproject.toml backend\app
python -m pytest -q backend
python -m alembic upgrade head --sql
```

Frontend:

```powershell
Set-Location C:\Users\nishi\Desktop\sales\frontend
npm run lint
npx tsc -b --pretty false
npm run build
```

Last recorded baseline: 24 backend tests passed; Ruff, Mypy strict mode, ESLint, TypeScript, the
Vite production build, and offline migration rendering all passed.

## 7. Phase 1 Acceptance Smoke Test

### 7.1 Foundation and Authentication

1. Confirm liveness returns `status: ok`.
2. Confirm readiness reports PostgreSQL and MinIO as available.
3. Sign in using the seed administrator configured in `.env`.
4. Call `/api/v1/auth/me` and confirm the TCG Admin role and permissions.

### 7.2 Partner Access

1. As TCG Admin, create an active partner and its Partner Admin.
2. Sign out and submit another company through `/register`.
3. Sign back in as TCG Admin and approve or reject the pending registration.
4. For an active partner, create a Partner Sales user.
5. Verify a partner token cannot read or change another partner's resource by ID.
6. Suspend a test partner and confirm its users can no longer authenticate.

### 7.3 Product and Pricing

1. Open **Products & SKUs** as TCG Admin.
2. Configure an effective USD list price for at least one active SKU.
3. Open **Pricing**, select an active partner, and inspect the calculation breakdown.
4. Add a partner/SKU fixed or percentage override and confirm the resolved price changes.
5. Sign in as that partner and confirm only its authorized final pricing is returned.

### 7.4 Documents

1. Publish a small document for All Partners.
2. Confirm its metadata and first version appear in **Documents**.
3. Sign in as a partner and confirm the document can be listed and downloaded.
4. Publish a TCG Internal document and confirm the partner cannot list or download it.
5. Through the API, test a Partner Type, Partner Tier, or Specific Partner scope.
6. Upload another version and verify the version number and SHA-256 metadata change.

### 7.5 Deals and Pipeline

1. Register a deal for an active partner, customer, and product.
2. Submit and approve it as TCG; confirm a 90-day protection expiry is recorded.
3. Attempt the same customer/product for a second partner and confirm HTTP 409.
4. Move the approved deal through at least one pipeline stage.
5. Verify stage history through `GET /api/v1/deals/{deal_id}`.
6. Confirm Won is rejected without actual contract value and close date.
7. Confirm Lost is rejected without a reason.

### 7.6 Quotes

1. Create a quote from the approved deal.
2. Add a priced SKU with quantity and an optional line discount.
3. Finalize the quote as TCG and confirm revision 1 is stored.
4. Optionally reopen it, change the draft, and finalize revision 2.
5. Sign in as the owning partner and accept the final quote.
6. Confirm the snapshot retains the price used even if live pricing is changed later.

### 7.7 MAF

1. Create a MAF request against the approved deal.
2. Upload supporting tender evidence and submit it.
3. As TCG, return it with a reason or approve it.
4. Upload an attachment with kind `ISSUED_DOCUMENT`.
5. Issue the MAF and confirm its expiry metadata and protected download.

### 7.8 Orders

1. Create an order from the accepted quote.
2. Upload a PO or signed contract.
3. Submit the order and return it once with a correction reason if desired.
4. Confirm it as TCG.
5. Verify an `ORDER_CONFIRMED` row exists in `domain_events` for the order.
6. Move the order to Provisioning and then Active.
7. Verify the complete status history is retained.

### 7.9 Audit Review

Confirm high-value actions in `audit_logs`, including actor, role, entity, timestamp, changed
values, and request ID. Review partner, pricing, document, deal, quote, MAF, and order actions.

## 8. Operational Notes

- All authoritative commercial values use USD.
- Provisional pricing rules remain database configuration, not application constants.
- Partner-owned records are always authorized by the API using `partner_id`.
- Frontend visibility is a usability feature and is not an authorization boundary.
- MinIO objects remain private. Authorized downloads expire after ten minutes.
- Phase 1 uploads are limited to 25 MB.
- Quote and order snapshots must never be recalculated from current pricing.
- `ORDER_CONFIRMED` is persisted transactionally but is not externally published yet.
- MAF and quote expiry are not driven by a background scheduler in the current release.

## 9. Troubleshooting

### PostgreSQL reports that the database does not exist

The server can be reachable while the database named in `DATABASE_URL` is absent. Confirm the
database name, account, and port in `.env`, then create the database or point the URL to the
existing database before rerunning Alembic.

### Readiness reports MinIO as unavailable

Confirm `MINIO_ENDPOINT` is the S3 API endpoint rather than the browser-console URL, verify the
credentials, and rerun `python -m app.storage.bootstrap`.

### Resolved pricing is empty

The development seed intentionally creates no list-price amounts. Add an effective USD price to
an active SKU through **Products & SKUs**.

### A workflow action returns HTTP 403

Check both the user's role/permissions and its `partner_id`. A valid record ID does not bypass
partner ownership checks.

### An order cannot be submitted

Verify the source quote is Accepted and that the order has an attachment whose kind is
`PURCHASE_ORDER`.

### A MAF cannot be issued

Verify the MAF is Approved and has an attachment whose kind is `ISSUED_DOCUMENT`.

## 10. Known Acceptance Refinements

The authoritative list is maintained in [PRD.md](PRD.md#24-known-acceptance-refinements) and
[Memory.md](Memory.md#31-known-acceptance-gaps). Current items include deal editing before
resubmission, Customer Master editing/deduplication, complete document-scope/version controls in
the UI, richer attachment controls, scheduled expiry, quote approval thresholds, and external
publication of `ORDER_CONFIRMED`.

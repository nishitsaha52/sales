# Phase 1C–1H implementation

This release completes the Phase 1 partner-portal workflows.

## Delivered capabilities

- **Content repository:** private MinIO objects, PostgreSQL metadata, categories, partner/type/tier/internal visibility, versions, SHA-256 checksums, search filters, and short-lived protected downloads.
- **Customers and deals:** customer capture, partner-scoped deal registration, submit/reject/resubmit/approve lifecycle, conflict-safe customer-and-product protection for 90 days, supporting files, and audit events.
- **Pipeline:** Registered through Won/Lost stages with immutable stage history. Won requires actual value and close date; Lost requires a reason.
- **Quotes:** approved-deal prerequisite, resolved SKU pricing, line discounts, totals, commercial model, final revisions, and immutable pricing snapshots.
- **MAF:** approved-deal prerequisite, tender details, supporting files, review/return/approve/issue flow, issued document requirement, protected download, and expiry metadata.
- **Orders:** accepted-quote prerequisite, billing details, quote snapshot, PO/contract requirement, review/return/confirm/provision/activate flow, status history, and a durable `ORDER_CONFIRMED` domain event.

All partner-owned records are filtered and authorized by `partner_id` in the API. TCG users can work across partners. Stored files remain private; the API returns ten-minute presigned download links only after authorization.

## Apply locally

From `backend`, after confirming `.env` points to the intended PostgreSQL and MinIO instances:

```powershell
python -m alembic upgrade head
python -m app.db.seed
python -m app.storage.bootstrap
```

Restart the backend and frontend after applying the migration. The new navigation entries are **Documents**, **Deals & pipeline**, and **Quote to order**.

## Suggested smoke test

1. Sign in as TCG Admin; confirm the three new pages load.
2. Ensure every SKU used for quoting has an effective list price.
3. Register and submit a deal, then approve it as TCG.
4. Move the deal through one pipeline stage and verify the history through `GET /api/v1/deals/{id}`.
5. Create a quote, add a priced SKU, finalize it, and accept it while signed in as the partner.
6. Create an order, upload a PO/contract, submit, and confirm it as TCG.
7. Publish a document, sign in as a partner, and verify only authorized documents can be listed and downloaded.
8. Create a MAF request, upload supporting evidence, approve it, upload an `ISSUED_DOCUMENT`, and issue it.

The OpenAPI explorer at `http://localhost:8000/docs` exposes all request bodies and workflow endpoints.

## Automated verification

The implementation is covered by workflow-policy tests in `backend/tests/test_phase1_workflows.py`, in addition to the existing authentication, access, pricing, and API tests. Offline migration rendering is supported with:

```powershell
python -m alembic upgrade head --sql
```

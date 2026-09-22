# Partner Portal — Project Memory / Decision Log

This file captures the current agreed understanding so future development discussions do not reopen already-settled decisions unnecessarily.

Last implementation update: **23 September 2026**.

## 1. Product Context

- TCG Digital supplies mcube and LVA.
- Partners help TCG find customers, sell products, or implement them.
- The Partner Portal is the shared digital workspace between TCG and partner companies.

## 2. Local Development Stack

Confirmed:
- Frontend: React + TypeScript + Vite
- Frontend routing/data: React Router + TanStack Query
- Backend: Python + FastAPI
- Database: PostgreSQL
- Extension: pgvector
- Storage: MinIO AIStor
- ORM/migrations: SQLAlchemy async + Alembic
- Authentication: JWT bearer tokens
- Local infra: existing PostgreSQL and MinIO containers managed outside this repository
- Repository Dockerfiles and Docker Compose configuration were removed by project decision
- Frontend/backend developed and run from VS Code

Deployment is not being considered yet.

## 3. Phase 1

Confirmed Phase 1 includes:
- Access & Pricing
- Content Repositories
- Deal & Order Engine

Further clarification includes:
- Quote flow
- MAF
- Order flow

Implementation status:
- Phase 0 is complete.
- The core Phase 1A through Phase 1H workflow baseline is implemented in the repository.
- Applying migration `20260923_0004`, rerunning the idempotent seed, and completing live
  acceptance testing remain environment-owner actions.

Not Phase 1:
- Support/SLA
- Training/certification
- Full implementation project tracking
- License renewal
- QBR/health score
- AI/RAG

## 4. Partner Types

Confirmed:
- Reseller
- Referral
- System Integrator

These are partner types, not tiers.

## 5. Partner Tiers

Confirmed:
- Silver
- Gold
- Platinum

Tier qualification rules are not final.

Current development assumption:
- TCG Admin assigns tier manually.

Temporary configurable pricing assumptions:
- Silver: 0%
- Gold: 5%
- Platinum: 10%

These are not final stakeholder-approved commercial terms.

## 6. Territory

Confirmed:
- Territory means location/country.
- Multiple partners can operate in the same territory.
- Territory does not restrict deal registration.

## 7. Partner Creation

Confirmed:
- TCG can create partner manually.
- Partner can self-register.
- Self-registration requires approval.

## 8. Roles

Stakeholder delegated role design to development team.

Recommended:
TCG:
- TCG Admin
- TCG Sales

Partner:
- Partner Admin
- Partner Sales
- Partner Pre-Sales
- Partner Delivery

Implemented permission intent:
- TCG Admin: all permissions and cross-partner administration.
- TCG Sales: cross-partner sales workflows and read access to partner, catalog, pricing, and
  documents.
- Partner Admin: own-partner profile/users plus sales-management workflows.
- Partner Sales: own-partner sales-management workflows.
- Partner Pre-Sales and Partner Delivery: authorized read access only in the current seed.
- API ownership checks remain mandatory even when the frontend hides an action.

## 9. Deal Model

Current decision:
- One Deal/Opportunity entity in Phase 1.
- No separate Lead table initially.
- UI term = Deal.
- Backend/domain term = Opportunity.

## 10. Deal Approval

Confirmed:
- Admin approves/rejects.
- Rejected deal can be edited and resubmitted.
- Approved deal identity fields should not be freely changed.

## 11. Duplicate Rule

Confirmed:
- Same customer + same product + active protected deal = blocked/conflict.
- Same customer + different product = allowed.

## 12. Deal Protection

Confirmed:
- Starts on approval.
- The Phase 1 implementation sets `protection_expires_at` to 90 days after approval.
- Won and Lost are terminal stages and are excluded from active-protection conflicts.
- Same-customer/product conflict checks use a PostgreSQL transaction advisory lock so concurrent
  submissions cannot both acquire protection.

Do not add manual extension until stakeholders define the policy. The 90-day duration remains a
configurable-policy candidate.

## 13. Pipeline

Confirmed stages:
- Registered
- Qualified
- Discovery
- Demo
- POC
- Proposal
- Negotiation
- Won
- Lost

Confirmed:
- TCG Sales and Partner Sales can update stage.

Recommended:
- Won requires actual contract value + close date.
- Lost requires loss reason.

## 14. Products

Initial:
- mcube
- LVA

Actual SKU catalog will be configured later after development.

Implemented seed catalog:
- `MCUBE-LICENSE`
- `MCUBE-IMPLEMENTATION`
- `LVA-LICENSE`
- `LVA-IMPLEMENTATION`

List-price amounts are intentionally not seeded.

## 15. Currency

Confirmed:
- Transaction currency = USD.

Live market FX:
- may be used for informational local equivalent
- must not change official stored amounts

## 16. Commercial Models

Architectural decision:
Partner type, deal role, and commercial model are separate.

Partner Type:
- Reseller
- Referral
- System Integrator

Possible Deal Role:
- Reseller
- Referral
- System Integrator
- Co-Sell

Possible Commercial Model:
- Transfer Pricing
- Referral Commission
- SI Services
- Hybrid

## 17. Temporary Commercial Assumptions

Final Reseller and SI formulas will be configured later.

Development-only assumptions:
- Reseller = 20% discount from list price
- Referral = 1–5% of contract value
- Default referral = 3%
- SI = 15% markup on applicable service/base price

Do not treat these as final contractual terms.

## 18. Referral

Confirmed:
- 1–5%
- calculated on contract value

Store the rate/value used on the closed transaction so later configuration changes do not alter history.

## 19. Quote

Meaning:
- proposed commercial offer

Order cannot be created until customer accepts the quote.

Quote must preserve commercial snapshot.

Implemented:
- Quote requires an approved deal.
- SKU lines use effective resolved partner pricing at the time the line is added.
- Line-level pricing metadata is snapshotted.
- TCG finalization creates a numbered immutable quote revision.
- A final quote can be reopened for another revision without modifying the prior snapshot.
- The partner accepts the final quote before order creation.

## 20. Order

Confirmed:
- Order creation occurs after customer accepts quote.
- Customer commitment is signed contract or PO.
- Order is the confirmed transaction that TCG can fulfil.

Flow:
1. Deal approved
2. Quote finalized
3. Customer commits
4. Order submitted
5. TCG reviews
6. Return if correction needed
7. TCG confirms
8. Provisioning
9. Active

Recommended statuses:
- Draft
- Submitted
- Under Review
- Returned for Correction
- Confirmed
- Provisioning
- Active
- Cancelled

Deal model behavior:
- Reseller: reseller submits corresponding order to TCG.
- Referral: TCG creates order and referral partner stays linked.
- SI/joint: depends on customer contracting party.

Future:
- `ORDER_CONFIRMED` can automatically create an implementation project.

Implemented:
- One order per accepted quote.
- Order holds a complete quote snapshot and billing details.
- A `PURCHASE_ORDER`/signed commitment attachment is required before submission.
- Every order status transition is retained.
- Confirmation persists `ORDER_CONFIRMED` in `domain_events` in the same database transaction.
- External event publication and automatic project creation are future work.

## 21. MAF

Confirmed:
- MAF is required.
- MAF belongs in Phase 1.

Meaning:
- Manufacturer Authorization Form
- TCG authorizes partner for a named tender/RFP/customer/product context.

MAF is separate from:
- partner approval
- deal approval
- quote
- order

Recommended workflow:
- Draft
- Submitted
- Under Review
- Returned for Correction
- Approved
- Issued
- Rejected
- Expired

Recommended:
- related deal must be approved before MAF is issued.

Implemented:
- The deal must already be approved when the MAF request is created.
- TCG owns review, return, approval, rejection, issue, and expiry actions.
- Return/rejection requires a reason.
- An `ISSUED_DOCUMENT` attachment is required before issue.
- Issuance currently records expiry at 90 days.

## 22. Content Repository

Use:
- MinIO for binary files
- PostgreSQL for metadata

Recommended categories:
- Sales Enablement
- Product Documentation
- Implementation Guide
- Pricing
- Proposal Template
- SOW Template
- RFP
- Other

Implemented repository decisions:
- MinIO bucket is private.
- PostgreSQL stores document metadata and every version.
- Visibility scopes are All Partners, Partner Type, Partner Tier, Specific Partner, and TCG
  Internal.
- Access is enforced using the authenticated user's partner/type/tier context.
- Protected downloads use presigned URLs valid for ten minutes.
- SHA-256 checksum and file metadata are retained per version.
- Phase 1 upload limit is 25 MB.

## 23. Pricing Resolution

Recommended:
1. Product list price
2. Partner type rule
3. Tier adjustment
4. Partner-specific override
5. Final price

Keep all uncertain values configurable.

## 24. Important Deferred Items

Not blockers:
- final SKU list
- final actual prices
- final reseller formula
- final SI formula
- final tier adjustment %
- final quote approval thresholds
- final MAF template/signatory/validity details

## 25. Source-of-Truth Rule

Use this priority when requirements disagree:

1. Latest stakeholder clarification
2. Confirmed product decision
3. Original PPT
4. Temporary development assumption

Do not silently treat temporary assumptions as stakeholder-approved facts.

## 26. As-Built Phase 1 Workflow Decisions

- UI term is **Deal**; database/domain entity is `Opportunity`.
- Customer/product conflict identity uses foreign keys, not free-text matching.
- Deal approval statuses are Draft, Submitted, Under Review, Approved, and Rejected.
- Pipeline stages are Registered, Qualified, Discovery, Demo, POC, Proposal, Negotiation, Won,
  and Lost.
- Won requires actual value and actual close date. Lost requires a reason.
- Won and Lost cannot transition to another stage.
- Quote statuses are Draft, Under Review, Final, Accepted, Expired, and Cancelled.
- MAF statuses are Draft, Submitted, Under Review, Returned for Correction, Approved, Issued,
  Rejected, and Expired.
- Order statuses are Draft, Submitted, Under Review, Returned for Correction, Confirmed,
  Provisioning, Active, and Cancelled.
- Official and snapshotted commercial values remain USD.
- Partner-owned deals, quotes, MAF requests, orders, attachments, and scoped documents are
  authorized by the API; client-side filtering is never sufficient.

## 27. Schema and Seed State

Migration chain:
- `20260922_0001`: foundation identity, roles/permissions, audit, pgvector, seed tracking
- `20260923_0002`: partner types, tiers, countries, partners, partner users
- `20260923_0003`: products, SKUs, effective prices, commercial terms, tier adjustments, overrides
- `20260923_0004`: documents, customers, opportunities, stage history, attachments, quotes,
  revisions, MAF requests, orders, order history, domain events

Idempotent seed keys:
- `foundation-identity-v1`
- `phase-1a-partner-master-data-v1`
- `phase-1b-product-pricing-v1`
- `phase-1-remaining-permissions-v1`
- `phase-1-mcube-display-name-v1`

## 28. Current User Experience

Authenticated navigation includes:
- Overview
- Partner/company profile and users
- Products & SKUs
- Pricing
- Documents
- Deals & pipeline
- Quote to order, with Quotes, MAF, and Orders workspaces
- System status

The API is documented through FastAPI OpenAPI at `/docs`. Phase 1 currently exposes 50 API paths.

## 29. Verification Baseline

As of the last Phase 1 implementation pass:
- 24 backend tests pass.
- Ruff passes.
- Mypy strict mode passes.
- ESLint passes.
- TypeScript project checking passes.
- The Vite production build passes.
- Alembic renders the full migration chain through `20260923_0004` in offline SQL mode.

These checks do not replace the environment-owner live migration and end-to-end smoke test.

## 30. Operating Constraints for Continued Work

- Do not run live migrations, seeds, or MinIO mutations before the environment owner confirms the
  target `.env` and explicitly performs or requests the operation.
- Do not seed authoritative SKU prices until stakeholder-approved values exist.
- Preserve quote and order snapshots; never recalculate historical accepted values from current
  pricing configuration.
- Persist future fulfilment integration from `ORDER_CONFIRMED`; do not couple Phase 1 order
  confirmation directly to a not-yet-built project module.

## 31. Known Acceptance Gaps

Keep these visible in future planning:
- Rejected deal resubmission exists, but a deal update/edit endpoint and UI are still needed before
  the “edit and resubmit” requirement is fully accepted.
- Customer capture and authorized listing exist; customer editing, merging, and deduplication do
  not.
- Document APIs support every visibility scope and new versions. The current publisher UI only
  exposes All Partners and TCG Internal, and does not yet provide version-management controls.
- Protected attachment APIs exist for deals, MAF requests, and orders, but their full list/download
  experience is not complete in every workspace screen.
- MAF and quote expiry are metadata/workflow states, not scheduled background jobs.
- Quote approval thresholds are awaiting stakeholder rules.
- `ORDER_CONFIRMED` is stored durably but not externally published.

# Partner Portal — Architecture

## 1. Development Architecture

Phase 1 is designed for local development first.

### Technology Stack
- **Frontend:** React + TypeScript + Vite
- **Backend:** Python + FastAPI
- **ORM:** SQLAlchemy 2.x
- **Validation:** Pydantic
- **Migrations:** Alembic
- **Database:** PostgreSQL
- **Vector extension:** pgvector
- **Object storage:** MinIO AIStor
- **Local infrastructure:** existing PostgreSQL and MinIO containers managed outside this repository
- **Development environment:** VS Code

Deployment architecture is intentionally out of scope for now.

## 2. High-Level Architecture

```text
React Frontend
      |
      | REST
      v
FastAPI Backend
      |
      +------------------+
      |                  |
      v                  v
PostgreSQL           MinIO AIStor
+ pgvector           Object Storage
```

## 3. Frontend Responsibilities

React owns:
- Navigation
- Forms
- Tables
- Search/filter UI
- Role-aware menus
- Client-side validation
- API calls
- File upload/download UX
- Deal pipeline views
- Pricing views
- Quote/order screens
- MAF request screens

Recommended libraries:
- React Router
- TanStack Query
- React Hook Form
- Zod or equivalent validation
- A component library selected by the team

## 4. Backend Responsibilities

FastAPI owns:
- Authentication/session handling
- Authorization
- Partner isolation
- Business workflows
- Pricing rules
- Deal conflict checks
- Deal protection
- Quote snapshots
- MAF workflow
- Order workflow
- MinIO access
- Audit logging
- Database transactions
- API validation

## 5. Suggested Backend Structure

```text
backend/
  app/
    main.py
    api/v1/
    core/
    db/
    models/
    schemas/
    repositories/
    services/
    domain/
    integrations/
    storage/
    tests/
```

## 6. Suggested Frontend Structure

```text
frontend/
  src/
    app/
    routes/
    pages/
    components/
    features/
      auth/
      partners/
      users/
      customers/
      pricing/
      deals/
      quotes/
      maf/
      orders/
      documents/
    api/
    hooks/
    types/
    utils/
```

## 7. Core Domain Entities

### Identity & Access
- users
- roles
- permissions
- user_roles

### Partner
- partners
- partner_types
- partner_tiers
- partner_countries

### Customer
- customers

### Product & Pricing
- products
- skus
- product_prices
- partner_commercial_terms
- partner_price_overrides

### Deal
- opportunities
- opportunity_stage_history
- opportunity_attachments

### Quote
- quotes
- quote_items
- quote_revisions

### MAF
- maf_requests
- maf_documents

### Order
- orders
- order_items
- order_attachments

### Content
- documents
- document_versions
- document_access_rules

### Platform
- notifications
- audit_logs

## 8. Partner Isolation

All partner-owned business records should carry a `partner_id` where appropriate.

Backend authorization must ensure:
- Partner users only access their own partner's data.
- TCG users can access cross-partner data based on role.
- Pricing remains restricted.
- Documents obey access scope rules.

Authorization must be enforced in the backend, not only hidden in the React UI.

## 9. Identity & Authorization

Recommended roles:

### TCG
- `TCG_ADMIN`
- `TCG_SALES`

### Partner
- `PARTNER_ADMIN`
- `PARTNER_SALES`
- `PARTNER_PRESALES`
- `PARTNER_DELIVERY`

Use permissions behind roles so access rules can evolve without redesign.

## 10. Customer Master and Conflict Checking

Deals reference a canonical customer record.

Conflict lookup uses:
- `customer_id`
- `product_id`
- active deal protection

This avoids unreliable free-text-only comparisons.

## 11. Pricing Architecture

Authoritative currency is USD.

```text
Product List Price
      ↓
Partner Type Rule
      ↓
Tier Adjustment
      ↓
Partner Override
      ↓
Final Partner Price
```

Commercial settings must be data/configuration, not hardcoded.

## 12. Live FX

Live FX is informational only.

Use an abstraction:

```text
FXRateProvider
  get_rate(from_currency, to_currency)
```

Do not scatter provider-specific calls across the application.

## 13. MinIO Architecture

Use MinIO for file binaries.

PostgreSQL stores:
- filename
- document type
- category
- MinIO object key
- MIME type
- size
- checksum
- owner
- visibility
- version
- created/updated timestamps

Suggested object structure:

```text
partner-portal/
  documents/
  partners/{partner_id}/
  deals/{deal_id}/
  quotes/{quote_id}/
  maf/{maf_request_id}/
  orders/{order_id}/
```

Prefer private objects with backend-generated presigned upload/download URLs.

## 14. Quote Snapshot Strategy

Once quote is finalized:
- Persist quote item prices.
- Persist discounts.
- Persist commercial rule values used.
- Persist currency.
- Persist totals.

Do not recalculate historical finalized quotes from current price master.

## 15. Order Snapshot Strategy

Order references accepted quote but preserves its own commercial snapshot.

Store:
- accepted quote ID
- accepted quote revision
- line prices
- totals
- commercial model
- applicable commission/transfer values

## 16. Referral Snapshot Strategy

On deal/order closure, persist:
- contract value
- referral rate used
- referral amount

Do not recalculate historical commission if partner terms change later.

## 17. Pipeline History

Persist:
- from_stage
- to_stage
- changed_by
- changed_at
- comment

Current stage also remains on `opportunities` for fast reads.

## 18. Domain Events

Introduce lightweight internal events:
- `PARTNER_APPROVED`
- `DEAL_APPROVED`
- `DEAL_REJECTED`
- `DEAL_WON`
- `QUOTE_FINALIZED`
- `MAF_ISSUED`
- `ORDER_CONFIRMED`

Initially these can be handled synchronously in-process.

## 19. Audit Logging

Audit high-value actions:
- partner creation/approval/rejection
- role changes
- pricing changes
- deal approval/rejection
- deal stage changes
- quote finalization
- MAF approval/issue
- order review/confirmation
- document publication/access if required

Recommended audit fields:
- actor_user_id
- actor_role
- action
- entity_type
- entity_id
- old_values
- new_values
- timestamp
- correlation/request ID

## 20. API Conventions

Recommended:
- REST
- `/api/v1/...`
- UUID identifiers
- UTC timestamps
- ISO-8601 dates
- pagination
- consistent error envelope
- OpenAPI/Swagger from FastAPI

## 21. pgvector

Enable pgvector from the beginning, but do not make Phase 1 dependent on vector search.

Future uses:
- semantic document search
- RAG
- similar opportunity search

## 22. Local Service Setup

Required services:
- A running PostgreSQL container with the configured database already created
- A running MinIO container with the configured private bucket already created

The repository does not contain Dockerfiles or Docker Compose configuration. Confirm the
containers and their port mappings with the local container runtime, then run the frontend and
backend directly from the repository workspace.

## 23. Security Baseline

- Password hashing
- Backend-enforced RBAC
- Partner data isolation
- Secure token/session handling
- Input validation
- File type validation
- Private MinIO buckets
- Audit logs
- No secrets committed to repository

## 24. Future Expansion

Architecture should allow later modules:
- Project/implementation tracking
- Support/SLA
- License tracking
- Renewals
- Certification
- QBR
- Health score
- AI/RAG
- ERP/CRM integrations

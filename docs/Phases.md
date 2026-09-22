# Partner Portal — Delivery Phases

## Phase 0 — Foundation

### Deliverables
- React + TypeScript + Vite frontend
- FastAPI backend
- PostgreSQL + pgvector
- MinIO AIStor
- Connection to existing PostgreSQL and MinIO containers
- Environment configuration
- Alembic migrations
- Base API structure
- Authentication foundation
- Error handling
- Logging
- Audit framework
- Seed/master-data framework

### Exit Criteria
- Frontend can call backend
- Backend can access PostgreSQL
- Backend can access MinIO
- Migrations run successfully
- Local developer setup documented

## Phase 1A — Partner Access & Management

### Features
- TCG Admin login
- Partner self-registration
- TCG partner creation
- Partner approval/rejection
- Partner profile
- Partner types
- Partner tiers
- Country/territory
- Partner users
- Role-based access
- Partner data isolation

## Phase 1B — Product & Pricing

### Features
- Product master
- SKU master
- Product price configuration
- Partner commercial terms
- Tier adjustment configuration
- Partner-specific override
- USD pricing
- Optional live FX display

### Initial Products
- mcube
- LVA

### Temporary Development Defaults
- Reseller: 20% discount
- Referral: 3%, configurable 1–5%
- SI: 15% markup
- Silver: 0%
- Gold: 5%
- Platinum: 10%

## Phase 1C — Content Repository

### Features
- Document upload
- MinIO storage
- Metadata in PostgreSQL
- Categories
- Versioning
- Access scopes
- Protected download
- Metadata search/filter

## Phase 1D — Customer & Deal Registration

### Features
- Customer master
- Deal creation
- Deal submission
- Admin approval/rejection
- Rejection reason
- Resubmission
- Customer+product conflict check
- Deal protection
- Attachments

## Phase 1E — Pipeline

### Features
- Pipeline stages
- Stage updates by Partner Sales and TCG Sales
- Stage history
- Won validation
- Lost validation
- Basic deal dashboard/filtering

## Phase 1F — Quote

### Features
- Quote creation from deal
- Quote items
- Product/SKU pricing
- Discount application
- Commercial model
- Revision/version
- Finalization
- Price snapshot

## Phase 1G — MAF

### Features
- MAF request creation
- Link to approved deal
- Tender/RFP details
- Supporting file upload
- Admin review
- Return for correction
- Approval
- Issued MAF document upload/generation
- Download
- Expiry metadata

## Phase 1H — Order

### Features
- Create order from accepted quote
- PO/signed contract attachment
- Billing details
- Order review
- Return for correction
- Confirm
- Provision
- Activate
- Order status history
- Domain event `ORDER_CONFIRMED`

# Future Phase 2 — Implementation & Delivery

Potential scope:
- Automatic project creation on `ORDER_CONFIRMED`
- Project milestones
- Requirement gathering
- Infrastructure readiness
- Installation/configuration
- Testing
- UAT
- Go-live
- Handover

# Future Phase 3 — Support & Subscription

Potential scope:
- Support tickets
- SLA tracking
- L1/L2/L3 escalation
- Knowledge base
- Subscription/license visibility
- Renewal alerts
- Expansion opportunities

# Future Phase 4 — Enablement & Governance

Potential scope:
- Training
- Certification
- Partner health score
- QBR
- Monthly reporting
- Advanced analytics
- Joint business plans

# Future Phase 5 — AI / Advanced Search

Potential scope:
- Document text extraction
- Embeddings
- pgvector
- Semantic search
- RAG assistant
- Similar-deal discovery

## Recommended Execution Order

1. Foundation
2. Access & Partner Management
3. Product & Pricing
4. Content Repository
5. Customer & Deal
6. Pipeline
7. Quote
8. MAF
9. Order

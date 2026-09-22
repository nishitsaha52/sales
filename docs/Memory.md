# Partner Portal — Project Memory / Decision Log

This file captures the current agreed understanding so future development discussions do not reopen already-settled decisions unnecessarily.

## 1. Product Context

- TCG Digital supplies mCube and LVA.
- Partners help TCG find customers, sell products, or implement them.
- The Partner Portal is the shared digital workspace between TCG and partner companies.

## 2. Local Development Stack

Confirmed:
- Frontend: React
- Recommended frontend setup: React + TypeScript + Vite
- Backend: Python
- Recommended backend framework: FastAPI
- Database: PostgreSQL
- Extension: pgvector
- Storage: MinIO AIStor
- Local infra: Docker / Docker Compose
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
- Lasts until deal closes.
- Deal closes on Won or Lost.

Do not implement extension unless a future expiry rule is introduced.

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
- mCube
- LVA

Actual SKU catalog will be configured later after development.

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
- `ORDER_CONFIRMED` can automatically create implementation project.

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

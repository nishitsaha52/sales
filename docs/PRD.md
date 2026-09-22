# Partner Portal — Product Requirements Document (PRD)

## 1. Product Summary

TCG Digital supplies products including **mCube** and **LVA**. The Partner Portal is a web application used by TCG Digital and approved partner companies to manage partner onboarding, pricing access, content, deal registration, quoting, MAF requests, and order tracking.

The product replaces fragmented offline work such as email, spreadsheets, manual approval chains, ad-hoc document sharing, and untracked deal claims with a controlled, auditable portal.

## 2. Phase 1 Scope

Phase 1 includes:

1. **Partner Access & Management**
   - Partner self-registration
   - Partner creation by TCG Admin
   - TCG approval/rejection of partner registrations
   - Partner profile management
   - Partner type
   - Partner tier
   - Territory/country
   - User and role management
   - Role-based access control

2. **Pricing & Quotes**
   - Product and SKU master
   - USD-based commercial pricing
   - Partner-type pricing rules
   - Tier-based pricing adjustments
   - Partner-specific overrides
   - Quote creation
   - Quote finalization / approval
   - Special discount handling

3. **Content Repository**
   - mCube / LVA documentation
   - Sales enablement kits
   - Product documentation
   - Implementation guides
   - Proposal templates
   - SOW templates
   - RFP material
   - Controlled document access
   - File storage in MinIO AIStor

4. **Deal Registration & Pipeline**
   - Deal registration
   - Admin approval / rejection
   - Duplicate/conflict detection
   - Deal protection
   - Pipeline stage tracking
   - Stage history
   - Won / lost tracking

5. **MAF**
   - Manufacturer Authorization Form request
   - Admin review
   - Return for correction
   - Approval
   - Issue / upload generated document
   - Download by authorized partner users

6. **Orders**
   - Order creation after quote acceptance
   - Accepted quote linkage
   - PO / signed contract attachment
   - TCG review
   - Return for correction
   - Confirmation
   - Provisioning status
   - Active status

## 3. Out of Scope for Phase 1

- Support ticketing
- SLA management
- Training/certification
- Implementation project management
- License/subscription renewal workflows
- QBR
- Partner health scoring
- Advanced analytics
- AI/RAG document assistant
- Automated tier promotion/demotion
- Billing/invoicing engine
- ERP integration

The architecture should leave room for these later.

## 4. Primary Actors

### TCG Users
- **TCG Admin**
- **TCG Sales**

### Partner Users
- **Partner Admin**
- **Partner Sales**
- **Partner Pre-Sales**
- **Partner Delivery**

## 5. Partner Model

### 5.1 Partner Types
- `RESELLER`
- `REFERRAL`
- `SYSTEM_INTEGRATOR`

### 5.2 Partner Tiers
- `SILVER`
- `GOLD`
- `PLATINUM`

Phase 1 uses manual tier assignment by TCG Admin.

Temporary development pricing assumptions:
- Silver: 0% additional tier adjustment
- Gold: 5% additional benefit
- Platinum: 10% additional benefit

These values must be configurable and treated as placeholders until finalized.

### 5.3 Territory
Territory refers to location/country.

Rules:
- Multiple partners may operate in the same country.
- Territory does not block deal registration.
- A partner may be associated with one or more countries.

## 6. Partner Onboarding

### 6.1 TCG-Created Partner
1. TCG Admin creates partner.
2. TCG Admin creates or invites Partner Admin.
3. Partner becomes active.

### 6.2 Self-Registration
1. Partner submits registration.
2. Status becomes `PENDING_APPROVAL`.
3. TCG Admin reviews.
4. Admin approves or rejects.
5. If approved, partner becomes `ACTIVE`.
6. If rejected, rejection reason is stored.

Partner statuses:
- `PENDING_APPROVAL`
- `ACTIVE`
- `REJECTED`
- `SUSPENDED`
- `INACTIVE`

## 7. Recommended Partner Profile Fields

### Company
- Company name *
- Legal name
- Partner type *
- Tier
- Country / countries *
- Website
- Company email *
- Phone
- Address

### Primary Contact
- Name *
- Email *
- Phone

### System / TCG-Controlled
- Partner code
- Status
- Approved by
- Approved at
- Created at
- Updated at

## 8. Deal Model

Phase 1 uses a single **Deal/Opportunity** entity.

- UI term: **Deal**
- Backend/domain term: **Opportunity**
- A separate Lead entity is not required initially.

## 9. Recommended Deal Registration Fields

### Customer
- Customer/account *
- Customer website/domain
- Country *
- Industry

### Opportunity
- Deal name *
- Product *
- Estimated contract value (USD)
- Expected close date *
- Requirement / description *

### Contact
- Customer contact name
- Designation
- Email
- Phone

### Commercial / Ownership
- Partner role on this deal *
- Commercial model *
- Partner Sales owner *
- TCG Sales owner
- Competitor
- Notes

### Attachments
- Supporting files

### System-Controlled
- Deal number
- Partner
- Approval status
- Pipeline stage
- Protection status
- Created/updated timestamps

## 10. Partner Type vs Deal Role vs Commercial Model

These are separate concepts.

### Partner Type
- Reseller
- Referral
- System Integrator

### Deal Role
- `RESELLER`
- `REFERRAL`
- `SYSTEM_INTEGRATOR`
- `COSELL`

### Commercial Model
- `TRANSFER_PRICING`
- `REFERRAL_COMMISSION`
- `SI_SERVICES`
- `HYBRID`

A System Integrator may act as a reseller on one deal and as a referral partner on another.

## 11. Deal Approval

Approval status:
- `DRAFT`
- `SUBMITTED`
- `UNDER_REVIEW`
- `APPROVED`
- `REJECTED`

Workflow:
1. Partner creates draft.
2. Partner submits.
3. TCG Admin reviews.
4. Admin approves or rejects.
5. Rejected deals can be edited and resubmitted.

Approved deals may be updated for operational fields such as expected close date, estimated value, notes, and customer contact. Changing customer/product should require Admin intervention or re-approval.

## 12. Duplicate / Conflict Rule

Conflict key:

> Same customer + same product + active protected deal = conflict

Examples:
- Acme Pharma + mCube by Partner A → approved/protected
- Acme Pharma + mCube by Partner B → blocked/conflict
- Acme Pharma + LVA by Partner B → allowed

Customer matching should use a Customer Master and `customer_id`, not only text matching.

## 13. Deal Protection

- Protection starts when Admin approves the deal.
- Protection remains active until the deal closes.
- Deal closes when it becomes `WON` or `LOST`.

Store:
- `protection_started_at`
- `protection_ended_at`

Time-based extension is not required unless a future expiry rule is introduced.

## 14. Pipeline Stages

1. `REGISTERED`
2. `QUALIFIED`
3. `DISCOVERY`
4. `DEMO`
5. `POC`
6. `PROPOSAL`
7. `NEGOTIATION`
8. `WON`
9. `LOST`

Both Partner Sales and TCG Sales may change stages. Every stage change must be recorded in stage history.

Recommended validations:
- `WON` requires actual contract value and close date.
- `LOST` requires loss reason.

## 15. Products

Initial products:
- `MCUBE`
- `LVA`

The data model must support later addition of SKUs.

Suggested development SKUs:
- `MCUBE-LICENSE`
- `MCUBE-IMPLEMENTATION`
- `LVA-LICENSE`
- `LVA-IMPLEMENTATION`

Actual catalog and pricing will be configured later.

## 16. Pricing

### 16.1 Official Currency
All authoritative commercial values are stored and calculated in **USD**.

### 16.2 Live FX
Live FX may be used only for optional informational local-currency display. FX movement must not change accepted/stored commercial values.

### 16.3 Pricing Precedence
1. Product list price
2. Partner type rule
3. Partner tier adjustment
4. Partner-specific override
5. Final partner price

### 16.4 Temporary Development Defaults
- Reseller: 20% discount from list price
- Referral: default 3%, configurable 1–5%, applied on contract value
- System Integrator: 15% markup on applicable service price
- Silver tier: 0%
- Gold tier: 5%
- Platinum tier: 10%

These are placeholders only.

## 17. Quotes

A quote represents the proposed commercial offer before customer commitment.

Quote should capture:
- Customer
- Deal
- Product/SKU lines
- Quantity
- Subscription term
- Implementation work
- List price
- Discount
- Final price
- Currency = USD
- Validity period
- Commercial model
- Version/revision
- Approval/finalization state

Accepted quote values must be snapshotted and preserved historically.

## 18. MAF

MAF = Manufacturer Authorization Form.

Phase 1 includes MAF.

Purpose:
- Authorize a named partner to offer TCG product(s) for a specific tender / RFP / bid.

### MAF Workflow
- `DRAFT`
- `SUBMITTED`
- `UNDER_REVIEW`
- `RETURNED_FOR_CORRECTION`
- `APPROVED`
- `ISSUED`
- `REJECTED`
- `EXPIRED`

### Recommended MAF Fields
- Request number
- Partner *
- Related deal *
- Customer *
- Product(s) *
- Tender/RFP name *
- Tender/RFP number
- Issuing organization
- Submission deadline *
- Authorization purpose
- Requested validity date
- Partner legal name/address
- Supporting tender/RFP document
- Additional attachments
- Review / approval metadata
- Issued MAF document
- Issue date
- Expiry date

Recommended eligibility:
- Partner must be active.
- Deal should be approved before MAF is issued.

MAF does not itself create a deal, quote, or order.

## 19. Order

An order is created after the customer accepts the quote.

Meaning:
- Deal = pursuing the customer
- Quote = proposed price/terms
- Order = customer committed and fulfilment can begin

### Order Flow
1. Deal approved.
2. Quote finalized.
3. Customer signs contract or provides PO.
4. Order is submitted with PO/signed agreement.
5. TCG reviews commercial and billing details.
6. If incorrect, order is returned for correction.
7. If accepted, TCG confirms the order and assigns order number.
8. Order moves into provisioning.
9. Order becomes active.

### Order Statuses
- `DRAFT`
- `SUBMITTED`
- `UNDER_REVIEW`
- `RETURNED_FOR_CORRECTION`
- `CONFIRMED`
- `PROVISIONING`
- `ACTIVE`
- `CANCELLED`

### Who Submits
- Reseller: Partner submits order to TCG.
- Referral: TCG submits/creates order; referral partner remains linked.
- SI/Joint: Based on the customer contracting party.

### Recommended Order Fields
- Order number
- Related deal *
- Related accepted quote *
- Partner *
- Customer *
- Products/SKUs *
- Commercial model *
- Customer contracting party *
- PO number/date
- PO or signed agreement attachment *
- Contract value USD *
- Approved transfer price
- Referral rate/amount if applicable
- Billing name/address/contact/email
- Subscription start date
- Subscription term
- Requested fulfilment date
- Implementation required flag
- SOW reference
- Status
- Submitted/reviewed/confirmed metadata
- Return reason
- Notes

### Submission Validations
- Deal must be approved.
- Deal must not be lost.
- Quote must be final/approved.
- Commitment document must exist.
- Pricing differences from quote must be flagged for review.

### Confirmation Event
On `CONFIRMED`, emit domain event:
- `ORDER_CONFIRMED`

Future phases may use this event to create an implementation project automatically.

## 20. Content Repository

Recommended categories:
- Sales Enablement
- Product Documentation
- Implementation Guide
- Pricing
- Proposal Template
- SOW Template
- RFP
- Other

PostgreSQL stores metadata. MinIO AIStor stores binary files.

Recommended visibility scopes:
- `ALL_PARTNERS`
- `PARTNER_TYPE`
- `PARTNER_TIER`
- `SPECIFIC_PARTNER`
- `TCG_INTERNAL`

## 21. Phase 1 Success Criteria

Phase 1 is successful when:
- A partner can register and be approved.
- A TCG Admin can create partners manually.
- Partner users see only authorized partner data.
- Pricing can be configured and displayed per partner.
- Users can access controlled documents.
- A partner can register a deal.
- Admin can approve/reject a deal.
- Duplicate/protected conflicts are enforced.
- Partner and TCG Sales can move deals through the pipeline.
- Partner can request MAF and receive issued document.
- Quote can be finalized and linked to an order.
- Accepted order can be submitted, reviewed, corrected, confirmed, provisioned, and activated.
- Important actions are auditable.

## 22. Remaining Configuration Items

Not blockers for development:
- Final mCube/LVA SKU catalog
- Actual SKU prices
- Final Reseller formula
- Final SI formula
- Final Silver/Gold/Platinum pricing adjustments
- Final MAF document template/signatory/validity rules
- Final quote approval thresholds

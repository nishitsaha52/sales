# Partner Portal — UX / Functional Design

## 1. Design Principles

- Keep partner workflows simple and guided.
- Clearly separate TCG actions from Partner actions.
- Never expose cross-partner confidential data.
- Make status and next action obvious.
- Avoid overwhelming users with future-phase functionality.
- Use tables for operational lists and step/status components for workflows.
- Use role-based navigation.
- Show commercial values in USD.
- Live FX, if shown, must be labeled approximate/informational.

## 2. Primary Navigation

### Partner User
- Dashboard
- Deals
  - My Deals
  - Register Deal
- Pricing
- Quotes
- MAF Requests
- Orders
- Documents
- Profile

### Partner Admin
All Partner User items plus:
- Company Profile
- Users

### TCG Admin
- Dashboard
- Partners
  - Pending Registrations
  - Active Partners
- Users
- Customers
- Deals
  - Pending Approval
  - All Deals
- Products & SKUs
- Pricing
- Quotes
- MAF Requests
- Orders
- Documents
- Administration

### TCG Sales
- Dashboard
- Customers
- Deals
- Quotes
- Orders
- Pricing (view)
- Documents

## 3. Dashboard Design

### Partner Dashboard
Suggested cards:
- Open Deals
- Deals Awaiting TCG Approval
- Quotes in Progress
- MAF Requests in Review
- Orders in Progress

Suggested lists:
- Recent Deals
- Recent Documents
- Pending Actions

### TCG Admin Dashboard
Suggested cards:
- Pending Partner Registrations
- Deals Awaiting Approval
- MAF Requests Awaiting Review
- Orders Under Review
- Active Partners

## 4. Partner Registration

### Self-Registration Screen
Sections:
1. Company
2. Primary Contact
3. Partner Type
4. Territory
5. Account Credentials
6. Review & Submit

After submission:
- show Pending Approval
- display request reference
- explain that TCG will review

### Admin Review Screen
Show:
- company details
- contact
- requested partner type
- country
- submitted date
- approve/reject actions

Reject requires reason.

## 5. Partner Details

Tabs:
- Overview
- Users
- Commercial Terms
- Documents
- Activity

Overview:
- Partner code
- Status
- Type
- Tier
- Countries
- Primary contact

Commercial Terms:
- Product
- Commercial model
- Tier
- Partner override
- Effective dates

## 6. Deal Registration

Use a multi-section form.

### Customer
- Customer selector
- Create new customer
- Country
- Industry
- Website

### Deal
- Deal name
- Product
- Estimated contract value USD
- Expected close date
- Description

### Role & Commercial
- Partner role on this deal
- Commercial model
- Partner Sales owner
- TCG Sales owner if known

### Contact
- Name
- Designation
- Email
- Phone

### Attachments
- Upload files

Before submit:
- run conflict check
- block if active protected conflict exists
- otherwise submit for review

## 7. Deal Detail

Header:
- Deal number
- Customer
- Product
- Partner
- Approval status
- Pipeline stage
- Protection status

Tabs:
- Overview
- Commercial
- Activity
- Files
- Quotes
- MAF
- Orders

## 8. Pipeline

```text
Registered → Qualified → Discovery → Demo → POC → Proposal → Negotiation → Won/Lost
```

Stage update dialog:
- new stage
- comment
- required fields based on stage

For Won:
- Actual contract value
- Close date

For Lost:
- Loss reason
- Optional notes

## 9. Pricing Screen

Partner view:
- Product/SKU
- Description
- Your Price (USD)
- Effective From
- Effective Until

Do not show internal formulas unless explicitly allowed.

Optional:
- Approx local equivalent using live FX

TCG Admin view:
- List price
- Partner type rule
- Tier adjustment
- Partner override
- Final result

## 10. Quote Design

Quote builder:
- Related deal
- Customer
- Product/SKU lines
- Quantity
- Term
- List price
- Discount
- Final unit price
- Line total
- Implementation/service lines
- Quote total
- Validity
- Notes

Suggested statuses:
- Draft
- Under Review
- Final
- Accepted
- Expired
- Cancelled

Keep revision history.

## 11. MAF Design

### Partner Request Screen
- Related deal
- Customer
- Product(s)
- Tender/RFP name
- Tender number
- Issuing organization
- Deadline
- Authorization purpose
- Requested validity
- Supporting document
- Notes

### Status Timeline
- Draft
- Submitted
- Under Review
- Returned
- Approved
- Issued

### Admin Review
Show:
- Partner status/type/tier
- Related approved deal
- Tender details
- Supporting docs

Actions:
- Return for correction
- Reject
- Approve
- Upload/issue MAF

## 12. Order Design

### Create Order
Start from accepted quote.

Pre-fill:
- Partner
- Customer
- Deal
- Quote
- Product lines
- Commercial values

Additional inputs:
- PO number
- PO date
- PO/signed agreement
- Billing details
- Subscription term/start date
- Requested fulfilment date
- Implementation required
- SOW reference

### Status Timeline
- Draft
- Submitted
- Under Review
- Returned for Correction
- Confirmed
- Provisioning
- Active

### Review Screen
TCG compares:
- quote total
- order total
- discount
- line items
- PO details
- billing details
- scope

Highlight variance.

## 13. Documents

### Repository List
Filters:
- Product
- Category
- Audience
- Version
- Date

Fields:
- Name
- Product
- Category
- Version
- Published date
- Download

### Admin Upload
- Name
- Product
- Category
- Description
- Version
- Visibility
- File
- Effective dates

## 14. Tables

Operational tables should support:
- Search
- Pagination
- Sorting
- Status filters
- Partner filter for TCG
- Product filter
- Date filters

## 15. Error UX

Business-rule errors should be specific.

Example:
> An active protected deal already exists for this customer and product.

## 16. Responsive Design

Desktop-first is acceptable for Phase 1, but forms and critical workflows should remain usable on tablet/laptop widths.

## 17. Accessibility

Baseline:
- keyboard navigation
- proper form labels
- visible focus states
- semantic tables
- status text, not color alone
- sufficient contrast

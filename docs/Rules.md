# Partner Portal — Business Rules

## 1. Rule Priority

Use this source priority:

1. Confirmed stakeholder clarification
2. Confirmed Phase 1 product decision
3. PPT requirement
4. Temporary developer assumption

Temporary assumptions must be configurable.

## 2. Partner Rules

- **R-PARTNER-001:** Partner types are Reseller, Referral, System Integrator.
- **R-PARTNER-002:** Partner tiers are Silver, Gold, Platinum.
- **R-PARTNER-003:** Tier is separate from partner type.
- **R-PARTNER-004:** Tier is manually assigned by TCG Admin in Phase 1.
- **R-PARTNER-005:** Territory means country/location.
- **R-PARTNER-006:** Multiple partners may operate in the same territory.
- **R-PARTNER-007:** Territory does not block deal registration.
- **R-PARTNER-008:** TCG Admin may create partners manually.
- **R-PARTNER-009:** Partners may self-register.
- **R-PARTNER-010:** Self-registered partners require TCG Admin approval.
- **R-PARTNER-011:** Rejected partner registration must store a rejection reason.

## 3. Access Rules

- **R-ACCESS-001:** Partner users may access only data authorized for their partner.
- **R-ACCESS-002:** Restricted pricing must not be visible to unauthorized roles.
- **R-ACCESS-003:** Authorization must be enforced by backend APIs.
- **R-ACCESS-004:** Suggested TCG roles: TCG Admin, TCG Sales.
- **R-ACCESS-005:** Suggested partner roles: Partner Admin, Partner Sales, Partner Pre-Sales, Partner Delivery.

## 4. Deal Rules

- **R-DEAL-001:** Phase 1 uses one Deal/Opportunity entity.
- **R-DEAL-002:** A separate Lead entity is not required initially.
- **R-DEAL-003:** Approval statuses: Draft, Submitted, Under Review, Approved, Rejected.
- **R-DEAL-004:** Rejected deals may be edited and resubmitted.
- **R-DEAL-005:** TCG Admin approves or rejects deals.
- **R-DEAL-006:** Operational fields of an approved deal may be updated.
- **R-DEAL-007:** Changing customer or product on an approved/protected deal should require Admin intervention or re-approval.

## 5. Deal Conflict Rules

- **R-CONFLICT-001:** Same customer + same product + another active protected deal = conflict.
- **R-CONFLICT-002:** Same customer with a different product is allowed.
- **R-CONFLICT-003:** Use canonical customer records and IDs for conflict checking.

## 6. Deal Protection Rules

- **R-PROTECT-001:** Protection starts when the deal is approved.
- **R-PROTECT-002:** Protection remains active until the deal is closed.
- **R-PROTECT-003:** Closed means Won or Lost.
- **R-PROTECT-004:** Protection extension is not required unless a future expiry period is introduced.

## 7. Pipeline Rules

- **R-PIPE-001:** Stages: Registered, Qualified, Discovery, Demo, POC, Proposal, Negotiation, Won, Lost.
- **R-PIPE-002:** Partner Sales and TCG Sales may change stage.
- **R-PIPE-003:** Every stage change must be retained in history.
- **R-PIPE-004:** Won requires actual contract value and close date.
- **R-PIPE-005:** Lost requires loss reason.

## 8. Partner Role / Commercial Model Rules

- **R-COMM-001:** Partner type and deal role are separate concepts.
- **R-COMM-002:** Suggested deal roles: Reseller, Referral, System Integrator, Co-Sell.
- **R-COMM-003:** Commercial model is deal-specific.
- **R-COMM-004:** Suggested commercial models: Transfer Pricing, Referral Commission, SI Services, Hybrid.
- **R-COMM-005:** A partner may use a different commercial role on different deals.

## 9. Product Rules

- **R-PRODUCT-001:** Initial products are mCube and LVA.
- **R-PRODUCT-002:** Products must not be hardcoded as columns in partner/deal tables.
- **R-PRODUCT-003:** System must support future SKU expansion.

## 10. Currency & Pricing Rules

- **R-PRICE-001:** Authoritative transaction currency is USD.
- **R-PRICE-002:** All final commercial amounts are stored in USD.
- **R-PRICE-003:** Live FX is informational only.
- **R-PRICE-004:** FX changes must not alter accepted quotes or confirmed orders.
- **R-PRICE-005:** Pricing precedence: Product list price → Partner type rule → Tier adjustment → Partner-specific override → Final price.
- **R-PRICE-006:** Final reseller and SI formulas are configurable and not yet final.
- **R-PRICE-007:** Temporary reseller development rule: 20% discount from list price.
- **R-PRICE-008:** Referral commission is configurable from 1% to 5% and calculated on contract value.
- **R-PRICE-009:** Temporary default referral rate is 3%.
- **R-PRICE-010:** Temporary SI development rule: 15% markup on applicable service/base price.
- **R-PRICE-011:** Temporary tier adjustments: Silver 0%, Gold 5%, Platinum 10%.

## 11. Quote Rules

- **R-QUOTE-001:** Quote represents proposed commercial offer.
- **R-QUOTE-002:** Finalized quote must preserve a price snapshot.
- **R-QUOTE-003:** Accepted quote is required before order creation.
- **R-QUOTE-004:** Quote may contain products, quantities, subscription term, implementation scope, discounts and final price.

## 12. MAF Rules

- **R-MAF-001:** MAF is in Phase 1.
- **R-MAF-002:** MAF is separate from partner approval, deal approval, quote and order.
- **R-MAF-003:** MAF links to partner, deal, customer, product and tender/RFP context.
- **R-MAF-004:** Workflow: Draft, Submitted, Under Review, Returned for Correction, Approved, Issued, Rejected, Expired.
- **R-MAF-005:** Partner must be active to request MAF.
- **R-MAF-006:** MAF should not be issued unless related deal is approved.

## 13. Order Rules

- **R-ORDER-001:** Order creation occurs after the customer accepts the quote.
- **R-ORDER-002:** Customer commitment is evidenced by PO or signed agreement.
- **R-ORDER-003:** Order links to accepted quote.
- **R-ORDER-004:** Statuses: Draft, Submitted, Under Review, Returned for Correction, Confirmed, Provisioning, Active, Cancelled.
- **R-ORDER-005:** TCG verifies approved price, contract/PO, billing details and scope.
- **R-ORDER-006:** If order differs from accepted quote, it must be returned or flagged for review.
- **R-ORDER-007:** TCG assigns/confirms order number when confirmed.
- **R-ORDER-008:** Reseller flow: reseller submits corresponding order to TCG.
- **R-ORDER-009:** Referral flow: TCG creates/submits order and referral partner stays linked.
- **R-ORDER-010:** SI/joint flow depends on customer contracting party.
- **R-ORDER-011:** Confirmed order emits `ORDER_CONFIRMED`.
- **R-ORDER-012:** Future project creation should subscribe to `ORDER_CONFIRMED`.

## 14. Content Rules

- **R-DOC-001:** Binary files are stored in MinIO.
- **R-DOC-002:** Document metadata is stored in PostgreSQL.
- **R-DOC-003:** Categories: Sales Enablement, Product Documentation, Implementation Guide, Pricing, Proposal Template, SOW Template, RFP, Other.
- **R-DOC-004:** Visibility: All Partners, Partner Type, Partner Tier, Specific Partner, TCG Internal.

## 15. Historical Data Rules

- **R-HISTORY-001:** Historical finalized quotes must not be recalculated from current pricing.
- **R-HISTORY-002:** Referral commission rate used at closure must be stored.
- **R-HISTORY-003:** Price/discount values used at quote/order time must be snapshotted.
- **R-HISTORY-004:** Deal stage history must be retained.

## 16. Audit Rules

Audit at minimum:
- partner approval/rejection
- role changes
- pricing changes
- deal approval/rejection
- deal stage changes
- quote finalization
- MAF approval/issue
- order confirmation

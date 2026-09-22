# Phase 1B — Product & Pricing

## Delivered scope

- Product and SKU master data with active/inactive lifecycle
- Suggested mCube and LVA development SKUs
- Effective-dated USD list prices
- Effective-dated partner-type commercial rules
- Effective-dated tier discount/benefit configuration
- Effective-dated partner-specific SKU overrides
- Role-aware resolved pricing for TCG and partner users
- Admin-only calculation breakdown and configuration screens
- Audit events for catalog and pricing changes

Actual prices are intentionally not seeded because stakeholder-approved values are still pending.
TCG Admin must configure a USD list price before a SKU appears in resolved partner pricing.

## Resolution order

For a requested effective date, the backend resolves:

1. The most recent active SKU list price in USD.
2. The active partner-type rule.
3. The active tier benefit.
4. The active partner/SKU override.
5. The final price, rounded to two decimal places using half-up rounding.

Percentage partner overrides apply to the amount after the partner-type and tier steps. A fixed
override replaces that amount. Referral commission is returned as commercial metadata and does
not reduce the SKU price; its eventual value is calculated on contract value in the deal/order
flow.

Overlapping effective records are resolved deterministically by the latest `effective_from` date.
Historical quote and order prices will be snapshotted in their respective phases and will not be
recalculated from this live configuration.

## Temporary configurable defaults

The idempotent Phase 1B seed creates these explicitly provisional rules:

- Reseller: 20% discount
- Referral: 3% commission
- System Integrator: 15% markup
- Silver: 0% benefit
- Gold: 5% benefit
- Platinum: 10% benefit

They remain database configuration, not application constants.

## Apply locally

Stop the backend and run:

```powershell
Set-Location C:\Users\nishi\Desktop\sales\backend
python -m alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload
```

The migration is `20260923_0003` and the seed is `phase-1b-product-pricing-v1`.

## Acceptance smoke test

1. Sign in as TCG Admin and open **Products & SKUs**.
2. Configure a USD list price for at least one seeded SKU.
3. Open **Pricing**, choose an active partner, and confirm the calculation breakdown follows the
   configured type, tier, and override precedence.
4. Add a fixed or percentage override and confirm the resolved price changes.
5. Sign in as that partner and verify only the final authorized price and applicable referral
   commission are displayed—not the internal breakdown.
6. Try another partner ID through the API and confirm the request is rejected with HTTP 403.


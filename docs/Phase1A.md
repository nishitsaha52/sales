# Phase 1A — Partner Access & Management

## Delivered workflows

### Public partner registration

1. A prospective partner opens `/register`.
2. Company, partner type, territory, primary contact, and credentials are submitted.
3. The partner is stored as `PENDING_APPROVAL`; its primary administrator remains inactive.
4. TCG Admin approves with a tier or rejects with a required reason.
5. Approval assigns a partner code, activates the partner, and activates its initial user.

### TCG-created partner

TCG Admin can create a partner from `/partners/new`. The partner and its primary Partner Admin
are active immediately. The selected tier remains an explicit, manually assigned value.

### Partner administration

- TCG Admin can view and manage every partner.
- TCG Sales can view partners but cannot approve, reject, or administer them.
- Partner users are restricted to records carrying their own `partner_id`.
- Partner Admin can update its company profile and administer its partner users.
- Other partner roles can view their own partner profile and user directory.
- Only partner roles may be assigned to partner users.
- A partner must retain at least one active Partner Admin.
- Suspended and inactive partners cannot have active users.

All authorization is enforced by the API. Hiding a frontend action is only a usability measure.

## Apply locally

Stop the API, then run:

```powershell
Set-Location C:\Users\nishi\Desktop\sales\backend
python -m alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload
```

The new migration is `20260923_0002`. The new seed is
`phase-1a-partner-master-data-v1`; both operations are safe to rerun.

## Acceptance smoke test

1. Sign in as TCG Admin and create an active partner.
2. Sign out and submit a second organization through `/register`.
3. Sign back in as TCG Admin and approve or reject the pending registration.
4. For an approved partner, open **Users**, create a Partner Sales user, and verify that the user
   cannot access another partner ID.
5. Suspend the partner and verify its users can no longer authenticate.
6. Confirm the partner workflow actions appear in `audit_logs` with their request IDs.


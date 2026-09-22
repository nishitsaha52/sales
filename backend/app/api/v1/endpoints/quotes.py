from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user
from app.api.v1.endpoints.workflow_common import (
    actor_role,
    make_reference,
    require_partner_scope,
    require_sales_manage,
    require_tcg,
)
from app.db.session import get_db
from app.domain.access import is_tcg_user
from app.domain.workflows import QUOTE_TRANSITIONS, WorkflowError, ensure_transition
from app.models.identity import User
from app.models.sales import (
    DealApprovalStatus,
    Opportunity,
    Quote,
    QuoteItem,
    QuoteRevision,
    QuoteStatus,
)
from app.schemas.sales import QuoteCreate, QuoteItemCreate, QuoteRead, StatusChange
from app.services.audit import record_audit_event
from app.services.pricing import resolve_partner_pricing

router = APIRouter()
CENT = Decimal("0.01")


async def get_quote(session: AsyncSession, quote_id: UUID) -> Quote:
    quote = await session.scalar(
        select(Quote)
        .where(Quote.id == quote_id)
        .options(selectinload(Quote.items), selectinload(Quote.revisions))
    )
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote


def recalculate(quote: Quote) -> None:
    subtotal = sum((item.unit_price * item.quantity for item in quote.items), Decimal("0"))
    total = sum((item.line_total for item in quote.items), Decimal("0"))
    quote.subtotal = subtotal.quantize(CENT, rounding=ROUND_HALF_UP)
    quote.total = total.quantize(CENT, rounding=ROUND_HALF_UP)
    quote.discount_total = (quote.subtotal - quote.total).quantize(CENT, rounding=ROUND_HALF_UP)


def snapshot(quote: Quote) -> dict[str, object]:
    return {
        "reference": quote.reference,
        "currency": quote.currency,
        "commercial_model": quote.commercial_model,
        "valid_until": quote.valid_until.isoformat() if quote.valid_until else None,
        "subtotal": str(quote.subtotal),
        "discount_total": str(quote.discount_total),
        "total": str(quote.total),
        "items": [
            {
                "sku_id": str(item.sku_id),
                "sku_code": item.sku_code,
                "sku_name": item.sku_name,
                "quantity": str(item.quantity),
                "unit_price": str(item.unit_price),
                "discount_percentage": str(item.discount_percentage),
                "line_total": str(item.line_total),
                "pricing_snapshot": item.pricing_snapshot,
            }
            for item in quote.items
        ],
    }


@router.get("", response_model=list[QuoteRead])
async def list_quotes(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[QuoteRead]:
    statement = select(Quote).options(selectinload(Quote.items)).order_by(Quote.created_at.desc())
    if not is_tcg_user(user):
        statement = statement.where(Quote.partner_id == user.partner_id)
    return [QuoteRead.model_validate(item) for item in await session.scalars(statement)]


@router.post("", response_model=QuoteRead, status_code=201)
async def create_quote(
    body: QuoteCreate,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> QuoteRead:
    require_sales_manage(user)
    deal = await session.get(Opportunity, body.opportunity_id)
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    require_partner_scope(user, deal.partner_id)
    if deal.approval_status != DealApprovalStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Quotes require an approved deal")
    quote = Quote(
        reference=make_reference("QTE"),
        opportunity_id=deal.id,
        partner_id=deal.partner_id,
        commercial_model=body.commercial_model,
        valid_until=body.valid_until,
        notes=body.notes,
        created_by_id=user.id,
    )
    session.add(quote)
    await session.flush()
    await record_audit_event(
        session,
        action="quote.created",
        entity_type="quote",
        entity_id=str(quote.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        request_id=getattr(request.state, "request_id", None),
    )
    await session.commit()
    return QuoteRead.model_validate(await get_quote(session, quote.id))


@router.post("/{quote_id}/items", response_model=QuoteRead)
async def add_quote_item(
    quote_id: UUID,
    body: QuoteItemCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> QuoteRead:
    quote = await get_quote(session, quote_id)
    require_partner_scope(user, quote.partner_id)
    require_sales_manage(user)
    if quote.status != QuoteStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Only draft quotes can be edited")
    pricing = await resolve_partner_pricing(
        session, quote.partner_id, as_of=date.today(), include_breakdown=True
    )
    resolved = next((item for item in pricing.items if item.sku_id == body.sku_id), None)
    if resolved is None:
        raise HTTPException(status_code=422, detail="No active price is available for this SKU")
    multiplier = (Decimal("100") - body.discount_percentage) / Decimal("100")
    line_total = (resolved.final_price * body.quantity * multiplier).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    item = QuoteItem(
        quote_id=quote.id,
        sku_id=resolved.sku_id,
        sku_code=resolved.sku_code,
        sku_name=resolved.sku_name,
        quantity=body.quantity,
        unit_price=resolved.final_price,
        discount_percentage=body.discount_percentage,
        line_total=line_total,
        pricing_snapshot={
            "as_of": pricing.as_of.isoformat(),
            "base_effective_from": resolved.effective_from.isoformat(),
            "commercial_model": str(resolved.commercial_model)
            if resolved.commercial_model
            else None,
            "commission_percentage": str(resolved.commission_percentage)
            if resolved.commission_percentage
            else None,
            "resolved_unit_price": str(resolved.final_price),
            "breakdown": resolved.breakdown.model_dump(mode="json") if resolved.breakdown else None,
        },
    )
    quote.items.append(item)
    recalculate(quote)
    await session.commit()
    return QuoteRead.model_validate(await get_quote(session, quote.id))


@router.post("/{quote_id}/status", response_model=QuoteRead)
async def change_quote_status(
    quote_id: UUID,
    body: StatusChange,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> QuoteRead:
    quote = await get_quote(session, quote_id)
    require_partner_scope(user, quote.partner_id)
    require_sales_manage(user)
    if body.status == QuoteStatus.FINAL:
        require_tcg(user)
        if not quote.items:
            raise HTTPException(status_code=409, detail="A quote needs at least one item")
    if body.status == QuoteStatus.ACCEPTED and is_tcg_user(user):
        raise HTTPException(status_code=403, detail="The partner must accept the final quote")
    try:
        ensure_transition(quote.status, body.status, QUOTE_TRANSITIONS)
    except WorkflowError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    old_status = quote.status
    quote.status = body.status
    if body.status == QuoteStatus.FINAL:
        recalculate(quote)
        quote.current_revision += 1
        session.add(
            QuoteRevision(
                quote_id=quote.id,
                revision_number=quote.current_revision,
                snapshot=snapshot(quote),
                created_by_id=user.id,
            )
        )
    await record_audit_event(
        session,
        action="quote.status_changed",
        entity_type="quote",
        entity_id=str(quote.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        old_values={"status": old_status},
        new_values={"status": body.status},
        request_id=getattr(request.state, "request_id", None),
    )
    await session.commit()
    return QuoteRead.model_validate(await get_quote(session, quote.id))


@router.post("/{quote_id}/revise", response_model=QuoteRead)
async def revise_quote(
    quote_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> QuoteRead:
    require_tcg(user)
    quote = await get_quote(session, quote_id)
    if quote.status != QuoteStatus.FINAL:
        raise HTTPException(status_code=409, detail="Only a final quote can be revised")
    quote.status = QuoteStatus.DRAFT
    await record_audit_event(
        session,
        action="quote.revision_started",
        entity_type="quote",
        entity_id=str(quote.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        old_values={"status": QuoteStatus.FINAL, "revision": quote.current_revision},
        new_values={"status": QuoteStatus.DRAFT},
        request_id=getattr(request.state, "request_id", None),
    )
    await session.commit()
    return QuoteRead.model_validate(await get_quote(session, quote.id))


@router.delete("/{quote_id}/items/{item_id}", response_model=QuoteRead)
async def remove_quote_item(
    quote_id: UUID,
    item_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> QuoteRead:
    quote = await get_quote(session, quote_id)
    require_partner_scope(user, quote.partner_id)
    require_sales_manage(user)
    if quote.status != QuoteStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Only draft quotes can be edited")
    item = next((candidate for candidate in quote.items if candidate.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Quote item not found")
    await session.delete(item)
    quote.items.remove(item)
    recalculate(quote)
    await session.commit()
    return QuoteRead.model_validate(await get_quote(session, quote.id))

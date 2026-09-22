from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.domain.access import is_tcg_admin, is_tcg_user, role_codes
from app.models.identity import User
from app.models.partner import Partner, PartnerTier, PartnerType
from app.models.pricing import (
    PartnerCommercialTerm,
    PartnerPriceOverride,
    Sku,
    TierPricingAdjustment,
)
from app.schemas.pricing import (
    CommercialTermRead,
    CommercialTermUpsert,
    PartnerOverrideCreate,
    PartnerOverrideRead,
    PartnerPricingResponse,
    PricingConfiguration,
    TierAdjustmentRead,
    TierAdjustmentUpsert,
)
from app.services.audit import record_audit_event
from app.services.pricing import resolve_partner_pricing

router = APIRouter()


def require_tcg_admin(user: User) -> None:
    if not is_tcg_admin(user):
        raise HTTPException(status_code=403, detail="TCG Admin access is required")


def actor_role(user: User) -> str | None:
    return sorted(role_codes(user))[0] if user.roles else None


@router.get("/resolved", response_model=PartnerPricingResponse)
async def resolved_pricing(
    partner_id: UUID | None = Query(default=None),
    as_of: date | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PartnerPricingResponse:
    if is_tcg_user(user):
        if partner_id is None:
            raise HTTPException(status_code=422, detail="partner_id is required for TCG users")
        target_partner_id = partner_id
    else:
        if user.partner_id is None:
            raise HTTPException(status_code=403, detail="A partner account is required")
        if partner_id is not None and partner_id != user.partner_id:
            raise HTTPException(
                status_code=403, detail="You cannot access another partner's pricing"
            )
        target_partner_id = user.partner_id
    return await resolve_partner_pricing(
        session,
        target_partner_id,
        as_of=as_of,
        include_breakdown=is_tcg_admin(user),
    )


@router.get("/configuration", response_model=PricingConfiguration)
async def pricing_configuration(
    partner_id: UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PricingConfiguration:
    require_tcg_admin(user)
    term_rows = (
        await session.execute(
            select(PartnerCommercialTerm, PartnerType.code, PartnerType.name)
            .join(PartnerType, PartnerCommercialTerm.partner_type_id == PartnerType.id)
            .order_by(PartnerType.name, PartnerCommercialTerm.effective_from.desc())
        )
    ).all()
    tier_rows = (
        await session.execute(
            select(TierPricingAdjustment, PartnerTier.code, PartnerTier.name)
            .join(PartnerTier, TierPricingAdjustment.tier_id == PartnerTier.id)
            .order_by(PartnerTier.rank, TierPricingAdjustment.effective_from.desc())
        )
    ).all()
    override_statement = (
        select(PartnerPriceOverride, Partner.company_name, Sku.code)
        .join(Partner, PartnerPriceOverride.partner_id == Partner.id)
        .join(Sku, PartnerPriceOverride.sku_id == Sku.id)
        .order_by(Partner.company_name, Sku.code, PartnerPriceOverride.effective_from.desc())
    )
    if partner_id:
        override_statement = override_statement.where(PartnerPriceOverride.partner_id == partner_id)
    override_rows = (await session.execute(override_statement)).all()
    return PricingConfiguration(
        commercial_terms=[
            CommercialTermRead(
                id=term.id,
                partner_type_id=term.partner_type_id,
                partner_type_code=type_code,
                partner_type_name=type_name,
                adjustment_type=term.adjustment_type,
                percentage=term.percentage,
                effective_from=term.effective_from,
                effective_until=term.effective_until,
                is_active=term.is_active,
            )
            for term, type_code, type_name in term_rows
        ],
        tier_adjustments=[
            TierAdjustmentRead(
                id=adjustment.id,
                tier_id=adjustment.tier_id,
                tier_code=tier_code,
                tier_name=tier_name,
                discount_percentage=adjustment.discount_percentage,
                effective_from=adjustment.effective_from,
                effective_until=adjustment.effective_until,
                is_active=adjustment.is_active,
            )
            for adjustment, tier_code, tier_name in tier_rows
        ],
        partner_overrides=[
            PartnerOverrideRead(
                id=override.id,
                partner_id=override.partner_id,
                partner_name=partner_name,
                sku_id=override.sku_id,
                sku_code=sku_code,
                override_type=override.override_type,
                value=override.value,
                currency=override.currency,
                effective_from=override.effective_from,
                effective_until=override.effective_until,
                is_active=override.is_active,
            )
            for override, partner_name, sku_code in override_rows
        ],
    )


@router.put("/partner-type-rules/{partner_type_id}", response_model=CommercialTermRead)
async def set_partner_type_rule(
    partner_type_id: UUID,
    payload: CommercialTermUpsert,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CommercialTermRead:
    require_tcg_admin(user)
    partner_type = await session.get(PartnerType, partner_type_id)
    if partner_type is None:
        raise HTTPException(status_code=404, detail="Partner type not found")
    term = await session.scalar(
        select(PartnerCommercialTerm).where(
            PartnerCommercialTerm.partner_type_id == partner_type_id,
            PartnerCommercialTerm.effective_from == payload.effective_from,
        )
    )
    action = "PARTNER_TYPE_PRICING_UPDATED" if term else "PARTNER_TYPE_PRICING_CREATED"
    if term is None:
        term = PartnerCommercialTerm(partner_type_id=partner_type_id, **payload.model_dump())
        session.add(term)
    else:
        term.adjustment_type = payload.adjustment_type
        term.percentage = payload.percentage
        term.effective_until = payload.effective_until
        term.is_active = True
    await session.flush()
    await record_audit_event(
        session,
        action=action,
        entity_type="partner_commercial_term",
        entity_id=str(term.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        new_values=payload.model_dump(mode="json") | {"partner_type_id": str(partner_type_id)},
        request_id=request.state.request_id,
    )
    await session.commit()
    return CommercialTermRead(
        id=term.id,
        partner_type_id=term.partner_type_id,
        partner_type_code=partner_type.code,
        partner_type_name=partner_type.name,
        adjustment_type=term.adjustment_type,
        percentage=term.percentage,
        effective_from=term.effective_from,
        effective_until=term.effective_until,
        is_active=term.is_active,
    )


@router.put("/tier-adjustments/{tier_id}", response_model=TierAdjustmentRead)
async def set_tier_adjustment(
    tier_id: UUID,
    payload: TierAdjustmentUpsert,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TierAdjustmentRead:
    require_tcg_admin(user)
    tier = await session.get(PartnerTier, tier_id)
    if tier is None:
        raise HTTPException(status_code=404, detail="Partner tier not found")
    adjustment = await session.scalar(
        select(TierPricingAdjustment).where(
            TierPricingAdjustment.tier_id == tier_id,
            TierPricingAdjustment.effective_from == payload.effective_from,
        )
    )
    action = "TIER_PRICING_UPDATED" if adjustment else "TIER_PRICING_CREATED"
    if adjustment is None:
        adjustment = TierPricingAdjustment(tier_id=tier_id, **payload.model_dump())
        session.add(adjustment)
    else:
        adjustment.discount_percentage = payload.discount_percentage
        adjustment.effective_until = payload.effective_until
        adjustment.is_active = True
    await session.flush()
    await record_audit_event(
        session,
        action=action,
        entity_type="tier_pricing_adjustment",
        entity_id=str(adjustment.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        new_values=payload.model_dump(mode="json") | {"tier_id": str(tier_id)},
        request_id=request.state.request_id,
    )
    await session.commit()
    return TierAdjustmentRead(
        id=adjustment.id,
        tier_id=adjustment.tier_id,
        tier_code=tier.code,
        tier_name=tier.name,
        discount_percentage=adjustment.discount_percentage,
        effective_from=adjustment.effective_from,
        effective_until=adjustment.effective_until,
        is_active=adjustment.is_active,
    )


@router.post(
    "/partner-overrides",
    response_model=PartnerOverrideRead,
    status_code=status.HTTP_201_CREATED,
)
async def set_partner_override(
    payload: PartnerOverrideCreate,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PartnerOverrideRead:
    require_tcg_admin(user)
    partner = await session.get(Partner, payload.partner_id)
    sku = await session.get(Sku, payload.sku_id)
    if partner is None or sku is None:
        raise HTTPException(status_code=404, detail="Partner or SKU not found")
    override = await session.scalar(
        select(PartnerPriceOverride).where(
            PartnerPriceOverride.partner_id == payload.partner_id,
            PartnerPriceOverride.sku_id == payload.sku_id,
            PartnerPriceOverride.effective_from == payload.effective_from,
        )
    )
    action = "PARTNER_PRICE_OVERRIDE_UPDATED" if override else "PARTNER_PRICE_OVERRIDE_CREATED"
    if override is None:
        override = PartnerPriceOverride(**payload.model_dump(), currency="USD")
        session.add(override)
    else:
        override.override_type = payload.override_type
        override.value = payload.value
        override.effective_until = payload.effective_until
        override.is_active = True
    await session.flush()
    await record_audit_event(
        session,
        action=action,
        entity_type="partner_price_override",
        entity_id=str(override.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        new_values=payload.model_dump(mode="json") | {"currency": "USD"},
        request_id=request.state.request_id,
    )
    await session.commit()
    return PartnerOverrideRead(
        id=override.id,
        partner_id=override.partner_id,
        partner_name=partner.company_name,
        sku_id=override.sku_id,
        sku_code=sku.code,
        override_type=override.override_type,
        value=override.value,
        currency=override.currency,
        effective_from=override.effective_from,
        effective_until=override.effective_until,
        is_active=override.is_active,
    )


@router.delete("/partner-overrides/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_partner_override(
    override_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    require_tcg_admin(user)
    override = await session.get(PartnerPriceOverride, override_id)
    if override is None:
        raise HTTPException(status_code=404, detail="Partner price override not found")
    override.is_active = False
    await record_audit_event(
        session,
        action="PARTNER_PRICE_OVERRIDE_DEACTIVATED",
        entity_type="partner_price_override",
        entity_id=str(override.id),
        actor_user_id=user.id,
        actor_role=actor_role(user),
        request_id=request.state.request_id,
    )
    await session.commit()

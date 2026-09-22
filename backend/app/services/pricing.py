from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.pricing import (
    AdjustmentType,
    OverrideType,
    PartnerCommercialTerm,
    PartnerPriceOverride,
    Product,
    ProductPrice,
    Sku,
    TierPricingAdjustment,
)
from app.schemas.pricing import (
    PartnerPricingResponse,
    PriceBreakdown,
    ResolvedPriceRead,
)
from app.services.partners import load_partner

MONEY = Decimal("0.01")
ZERO = Decimal("0")
HUNDRED = Decimal("100")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PriceCalculation:
    final_price: Decimal
    after_partner_type: Decimal
    after_tier: Decimal
    commission_percentage: Decimal | None


def calculate_price(
    list_price: Decimal,
    *,
    adjustment_type: AdjustmentType | None = None,
    adjustment_percentage: Decimal = ZERO,
    tier_discount_percentage: Decimal = ZERO,
    override_type: OverrideType | None = None,
    override_value: Decimal | None = None,
) -> PriceCalculation:
    after_type = list_price
    commission = None
    if adjustment_type == AdjustmentType.PERCENT_DISCOUNT:
        after_type = list_price * (HUNDRED - adjustment_percentage) / HUNDRED
    elif adjustment_type == AdjustmentType.PERCENT_MARKUP:
        after_type = list_price * (HUNDRED + adjustment_percentage) / HUNDRED
    elif adjustment_type == AdjustmentType.REFERRAL_COMMISSION:
        commission = adjustment_percentage
    after_type = money(after_type)

    after_tier = money(after_type * (HUNDRED - tier_discount_percentage) / HUNDRED)
    final = after_tier
    if override_type == OverrideType.FIXED_PRICE and override_value is not None:
        final = override_value
    elif override_type == OverrideType.PERCENT_DISCOUNT and override_value is not None:
        final = after_tier * (HUNDRED - override_value) / HUNDRED
    elif override_type == OverrideType.PERCENT_MARKUP and override_value is not None:
        final = after_tier * (HUNDRED + override_value) / HUNDRED
    return PriceCalculation(
        final_price=money(final),
        after_partner_type=after_type,
        after_tier=after_tier,
        commission_percentage=commission,
    )


def effective_on(model: Any, as_of: date) -> tuple[Any, ...]:
    return (
        model.is_active.is_(True),
        model.effective_from <= as_of,
        or_(model.effective_until.is_(None), model.effective_until >= as_of),
    )


async def resolve_partner_pricing(
    session: AsyncSession,
    partner_id: UUID,
    *,
    as_of: date | None = None,
    include_breakdown: bool = False,
) -> PartnerPricingResponse:
    pricing_date = as_of or datetime.now(UTC).date()
    partner = await load_partner(session, partner_id)
    skus = list(
        await session.scalars(
            select(Sku)
            .join(Product)
            .where(Sku.is_active.is_(True), Product.is_active.is_(True))
            .options(joinedload(Sku.product))
            .order_by(Product.name, Sku.name)
        )
    )
    if not skus:
        return PartnerPricingResponse(
            partner_id=partner.id,
            partner_name=partner.company_name,
            as_of=pricing_date,
            items=[],
        )

    sku_ids = [sku.id for sku in skus]
    price_rows = list(
        await session.scalars(
            select(ProductPrice)
            .where(ProductPrice.sku_id.in_(sku_ids), *effective_on(ProductPrice, pricing_date))
            .order_by(ProductPrice.effective_from.desc())
        )
    )
    prices: dict[UUID, ProductPrice] = {}
    for price in price_rows:
        prices.setdefault(price.sku_id, price)

    commercial_term = await session.scalar(
        select(PartnerCommercialTerm)
        .where(
            PartnerCommercialTerm.partner_type_id == partner.partner_type_id,
            *effective_on(PartnerCommercialTerm, pricing_date),
        )
        .order_by(PartnerCommercialTerm.effective_from.desc())
        .limit(1)
    )
    tier_adjustment = None
    if partner.tier_id:
        tier_adjustment = await session.scalar(
            select(TierPricingAdjustment)
            .where(
                TierPricingAdjustment.tier_id == partner.tier_id,
                *effective_on(TierPricingAdjustment, pricing_date),
            )
            .order_by(TierPricingAdjustment.effective_from.desc())
            .limit(1)
        )
    override_rows = list(
        await session.scalars(
            select(PartnerPriceOverride)
            .where(
                PartnerPriceOverride.partner_id == partner.id,
                PartnerPriceOverride.sku_id.in_(sku_ids),
                *effective_on(PartnerPriceOverride, pricing_date),
            )
            .order_by(PartnerPriceOverride.effective_from.desc())
        )
    )
    overrides: dict[UUID, PartnerPriceOverride] = {}
    for override_row in override_rows:
        overrides.setdefault(override_row.sku_id, override_row)

    adjustment_type = AdjustmentType(commercial_term.adjustment_type) if commercial_term else None
    adjustment_percentage = commercial_term.percentage if commercial_term else ZERO
    tier_percentage = tier_adjustment.discount_percentage if tier_adjustment else ZERO
    items: list[ResolvedPriceRead] = []
    for sku in skus:
        base_price = prices.get(sku.id)
        if base_price is None:
            continue
        override = overrides.get(sku.id)
        override_type = OverrideType(override.override_type) if override else None
        override_value = override.value if override else None
        calculation = calculate_price(
            base_price.amount,
            adjustment_type=adjustment_type,
            adjustment_percentage=adjustment_percentage,
            tier_discount_percentage=tier_percentage,
            override_type=override_type,
            override_value=override_value,
        )
        breakdown = None
        if include_breakdown:
            breakdown = PriceBreakdown(
                list_price=money(base_price.amount),
                partner_type_adjustment=adjustment_type,
                partner_type_percentage=adjustment_percentage,
                after_partner_type=calculation.after_partner_type,
                tier_discount_percentage=tier_percentage,
                after_tier=calculation.after_tier,
                override_type=override_type,
                override_value=override_value,
            )
        items.append(
            ResolvedPriceRead(
                product_id=sku.product.id,
                product_code=sku.product.code,
                product_name=sku.product.name,
                sku_id=sku.id,
                sku_code=sku.code,
                sku_name=sku.name,
                sku_description=sku.description,
                unit=sku.unit,
                final_price=calculation.final_price,
                effective_from=base_price.effective_from,
                effective_until=base_price.effective_until,
                commercial_model=adjustment_type,
                commission_percentage=calculation.commission_percentage,
                breakdown=breakdown,
            )
        )
    return PartnerPricingResponse(
        partner_id=partner.id,
        partner_name=partner.company_name,
        as_of=pricing_date,
        items=items,
    )

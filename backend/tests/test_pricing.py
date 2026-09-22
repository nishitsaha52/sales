from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.pricing import AdjustmentType, OverrideType
from app.schemas.pricing import CommercialTermUpsert, ProductCreate
from app.services.pricing import calculate_price


def test_reseller_discount_then_tier_benefit() -> None:
    result = calculate_price(
        Decimal("100.00"),
        adjustment_type=AdjustmentType.PERCENT_DISCOUNT,
        adjustment_percentage=Decimal("20"),
        tier_discount_percentage=Decimal("5"),
    )

    assert result.after_partner_type == Decimal("80.00")
    assert result.after_tier == Decimal("76.00")
    assert result.final_price == Decimal("76.00")


def test_si_markup_and_partner_override_follow_precedence() -> None:
    result = calculate_price(
        Decimal("100.00"),
        adjustment_type=AdjustmentType.PERCENT_MARKUP,
        adjustment_percentage=Decimal("15"),
        tier_discount_percentage=Decimal("10"),
        override_type=OverrideType.FIXED_PRICE,
        override_value=Decimal("99.99"),
    )

    assert result.after_partner_type == Decimal("115.00")
    assert result.after_tier == Decimal("103.50")
    assert result.final_price == Decimal("99.99")


def test_referral_commission_does_not_change_unit_price() -> None:
    result = calculate_price(
        Decimal("250.00"),
        adjustment_type=AdjustmentType.REFERRAL_COMMISSION,
        adjustment_percentage=Decimal("3"),
    )

    assert result.final_price == Decimal("250.00")
    assert result.commission_percentage == Decimal("3")


def test_percentage_override_is_applied_last() -> None:
    result = calculate_price(
        Decimal("100.00"),
        adjustment_type=AdjustmentType.PERCENT_DISCOUNT,
        adjustment_percentage=Decimal("20"),
        tier_discount_percentage=Decimal("5"),
        override_type=OverrideType.PERCENT_DISCOUNT,
        override_value=Decimal("10"),
    )

    assert result.final_price == Decimal("68.40")


def test_referral_commission_is_limited_to_confirmed_range() -> None:
    with pytest.raises(ValidationError):
        CommercialTermUpsert(
            adjustment_type=AdjustmentType.REFERRAL_COMMISSION,
            percentage=Decimal("6"),
            effective_from=date(2026, 1, 1),
        )


def test_product_codes_are_normalized_by_contract() -> None:
    with pytest.raises(ValidationError):
        ProductCreate(code="lowercase", name="Example")

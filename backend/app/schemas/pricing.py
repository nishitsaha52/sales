from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.pricing import AdjustmentType, OverrideType, SkuCategory


class EffectiveDatedSchema(BaseModel):
    effective_from: date
    effective_until: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "EffectiveDatedSchema":
        if self.effective_until and self.effective_until < self.effective_from:
            raise ValueError("effective_until must be on or after effective_from")
        return self


class ProductCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50, pattern=r"^[A-Z0-9][A-Z0-9_-]*$")
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=4000)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=4000)
    is_active: bool | None = None


class SkuCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80, pattern=r"^[A-Z0-9][A-Z0-9_-]*$")
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=4000)
    category: SkuCategory
    unit: str = Field(default="unit", min_length=1, max_length=50)


class SkuUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=4000)
    category: SkuCategory | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None


class SkuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    code: str
    name: str
    description: str | None
    category: SkuCategory
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None
    is_active: bool
    skus: list[SkuRead]
    created_at: datetime
    updated_at: datetime


class ProductPriceCreate(EffectiveDatedSchema):
    amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class ProductPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sku_id: UUID
    amount: Decimal
    currency: str
    effective_from: date
    effective_until: date | None
    is_active: bool


class CommercialTermUpsert(EffectiveDatedSchema):
    adjustment_type: AdjustmentType
    percentage: Decimal = Field(ge=0, le=1000, max_digits=7, decimal_places=4)

    @model_validator(mode="after")
    def validate_adjustment(self) -> "CommercialTermUpsert":
        if self.adjustment_type == AdjustmentType.PERCENT_DISCOUNT and self.percentage > 100:
            raise ValueError("Discount percentage cannot exceed 100")
        if self.adjustment_type == AdjustmentType.REFERRAL_COMMISSION and not (
            Decimal("1") <= self.percentage <= Decimal("5")
        ):
            raise ValueError("Referral commission must be between 1% and 5%")
        if self.adjustment_type == AdjustmentType.NONE and self.percentage != 0:
            raise ValueError("NONE adjustment must use zero percent")
        return self


class CommercialTermRead(BaseModel):
    id: UUID
    partner_type_id: UUID
    partner_type_code: str
    partner_type_name: str
    adjustment_type: AdjustmentType
    percentage: Decimal
    effective_from: date
    effective_until: date | None
    is_active: bool


class TierAdjustmentUpsert(EffectiveDatedSchema):
    discount_percentage: Decimal = Field(ge=0, le=100, max_digits=7, decimal_places=4)


class TierAdjustmentRead(BaseModel):
    id: UUID
    tier_id: UUID
    tier_code: str
    tier_name: str
    discount_percentage: Decimal
    effective_from: date
    effective_until: date | None
    is_active: bool


class PartnerOverrideCreate(EffectiveDatedSchema):
    partner_id: UUID
    sku_id: UUID
    override_type: OverrideType
    value: Decimal = Field(ge=0, max_digits=18, decimal_places=4)

    @model_validator(mode="after")
    def validate_override(self) -> "PartnerOverrideCreate":
        if self.override_type == OverrideType.PERCENT_DISCOUNT and self.value > 100:
            raise ValueError("Discount percentage cannot exceed 100")
        return self


class PartnerOverrideRead(BaseModel):
    id: UUID
    partner_id: UUID
    partner_name: str
    sku_id: UUID
    sku_code: str
    override_type: OverrideType
    value: Decimal
    currency: str
    effective_from: date
    effective_until: date | None
    is_active: bool


class PricingConfiguration(BaseModel):
    commercial_terms: list[CommercialTermRead]
    tier_adjustments: list[TierAdjustmentRead]
    partner_overrides: list[PartnerOverrideRead]


class PriceBreakdown(BaseModel):
    list_price: Decimal
    partner_type_adjustment: AdjustmentType | None
    partner_type_percentage: Decimal
    after_partner_type: Decimal
    tier_discount_percentage: Decimal
    after_tier: Decimal
    override_type: OverrideType | None
    override_value: Decimal | None


class ResolvedPriceRead(BaseModel):
    product_id: UUID
    product_code: str
    product_name: str
    sku_id: UUID
    sku_code: str
    sku_name: str
    sku_description: str | None
    unit: str
    currency: str = "USD"
    final_price: Decimal
    effective_from: date
    effective_until: date | None
    commercial_model: AdjustmentType | None
    commission_percentage: Decimal | None
    breakdown: PriceBreakdown | None = None


class PartnerPricingResponse(BaseModel):
    partner_id: UUID
    partner_name: str
    as_of: date
    currency: str = "USD"
    items: list[ResolvedPriceRead]

"""Add product catalog and pricing configuration.

Revision ID: 20260923_0003
Revises: 20260923_0002
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0003"
down_revision: str | None = "20260923_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def effective_range_constraint(name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        "effective_until IS NULL OR effective_until >= effective_from", name=name
    )


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_products"),
        sa.UniqueConstraint("code", name="uq_products_code"),
    )
    op.create_index("ix_products_code", "products", ["code"])
    op.create_index("ix_products_is_active", "products", ["is_active"])

    op.create_table(
        "skus",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("unit", sa.String(length=50), server_default="unit", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "category IN ('LICENSE', 'IMPLEMENTATION', 'SERVICE', 'OTHER')",
            name="ck_skus_valid_category",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name="fk_skus_product_id_products", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_skus"),
        sa.UniqueConstraint("code", name="uq_skus_code"),
    )
    op.create_index("ix_skus_code", "skus", ["code"])
    op.create_index("ix_skus_is_active", "skus", ["is_active"])
    op.create_index("ix_skus_product_id", "skus", ["product_id"])

    op.create_table(
        "product_prices",
        sa.Column("sku_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.CheckConstraint("amount >= 0", name="ck_product_prices_non_negative_amount"),
        sa.CheckConstraint("currency = 'USD'", name="ck_product_prices_usd_currency"),
        effective_range_constraint("ck_product_prices_valid_effective_range"),
        sa.ForeignKeyConstraint(
            ["sku_id"], ["skus.id"], name="fk_product_prices_sku_id_skus", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_product_prices"),
        sa.UniqueConstraint("sku_id", "effective_from", name="uq_product_prices_sku_effective"),
    )
    op.create_index("ix_product_prices_effective_from", "product_prices", ["effective_from"])
    op.create_index("ix_product_prices_sku_id", "product_prices", ["sku_id"])

    op.create_table(
        "partner_commercial_terms",
        sa.Column("partner_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("adjustment_type", sa.String(length=30), nullable=False),
        sa.Column("percentage", sa.Numeric(7, 4), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "adjustment_type IN ('NONE', 'PERCENT_DISCOUNT', "
            "'PERCENT_MARKUP', 'REFERRAL_COMMISSION')",
            name="ck_partner_commercial_terms_valid_adjustment_type",
        ),
        sa.CheckConstraint(
            "percentage >= 0 AND percentage <= 1000",
            name="ck_partner_commercial_terms_valid_percentage",
        ),
        effective_range_constraint("ck_partner_commercial_terms_valid_effective_range"),
        sa.ForeignKeyConstraint(
            ["partner_type_id"],
            ["partner_types.id"],
            name="fk_partner_commercial_terms_partner_type_id_partner_types",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_partner_commercial_terms"),
        sa.UniqueConstraint(
            "partner_type_id",
            "effective_from",
            name="uq_partner_terms_type_effective",
        ),
    )
    op.create_index(
        "ix_partner_commercial_terms_effective_from",
        "partner_commercial_terms",
        ["effective_from"],
    )
    op.create_index(
        "ix_partner_commercial_terms_partner_type_id",
        "partner_commercial_terms",
        ["partner_type_id"],
    )

    op.create_table(
        "tier_pricing_adjustments",
        sa.Column("tier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("discount_percentage", sa.Numeric(7, 4), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="ck_tier_pricing_adjustments_valid_discount_percentage",
        ),
        effective_range_constraint("ck_tier_pricing_adjustments_valid_effective_range"),
        sa.ForeignKeyConstraint(
            ["tier_id"],
            ["partner_tiers.id"],
            name="fk_tier_pricing_adjustments_tier_id_partner_tiers",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tier_pricing_adjustments"),
        sa.UniqueConstraint("tier_id", "effective_from", name="uq_tier_adjustments_tier_effective"),
    )
    op.create_index(
        "ix_tier_pricing_adjustments_effective_from",
        "tier_pricing_adjustments",
        ["effective_from"],
    )
    op.create_index("ix_tier_pricing_adjustments_tier_id", "tier_pricing_adjustments", ["tier_id"])

    op.create_table(
        "partner_price_overrides",
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("override_type", sa.String(length=30), nullable=False),
        sa.Column("value", sa.Numeric(18, 4), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "override_type IN ('FIXED_PRICE', 'PERCENT_DISCOUNT', 'PERCENT_MARKUP')",
            name="ck_partner_price_overrides_valid_override_type",
        ),
        sa.CheckConstraint("value >= 0", name="ck_partner_price_overrides_non_negative_value"),
        sa.CheckConstraint("currency = 'USD'", name="ck_partner_price_overrides_usd_currency"),
        effective_range_constraint("ck_partner_price_overrides_valid_effective_range"),
        sa.ForeignKeyConstraint(
            ["partner_id"],
            ["partners.id"],
            name="fk_partner_price_overrides_partner_id_partners",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sku_id"],
            ["skus.id"],
            name="fk_partner_price_overrides_sku_id_skus",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_partner_price_overrides"),
        sa.UniqueConstraint(
            "partner_id",
            "sku_id",
            "effective_from",
            name="uq_partner_overrides_effective",
        ),
    )
    op.create_index(
        "ix_partner_price_overrides_effective_from",
        "partner_price_overrides",
        ["effective_from"],
    )
    op.create_index(
        "ix_partner_price_overrides_partner_id", "partner_price_overrides", ["partner_id"]
    )
    op.create_index("ix_partner_price_overrides_sku_id", "partner_price_overrides", ["sku_id"])


def downgrade() -> None:
    op.drop_table("partner_price_overrides")
    op.drop_table("tier_pricing_adjustments")
    op.drop_table("partner_commercial_terms")
    op.drop_table("product_prices")
    op.drop_table("skus")
    op.drop_table("products")

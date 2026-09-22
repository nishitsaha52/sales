"""Add content, deal, quote, MAF, and order workflows.

Revision ID: 20260923_0004
Revises: 20260923_0003
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0004"
down_revision: str | None = "20260923_0003"
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


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("legal_name", sa.String(200)),
        sa.Column("website", sa.String(500)),
        sa.Column("industry", sa.String(100)),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("contact_name", sa.String(200)),
        sa.Column("contact_email", sa.String(320)),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        uuid_pk(),
        *timestamps(),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_name", "customers", ["name"])
    op.create_index("ix_customers_country_code", "customers", ["country_code"])

    op.create_table(
        "documents",
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("visibility", sa.String(40), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True)),
        sa.Column("partner_type_id", postgresql.UUID(as_uuid=True)),
        sa.Column("partner_tier_id", postgresql.UUID(as_uuid=True)),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        uuid_pk(),
        *timestamps(),
        sa.CheckConstraint(
            "category IN ('SALES_ENABLEMENT','PRODUCT_DOCUMENTATION','IMPLEMENTATION_GUIDE',"
            "'PRICING','PROPOSAL_TEMPLATE','SOW_TEMPLATE','RFP','OTHER')",
            name="ck_documents_valid_category",
        ),
        sa.CheckConstraint(
            "visibility IN ('ALL_PARTNERS','PARTNER_TYPE','PARTNER_TIER',"
            "'SPECIFIC_PARTNER','TCG_INTERNAL')",
            name="ck_documents_valid_visibility",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["partner_type_id"], ["partner_types.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["partner_tier_id"], ["partner_tiers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("title", "category", "visibility", "product_id", "partner_id", "is_active"):
        op.create_index(f"ix_documents_{column}", "documents", [column])
    op.create_table(
        "document_versions",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("object_key", sa.String(700), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("change_note", sa.String(500)),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        uuid_pk(),
        *timestamps(),
        sa.CheckConstraint("version_number > 0", name="ck_document_versions_positive_version"),
        sa.CheckConstraint("size_bytes >= 0", name="ck_document_versions_non_negative_size"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_version"),
    )
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])

    op.create_table(
        "opportunities",
        sa.Column("reference", sa.String(30), nullable=False),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("estimated_value", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("expected_close_date", sa.Date()),
        sa.Column("approval_status", sa.String(30), server_default="DRAFT", nullable=False),
        sa.Column("stage", sa.String(30), server_default="REGISTERED", nullable=False),
        sa.Column("review_reason", sa.String(1000)),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("protection_expires_at", sa.DateTime(timezone=True)),
        sa.Column("actual_contract_value", sa.Numeric(18, 2)),
        sa.Column("actual_close_date", sa.Date()),
        sa.Column("lost_reason", sa.String(1000)),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True)),
        uuid_pk(),
        *timestamps(),
        sa.CheckConstraint(
            "approval_status IN ('DRAFT','SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED')",
            name="ck_opportunities_valid_approval_status",
        ),
        sa.CheckConstraint(
            "stage IN ('REGISTERED','QUALIFIED','DISCOVERY','DEMO','POC',"
            "'PROPOSAL','NEGOTIATION','WON','LOST')",
            name="ck_opportunities_valid_stage",
        ),
        sa.CheckConstraint(
            "estimated_value >= 0", name="ck_opportunities_non_negative_estimated_value"
        ),
        sa.CheckConstraint(
            "actual_contract_value IS NULL OR actual_contract_value >= 0",
            name="ck_opportunities_non_negative_actual_value",
        ),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    for column in (
        "reference",
        "partner_id",
        "customer_id",
        "product_id",
        "approval_status",
        "stage",
        "protection_expires_at",
    ):
        op.create_index(f"ix_opportunities_{column}", "opportunities", [column])
    op.create_table(
        "opportunity_stage_history",
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_stage", sa.String(30)),
        sa.Column("to_stage", sa.String(30), nullable=False),
        sa.Column("note", sa.String(1000)),
        sa.Column("changed_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        uuid_pk(),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunity_stage_history_opportunity_id",
        "opportunity_stage_history",
        ["opportunity_id"],
    )

    op.create_table(
        "stored_attachments",
        sa.Column("owner_type", sa.String(30), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("object_key", sa.String(700), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        uuid_pk(),
        *timestamps(),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index("ix_stored_attachments_owner_type", "stored_attachments", ["owner_type"])
    op.create_index("ix_stored_attachments_owner_id", "stored_attachments", ["owner_id"])

    op.create_table(
        "quotes",
        sa.Column("reference", sa.String(30), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(30), server_default="DRAFT", nullable=False),
        sa.Column("commercial_model", sa.String(50), nullable=False),
        sa.Column("valid_until", sa.Date()),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("subtotal", sa.Numeric(18, 2), nullable=False),
        sa.Column("discount_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("total", sa.Numeric(18, 2), nullable=False),
        sa.Column("current_revision", sa.Integer(), server_default="0", nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        uuid_pk(),
        *timestamps(),
        sa.CheckConstraint(
            "status IN ('DRAFT','UNDER_REVIEW','FINAL','ACCEPTED','EXPIRED','CANCELLED')",
            name="ck_quotes_valid_status",
        ),
        sa.CheckConstraint(
            "subtotal >= 0 AND discount_total >= 0 AND total >= 0", name="ck_quotes_amounts"
        ),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    for column in ("reference", "opportunity_id", "partner_id", "status"):
        op.create_index(f"ix_quotes_{column}", "quotes", [column])
    op.create_table(
        "quote_items",
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku_code", sa.String(80), nullable=False),
        sa.Column("sku_name", sa.String(150), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("discount_percentage", sa.Numeric(7, 4), nullable=False),
        sa.Column("line_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("pricing_snapshot", postgresql.JSONB(), nullable=False),
        uuid_pk(),
        *timestamps(),
        sa.CheckConstraint("quantity > 0", name="ck_quote_items_positive_quantity"),
        sa.CheckConstraint(
            "unit_price >= 0 AND line_total >= 0", name="ck_quote_items_non_negative_amounts"
        ),
        sa.CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="ck_quote_items_discount",
        ),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quote_items_quote_id", "quote_items", ["quote_id"])
    op.create_table(
        "quote_revisions",
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        uuid_pk(),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quote_id", "revision_number", name="uq_quote_revision"),
    )
    op.create_index("ix_quote_revisions_quote_id", "quote_revisions", ["quote_id"])

    op.create_table(
        "maf_requests",
        sa.Column("reference", sa.String(30), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("tender_reference", sa.String(150), nullable=False),
        sa.Column("tender_authority", sa.String(200), nullable=False),
        sa.Column("tender_due_date", sa.Date(), nullable=False),
        sa.Column("tender_value", sa.Numeric(18, 2)),
        sa.Column("details", sa.Text()),
        sa.Column("review_reason", sa.String(1000)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True)),
        uuid_pk(),
        *timestamps(),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    for column in ("reference", "opportunity_id", "partner_id", "status"):
        op.create_index(f"ix_maf_requests_{column}", "maf_requests", [column])

    op.create_table(
        "orders",
        sa.Column("reference", sa.String(30), nullable=False),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("billing_name", sa.String(200), nullable=False),
        sa.Column("billing_address", sa.Text(), nullable=False),
        sa.Column("billing_email", sa.String(320), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("total", sa.Numeric(18, 2), nullable=False),
        sa.Column("quote_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("review_reason", sa.String(1000)),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True)),
        uuid_pk(),
        *timestamps(),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
        sa.UniqueConstraint("quote_id"),
    )
    for column in ("reference", "quote_id", "partner_id", "status"):
        op.create_index(f"ix_orders_{column}", "orders", [column])
    op.create_table(
        "order_status_history",
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_status", sa.String(40)),
        sa.Column("to_status", sa.String(40), nullable=False),
        sa.Column("note", sa.String(1000)),
        sa.Column("changed_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        uuid_pk(),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_status_history_order_id", "order_status_history", ["order_id"])
    op.create_table(
        "domain_events",
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("aggregate_type", sa.String(50), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        uuid_pk(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_domain_events_event_type", "domain_events", ["event_type"])
    op.create_index("ix_domain_events_aggregate_id", "domain_events", ["aggregate_id"])


def downgrade() -> None:
    for table in (
        "domain_events",
        "order_status_history",
        "orders",
        "maf_requests",
        "quote_revisions",
        "quote_items",
        "quotes",
        "stored_attachments",
        "opportunity_stage_history",
        "opportunities",
        "document_versions",
        "documents",
        "customers",
    ):
        op.drop_table(table)

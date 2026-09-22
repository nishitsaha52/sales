"""Add partner access and management data model.

Revision ID: 20260923_0002
Revises: 20260922_0001
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0002"
down_revision: str | None = "20260922_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> tuple[sa.Column, sa.Column]:
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


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_countries"),
        sa.UniqueConstraint("code", name="uq_countries_code"),
        sa.UniqueConstraint("name", name="uq_countries_name"),
    )
    op.create_index("ix_countries_code", "countries", ["code"])

    op.create_table(
        "partner_tiers",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_partner_tiers"),
        sa.UniqueConstraint("code", name="uq_partner_tiers_code"),
        sa.UniqueConstraint("rank", name="uq_partner_tiers_rank"),
    )
    op.create_index("ix_partner_tiers_code", "partner_tiers", ["code"])

    op.create_table(
        "partner_types",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_partner_types"),
        sa.UniqueConstraint("code", name="uq_partner_types_code"),
    )
    op.create_index("ix_partner_types_code", "partner_types", ["code"])

    op.create_table(
        "partners",
        sa.Column("code", sa.String(length=30), nullable=True),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("legal_name", sa.String(length=200), nullable=True),
        sa.Column("company_email", sa.String(length=320), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("primary_contact_name", sa.String(length=200), nullable=False),
        sa.Column("primary_contact_email", sa.String(length=320), nullable=False),
        sa.Column("primary_contact_phone", sa.String(length=50), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default="PENDING_APPROVAL",
            nullable=False,
        ),
        sa.Column("rejection_reason", sa.String(length=1000), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("partner_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('PENDING_APPROVAL', 'ACTIVE', 'REJECTED', 'SUSPENDED', 'INACTIVE')",
            name="ck_partners_valid_status",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by_id"],
            ["users.id"],
            name="fk_partners_approved_by_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name="fk_partners_created_by_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["partner_type_id"],
            ["partner_types.id"],
            name="fk_partners_partner_type_id_partner_types",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tier_id"],
            ["partner_tiers.id"],
            name="fk_partners_tier_id_partner_tiers",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_partners"),
        sa.UniqueConstraint("code", name="uq_partners_code"),
    )
    op.create_index("ix_partners_code", "partners", ["code"])
    op.create_index("ix_partners_company_email", "partners", ["company_email"])
    op.create_index("ix_partners_company_name", "partners", ["company_name"])
    op.create_index("ix_partners_partner_type_id", "partners", ["partner_type_id"])
    op.create_index("ix_partners_status", "partners", ["status"])
    op.create_index("ix_partners_tier_id", "partners", ["tier_id"])

    op.create_table(
        "partner_countries",
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["country_id"],
            ["countries.id"],
            name="fk_partner_countries_country_id_countries",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["partner_id"],
            ["partners.id"],
            name="fk_partner_countries_partner_id_partners",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("partner_id", "country_id", name="pk_partner_countries"),
    )

    op.add_column("users", sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_users_partner_id", "users", ["partner_id"])
    op.create_foreign_key(
        "fk_users_partner_id_partners",
        "users",
        "partners",
        ["partner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_partner_id_partners", "users", type_="foreignkey")
    op.drop_index("ix_users_partner_id", table_name="users")
    op.drop_column("users", "partner_id")
    op.drop_table("partner_countries")
    op.drop_table("partners")
    op.drop_table("partner_types")
    op.drop_table("partner_tiers")
    op.drop_table("countries")

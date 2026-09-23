from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import DateTime

from app.domain.access import can_manage_partner, can_view_partner, is_tcg_admin
from app.models.identity import Role, User
from app.models.partner import Partner
from app.schemas.partner import PartnerRegistrationRequest, PartnerUserCreate


def make_user(*role_codes: str, partner_id: object = None) -> User:
    return User(
        email=f"{uuid4()}@example.com",
        full_name="Test User",
        hashed_password="not-used",
        is_active=True,
        is_superuser=False,
        partner_id=partner_id,
        roles=[Role(code=code, name=code, permissions=[]) for code in role_codes],
    )


def test_tcg_admin_can_manage_any_partner() -> None:
    admin = make_user("TCG_ADMIN")

    assert is_tcg_admin(admin)
    assert can_view_partner(admin, uuid4())
    assert can_manage_partner(admin, uuid4())


def test_partner_admin_is_isolated_to_own_partner() -> None:
    own_partner = uuid4()
    other_partner = uuid4()
    admin = make_user("PARTNER_ADMIN", partner_id=own_partner)

    assert can_view_partner(admin, own_partner)
    assert can_manage_partner(admin, own_partner)
    assert not can_view_partner(admin, other_partner)
    assert not can_manage_partner(admin, other_partner)


def test_partner_sales_can_view_but_not_manage_own_partner() -> None:
    own_partner = uuid4()
    sales_user = make_user("PARTNER_SALES", partner_id=own_partner)

    assert can_view_partner(sales_user, own_partner)
    assert not can_manage_partner(sales_user, own_partner)


def test_registration_normalizes_master_data_codes() -> None:
    registration = PartnerRegistrationRequest(
        company_name="Example Partner",
        partner_type_code=" reseller ",
        country_codes=["in", "US", "in"],
        company_email="company@example.com",
        primary_contact_name="Partner Admin",
        primary_contact_email="admin@example.com",
        password="long-test-password",
    )

    assert registration.partner_type_code == "RESELLER"
    assert registration.country_codes == ["IN", "US"]


def test_registration_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        PartnerRegistrationRequest(
            company_name="Example Partner",
            partner_type_code="RESELLER",
            country_codes=["IN"],
            company_email="company@example.com",
            primary_contact_name="Partner Admin",
            primary_contact_email="admin@example.com",
            password="short",
        )


def test_partner_user_roles_are_normalized_and_deduplicated() -> None:
    user = PartnerUserCreate(
        email="member@example.com",
        full_name="Team Member",
        password="long-test-password",
        role_codes=["partner_sales", "PARTNER_SALES"],
    )

    assert user.role_codes == ["PARTNER_SALES"]


def test_partner_approval_timestamp_accepts_timezone_aware_values() -> None:
    approved_at_type = Partner.__table__.c.approved_at.type

    assert isinstance(approved_at_type, DateTime)
    assert approved_at_type.timezone is True

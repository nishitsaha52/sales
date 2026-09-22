from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.api.v1.endpoints.quotes import recalculate, snapshot
from app.domain.documents import can_access_document
from app.domain.workflows import (
    DEAL_TRANSITIONS,
    ORDER_TRANSITIONS,
    WorkflowError,
    ensure_transition,
    is_active_protection,
    validate_pipeline_change,
)
from app.models.content import DocumentVisibility
from app.models.sales import (
    DealApprovalStatus,
    OrderStatus,
    PipelineStage,
    Quote,
    QuoteItem,
)


def test_deal_submission_transition_is_allowed() -> None:
    ensure_transition(DealApprovalStatus.DRAFT, DealApprovalStatus.SUBMITTED, DEAL_TRANSITIONS)


def test_deal_cannot_skip_from_draft_to_approved() -> None:
    with pytest.raises(WorkflowError, match="Cannot transition"):
        ensure_transition(DealApprovalStatus.DRAFT, DealApprovalStatus.APPROVED, DEAL_TRANSITIONS)


def test_won_deal_requires_value_and_close_date() -> None:
    with pytest.raises(WorkflowError, match="contract value"):
        validate_pipeline_change(PipelineStage.WON)
    validate_pipeline_change(
        PipelineStage.WON,
        actual_contract_value=Decimal("1000"),
        actual_close_date=date.today(),
    )


def test_lost_deal_requires_reason() -> None:
    with pytest.raises(WorkflowError, match="reason"):
        validate_pipeline_change(PipelineStage.LOST, lost_reason=" ")


def test_protection_requires_approved_unexpired_deal() -> None:
    assert is_active_protection(DealApprovalStatus.APPROVED, datetime.now(UTC) + timedelta(days=1))
    assert not is_active_protection(
        DealApprovalStatus.REJECTED, datetime.now(UTC) + timedelta(days=1)
    )
    assert not is_active_protection(
        DealApprovalStatus.APPROVED, datetime.now(UTC) - timedelta(seconds=1)
    )


def test_document_visibility_rules_enforce_partner_scope() -> None:
    partner_id = uuid4()
    assert can_access_document(
        visibility=DocumentVisibility.ALL_PARTNERS,
        is_tcg=False,
        user_partner_id=partner_id,
        user_partner_type_id=None,
        user_partner_tier_id=None,
        document_partner_id=None,
        document_partner_type_id=None,
        document_partner_tier_id=None,
    )
    assert not can_access_document(
        visibility=DocumentVisibility.SPECIFIC_PARTNER,
        is_tcg=False,
        user_partner_id=partner_id,
        user_partner_type_id=None,
        user_partner_tier_id=None,
        document_partner_id=uuid4(),
        document_partner_type_id=None,
        document_partner_tier_id=None,
    )


def test_quote_total_and_snapshot_are_immutable_values() -> None:
    quote = Quote(
        reference="QTE-TEST",
        opportunity_id=uuid4(),
        partner_id=uuid4(),
        created_by_id=uuid4(),
        items=[],
    )
    quote.items.append(
        QuoteItem(
            sku_id=uuid4(),
            sku_code="SKU-1",
            sku_name="License",
            quantity=Decimal("2"),
            unit_price=Decimal("100"),
            discount_percentage=Decimal("10"),
            line_total=Decimal("180"),
            pricing_snapshot={"resolved_unit_price": "100.00"},
        )
    )
    recalculate(quote)
    frozen = snapshot(quote)
    assert quote.subtotal == Decimal("200.00")
    assert quote.discount_total == Decimal("20.00")
    assert quote.total == Decimal("180.00")
    assert frozen["total"] == "180.00"


def test_order_confirmation_is_not_reversible() -> None:
    ensure_transition(OrderStatus.SUBMITTED, OrderStatus.CONFIRMED, ORDER_TRANSITIONS)
    with pytest.raises(WorkflowError):
        ensure_transition(OrderStatus.CONFIRMED, OrderStatus.DRAFT, ORDER_TRANSITIONS)

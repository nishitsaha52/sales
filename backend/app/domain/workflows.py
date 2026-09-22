from datetime import UTC, datetime

from app.models.sales import DealApprovalStatus, MafStatus, OrderStatus, PipelineStage, QuoteStatus


class WorkflowError(ValueError):
    pass


DEAL_TRANSITIONS: dict[str, set[str]] = {
    DealApprovalStatus.DRAFT: {DealApprovalStatus.SUBMITTED},
    DealApprovalStatus.REJECTED: {DealApprovalStatus.SUBMITTED},
    DealApprovalStatus.SUBMITTED: {
        DealApprovalStatus.UNDER_REVIEW,
        DealApprovalStatus.APPROVED,
        DealApprovalStatus.REJECTED,
    },
    DealApprovalStatus.UNDER_REVIEW: {DealApprovalStatus.APPROVED, DealApprovalStatus.REJECTED},
    DealApprovalStatus.APPROVED: set(),
}

QUOTE_TRANSITIONS: dict[str, set[str]] = {
    QuoteStatus.DRAFT: {QuoteStatus.UNDER_REVIEW, QuoteStatus.FINAL, QuoteStatus.CANCELLED},
    QuoteStatus.UNDER_REVIEW: {QuoteStatus.DRAFT, QuoteStatus.FINAL, QuoteStatus.CANCELLED},
    QuoteStatus.FINAL: {
        QuoteStatus.DRAFT,
        QuoteStatus.ACCEPTED,
        QuoteStatus.EXPIRED,
        QuoteStatus.CANCELLED,
    },
    QuoteStatus.ACCEPTED: set(),
    QuoteStatus.EXPIRED: set(),
    QuoteStatus.CANCELLED: set(),
}

MAF_TRANSITIONS: dict[str, set[str]] = {
    MafStatus.DRAFT: {MafStatus.SUBMITTED},
    MafStatus.RETURNED_FOR_CORRECTION: {MafStatus.SUBMITTED},
    MafStatus.SUBMITTED: {
        MafStatus.UNDER_REVIEW,
        MafStatus.APPROVED,
        MafStatus.REJECTED,
        MafStatus.RETURNED_FOR_CORRECTION,
    },
    MafStatus.UNDER_REVIEW: {
        MafStatus.APPROVED,
        MafStatus.REJECTED,
        MafStatus.RETURNED_FOR_CORRECTION,
    },
    MafStatus.APPROVED: {MafStatus.ISSUED},
    MafStatus.ISSUED: {MafStatus.EXPIRED},
    MafStatus.REJECTED: set(),
    MafStatus.EXPIRED: set(),
}

ORDER_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.DRAFT: {OrderStatus.SUBMITTED, OrderStatus.CANCELLED},
    OrderStatus.RETURNED_FOR_CORRECTION: {OrderStatus.SUBMITTED, OrderStatus.CANCELLED},
    OrderStatus.SUBMITTED: {
        OrderStatus.UNDER_REVIEW,
        OrderStatus.CONFIRMED,
        OrderStatus.RETURNED_FOR_CORRECTION,
        OrderStatus.CANCELLED,
    },
    OrderStatus.UNDER_REVIEW: {
        OrderStatus.CONFIRMED,
        OrderStatus.RETURNED_FOR_CORRECTION,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {OrderStatus.PROVISIONING, OrderStatus.CANCELLED},
    OrderStatus.PROVISIONING: {OrderStatus.ACTIVE, OrderStatus.CANCELLED},
    OrderStatus.ACTIVE: set(),
    OrderStatus.CANCELLED: set(),
}


def ensure_transition(current: str, target: str, transitions: dict[str, set[str]]) -> None:
    if target not in transitions.get(current, set()):
        raise WorkflowError(f"Cannot transition from {current} to {target}")


def validate_pipeline_change(
    target: str,
    *,
    actual_contract_value: object | None = None,
    actual_close_date: object | None = None,
    lost_reason: str | None = None,
) -> None:
    if target not in PipelineStage:
        raise WorkflowError("Unknown pipeline stage")
    if target == PipelineStage.WON and (actual_contract_value is None or actual_close_date is None):
        raise WorkflowError("Won deals require actual contract value and close date")
    if target == PipelineStage.LOST and not (lost_reason or "").strip():
        raise WorkflowError("Lost deals require a reason")


def is_active_protection(status: str, protection_expires_at: datetime | None) -> bool:
    return (
        status == DealApprovalStatus.APPROVED
        and protection_expires_at is not None
        and protection_expires_at > datetime.now(UTC)
    )

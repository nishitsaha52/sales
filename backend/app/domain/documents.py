from app.models.content import DocumentVisibility


def can_access_document(
    *,
    visibility: str,
    is_tcg: bool,
    user_partner_id: object | None,
    user_partner_type_id: object | None,
    user_partner_tier_id: object | None,
    document_partner_id: object | None,
    document_partner_type_id: object | None,
    document_partner_tier_id: object | None,
) -> bool:
    if is_tcg:
        return True
    if user_partner_id is None or visibility == DocumentVisibility.TCG_INTERNAL:
        return False
    if visibility == DocumentVisibility.ALL_PARTNERS:
        return True
    if visibility == DocumentVisibility.SPECIFIC_PARTNER:
        return user_partner_id == document_partner_id
    if visibility == DocumentVisibility.PARTNER_TYPE:
        return user_partner_type_id == document_partner_type_id
    if visibility == DocumentVisibility.PARTNER_TIER:
        return user_partner_tier_id == document_partner_tier_id
    return False

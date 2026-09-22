from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    hashed = hash_password("a-secure-test-password")

    assert hashed != "a-secure-test-password"
    assert verify_password("a-secure-test-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_round_trip() -> None:
    token = create_access_token("user-id", {"roles": ["TCG_ADMIN"]})
    payload = decode_access_token(token)

    assert payload["sub"] == "user-id"
    assert payload["type"] == "access"
    assert payload["roles"] == ["TCG_ADMIN"]
    assert payload["jti"]

import pytest

from tet_engine.app.models import AdminRole, AdminUserCreate
from tet_engine.app.phase2.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    password = "strongpass123"
    password_hash = hash_password(password)
    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_jwt_create_and_decode():
    access = create_access_token(user_id="u1", email="a@b.com", role="super_admin")
    refresh = create_refresh_token(user_id="u1", email="a@b.com", role="super_admin")

    access_payload = decode_token(access)
    refresh_payload = decode_token(refresh)

    assert access_payload["sub"] == "u1"
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"


def test_admin_user_create_requires_min_password():
    with pytest.raises(Exception):
        AdminUserCreate(email="x@y.com", name="x", role=AdminRole.super_admin, password="short")

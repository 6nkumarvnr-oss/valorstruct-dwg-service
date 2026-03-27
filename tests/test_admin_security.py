import pytest

sqlalchemy = pytest.importorskip("sqlalchemy")

from tet_engine.app.models import AdminRole, AdminUserCreate
from tet_engine.app.phase2.auth import create_access_token, create_refresh_token
from tet_engine.app.services import authenticate_admin_access_token, create_admin_user, list_admin_users, storage


def test_admin_user_responses_are_sanitized():
    storage.admin_users.clear()
    user = create_admin_user(
        AdminUserCreate(
            email="admin@example.com",
            name="Admin",
            role=AdminRole.super_admin,
            password="supersecure",
        )
    )
    assert "password_hash" not in user

    users = list_admin_users()
    assert len(users) == 1
    assert "password_hash" not in users[0]


def test_admin_access_token_authentication():
    storage.admin_users.clear()
    seed_user = create_admin_user(
        AdminUserCreate(
            email="seed-admin@example.com",
            name="Seed Admin",
            role=AdminRole.super_admin,
            password="seedpassword",
        )
    )
    access_token = create_access_token(
        user_id=seed_user["id"],
        email=seed_user["email"],
        role=seed_user["role"],
    )
    authorized = authenticate_admin_access_token(access_token)
    assert authorized["id"] == seed_user["id"]

    refresh_token = create_refresh_token(
        user_id=seed_user["id"],
        email=seed_user["email"],
        role=seed_user["role"],
    )
    with pytest.raises(ValueError):
        authenticate_admin_access_token(refresh_token)

import pytest

from src.auth.models import Permission
from src.session import AuthenticationService


def test_authenticate_reetha_user():
    session = AuthenticationService().authenticate(
        "reetha-marketing"
    )

    assert session.authenticated is True
    assert session.user_id == "reetha-marketing"
    assert session.tenant_id == "reetha"
    assert session.email
    assert session.display_name


def test_authenticated_session_resolves_role():
    session = AuthenticationService().authenticate(
        "reetha-director"
    )

    assert session.tenant_id == "reetha"
    assert session.role.value == "director"


def test_tenant_access_is_allowed_for_own_tenant():
    service = AuthenticationService()

    session = service.authenticate("reetha-marketing")

    assert service.authorize_tenant_access(
        session,
        "reetha",
    ) is True


def test_cross_tenant_access_is_blocked():
    service = AuthenticationService()

    session = service.authenticate("reetha-marketing")

    with pytest.raises(
        PermissionError,
        match="another tenant",
    ):
        service.authorize_tenant_access(
            session,
            "demo",
        )


def test_permission_is_checked_through_existing_rbac():
    service = AuthenticationService()

    session = service.authenticate("reetha-marketing")

    assert service.authorize_permission(
        session,
        Permission.VIEW_LEADS,
    ) is True


def test_unauthorized_permission_is_blocked():
    service = AuthenticationService()

    session = service.authenticate("reetha-sales")

    with pytest.raises(PermissionError):
        service.authorize_permission(
            session,
            Permission.GENERATE_AI_RECOMMENDATION,
        )

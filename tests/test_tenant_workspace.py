import pytest

from src.auth.models import Permission
from src.session import AuthenticationService
from src.workspace import TenantWorkspaceService


def test_reetha_workspace_is_resolved_from_session():
    auth = AuthenticationService()
    service = TenantWorkspaceService(auth)

    session = auth.authenticate("reetha-marketing")
    workspace = service.resolve(session)

    assert workspace.tenant_id == "reetha"
    assert workspace.tenant_name == "Reetha IT Hub"
    assert workspace.user_id == "reetha-marketing"
    assert workspace.authenticated is True


def test_workspace_role_comes_from_authenticated_user():
    auth = AuthenticationService()
    service = TenantWorkspaceService(auth)

    session = auth.authenticate("reetha-director")
    workspace = service.resolve(session)

    assert workspace.role.value == "director"


def test_inactive_or_invalid_tenant_cannot_be_resolved():
    auth = AuthenticationService()
    service = TenantWorkspaceService(auth)

    session = auth.authenticate("reetha-marketing")

    with pytest.raises(
        PermissionError,
        match="another tenant",
    ):
        auth.authorize_tenant_access(
            session,
            "demo",
        )


def test_workspace_permission_uses_existing_rbac():
    auth = AuthenticationService()
    service = TenantWorkspaceService(auth)

    session = auth.authenticate("reetha-marketing")
    workspace = service.resolve(session)

    assert service.require_permission(
        workspace,
        Permission.VIEW_LEADS,
    ) is True


def test_workspace_cannot_bypass_permission():
    auth = AuthenticationService()
    service = TenantWorkspaceService(auth)

    session = auth.authenticate("reetha-sales")
    workspace = service.resolve(session)

    with pytest.raises(PermissionError):
        service.require_permission(
            workspace,
            Permission.GENERATE_AI_RECOMMENDATION,
        )

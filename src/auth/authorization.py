from .models import Permission, User
from .policy import has_permission


class AuthorizationError(PermissionError):
    """Raised when a user is not authorized to perform an action."""


def authorize(
    user: User,
    permission: Permission,
    resource_tenant_id: str,
) -> None:
    """Authorize a user against both RBAC and tenant boundaries."""

    if not user.active:
        raise AuthorizationError("User is inactive.")

    if user.tenant_id != resource_tenant_id:
        raise AuthorizationError(
            "Tenant access denied."
        )

    if not has_permission(user.role, permission):
        raise AuthorizationError(
            f"Permission denied: {permission.value}"
        )

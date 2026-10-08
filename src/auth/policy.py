from .models import Permission, Role


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),

    Role.DIRECTOR: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_LEADS,
            Permission.MANAGE_CAMPAIGNS,
            Permission.VIEW_ANALYTICS,
            Permission.GENERATE_AI_RECOMMENDATION,
            Permission.APPROVE_AI_ACTION,
            Permission.EXECUTE_CAMPAIGN,
        }
    ),

    Role.MARKETING_MANAGER: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_LEADS,
            Permission.MANAGE_CAMPAIGNS,
            Permission.VIEW_ANALYTICS,
            Permission.GENERATE_AI_RECOMMENDATION,
            Permission.APPROVE_AI_ACTION,
        }
    ),

    Role.SALES_USER: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_LEADS,
            Permission.VIEW_ANALYTICS,
        }
    ),

    Role.ANALYST: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
        }
    ),

    Role.VIEWER: frozenset(
        {
            Permission.VIEW_DASHBOARD,
        }
    ),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())

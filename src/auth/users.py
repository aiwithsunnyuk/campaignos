from .models import Role, User


USERS: dict[str, User] = {
    "demo-admin": User(
        user_id="demo-admin",
        email="demo-admin@campaignos.local",
        display_name="CampaignOS Demo Admin",
        tenant_id="demo",
        role=Role.ADMIN,
    ),
    "reetha-director": User(
        user_id="reetha-director",
        email="director@reetha.local",
        display_name="Reetha Director",
        tenant_id="reetha",
        role=Role.DIRECTOR,
    ),
    "reetha-marketing": User(
        user_id="reetha-marketing",
        email="marketing@reetha.local",
        display_name="Reetha Marketing Manager",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    ),
    "reetha-sales": User(
        user_id="reetha-sales",
        email="sales@reetha.local",
        display_name="Reetha Sales User",
        tenant_id="reetha",
        role=Role.SALES_USER,
    ),
}


def get_user(user_id: str) -> User:
    try:
        return USERS[user_id]
    except KeyError as exc:
        raise ValueError(f"Unknown CampaignOS user: {user_id}") from exc


def list_users() -> list[User]:
    return list(USERS.values())

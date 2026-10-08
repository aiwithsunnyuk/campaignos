from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    DIRECTOR = "director"
    MARKETING_MANAGER = "marketing_manager"
    SALES_USER = "sales_user"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_LEADS = "view_leads"
    MANAGE_CAMPAIGNS = "manage_campaigns"
    VIEW_ANALYTICS = "view_analytics"
    GENERATE_AI_RECOMMENDATION = "generate_ai_recommendation"
    APPROVE_AI_ACTION = "approve_ai_action"
    EXECUTE_CAMPAIGN = "execute_campaign"
    MANAGE_USERS = "manage_users"


@dataclass(frozen=True)
class User:
    user_id: str
    email: str
    display_name: str
    tenant_id: str
    role: Role
    active: bool = True

import pytest

from src.ai_governance import LeadActionGovernanceService
from src.auth.authorization import AuthorizationError
from src.auth.models import Role, User
from src.next_best_action.models import NextBestAction


def make_action(tenant_id="reetha"):
    return NextBestAction(
        lead_id="LEAD-0001",
        tenant_id=tenant_id,
        action_type="registration_follow_up",
        priority="high",
        recommendation="Prioritize registration conversion",
        reason="Lead is strongly engaged but has not registered.",
        evidence=(
            "5 engagements",
            "no registration recorded",
        ),
    )


def test_marketing_manager_can_create_governed_action():
    user = User(
        user_id="reetha-marketing",
        email="marketing@reetha.example",
        display_name="Reetha Marketing",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    governed = LeadActionGovernanceService().create_governed_action(
        user=user,
        action=make_action(),
    )

    assert governed.tenant_id == "reetha"
    assert governed.lead_id == "LEAD-0001"
    assert governed.action_type == "registration_follow_up"
    assert governed.status == "pending_approval"


def test_cross_tenant_governed_action_is_denied():
    user = User(
        user_id="demo-user",
        email="demo@example.com",
        display_name="Demo User",
        tenant_id="demo",
        role=Role.MARKETING_MANAGER,
    )

    with pytest.raises(AuthorizationError):
        LeadActionGovernanceService().create_governed_action(
            user=user,
            action=make_action(),
        )


def test_viewer_cannot_create_governed_action():
    user = User(
        user_id="reetha-viewer",
        email="viewer@reetha.example",
        display_name="Reetha Viewer",
        tenant_id="reetha",
        role=Role.VIEWER,
    )

    with pytest.raises(AuthorizationError):
        LeadActionGovernanceService().create_governed_action(
            user=user,
            action=make_action(),
        )


def test_marketing_manager_can_create_approval_request():
    user = User(
        user_id="reetha-marketing",
        email="marketing@reetha.example",
        display_name="Reetha Marketing",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    request = LeadActionGovernanceService().create_approval_request(
        user=user,
        action=make_action(),
    )

    assert request.tenant_id == "reetha"
    assert request.lead_id == "LEAD-0001"
    assert request.status == "pending"

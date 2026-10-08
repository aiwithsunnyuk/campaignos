import pytest

from src.auth.authorization import AuthorizationError
from src.auth.models import Role, User
from src.lead_360.models import Lead360
from src.next_best_action import LeadNextBestActionService


def make_lead(tenant_id="reetha"):
    return Lead360(
        lead_id="LEAD-0001",
        tenant_id=tenant_id,
        first_name="Test",
        last_name="Lead",
        email="test.lead@reetha.example",
        phone="+919999999999",
        source="website",
        lifecycle_stage="lead",
        interest="technology",
        course_id="COURSE-0001",
        lead_score=80,
        total_engagements=5,
        unique_campaigns=2,
        unique_courses=1,
        last_engagement_at="2026-10-09T00:00:00",
        registration_count=0,
        enrollment_count=0,
        engagement_channels=("email", "web"),
        engagement_event_types=("click", "page_view"),
    )


def test_marketing_manager_can_generate_lead_nba():
    user = User(
        user_id="reetha-marketing",
        email="marketing@reetha.example",
        display_name="Reetha Marketing",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    action = LeadNextBestActionService().recommend(
        user=user,
        tenant_id="reetha",
        lead=make_lead(),
    )

    assert action.lead_id == "LEAD-0001"
    assert action.tenant_id == "reetha"
    assert action.action_type == "registration_follow_up"
    assert action.priority == "high"


def test_cross_tenant_lead_nba_is_denied():
    user = User(
        user_id="demo-user",
        email="demo@example.com",
        display_name="Demo User",
        tenant_id="demo",
        role=Role.MARKETING_MANAGER,
    )

    with pytest.raises(AuthorizationError):
        LeadNextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead=make_lead(),
        )


def test_viewer_cannot_generate_lead_nba():
    user = User(
        user_id="reetha-viewer",
        email="viewer@reetha.example",
        display_name="Reetha Viewer",
        tenant_id="reetha",
        role=Role.VIEWER,
    )

    with pytest.raises(AuthorizationError):
        LeadNextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead=make_lead(),
        )


def test_lead_tenant_mismatch_is_denied():
    user = User(
        user_id="reetha-marketing",
        email="marketing@reetha.example",
        display_name="Reetha Marketing",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    with pytest.raises(ValueError, match="Lead tenant"):
        LeadNextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead=make_lead(tenant_id="demo"),
        )

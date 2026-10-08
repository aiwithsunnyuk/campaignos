import pytest

from src.auth.authorization import AuthorizationError
from src.auth.models import Role, User
from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.lead_360.builder import Lead360Builder
from src.marketing_intelligence import MarketingIntelligenceService


def _reetha_records():
    tenant_id = "reetha"

    leads = CSVLeadAdapter(
        tenant_id=tenant_id,
        path="data/reetha/leads.csv",
    ).load()

    engagements = CSVEngagementAdapter(
        tenant_id=tenant_id,
        path="data/reetha/engagements.csv",
    ).load()

    registrations = CSVRegistrationAdapter(
        tenant_id=tenant_id,
        path="data/reetha/registrations.csv",
    ).load()

    enrollments = CSVEnrollmentAdapter(
        tenant_id=tenant_id,
        path="data/reetha/enrollments.csv",
    ).load()

    return Lead360Builder(
        tenant_id=tenant_id,
    ).build(
        leads=leads,
        engagements=engagements,
        registrations=registrations,
        enrollments=enrollments,
    )


def _user(
    tenant_id: str = "reetha",
    role: Role = Role.ANALYST,
) -> User:
    return User(
        user_id="user-001",
        email="analyst@reetha.example",
        display_name="Reetha Analyst",
        tenant_id=tenant_id,
        role=role,
    )


def test_reetha_user_can_view_marketing_intelligence():
    records = _reetha_records()

    intelligence = MarketingIntelligenceService().get_intelligence(
        user=_user(),
        tenant_id="reetha",
        records=records,
    )

    assert intelligence.tenant_id == "reetha"
    assert intelligence.total_leads == 250
    assert intelligence.engaged_leads == 249
    assert intelligence.registered_leads == 78
    assert intelligence.enrolled_leads == 47
    assert intelligence.funnel_bottleneck == "registration"


def test_cross_tenant_access_is_denied():
    records = _reetha_records()

    with pytest.raises(AuthorizationError, match="Tenant access denied"):
        MarketingIntelligenceService().get_intelligence(
            user=_user(tenant_id="demo"),
            tenant_id="reetha",
            records=records,
        )


def test_inactive_user_is_denied():
    records = _reetha_records()

    user = User(
        user_id="inactive-001",
        email="inactive@reetha.example",
        display_name="Inactive User",
        tenant_id="reetha",
        role=Role.ANALYST,
        active=False,
    )

    with pytest.raises(AuthorizationError, match="User is inactive"):
        MarketingIntelligenceService().get_intelligence(
            user=user,
            tenant_id="reetha",
            records=records,
        )


def test_viewer_without_analytics_permission_is_denied():
    records = _reetha_records()

    with pytest.raises(
        AuthorizationError,
        match="Permission denied: view_analytics",
    ):
        MarketingIntelligenceService().get_intelligence(
            user=_user(role=Role.VIEWER),
            tenant_id="reetha",
            records=records,
        )

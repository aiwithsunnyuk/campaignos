import pytest

from src.auth.authorization import AuthorizationError
from src.auth.models import Role, User
from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.lead_360 import Lead360Service


def build_reetha_records():
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

    return leads, engagements, registrations, enrollments


def test_reetha_sales_user_can_view_lead_360():
    user = User(
        user_id="reetha-sales",
        email="sales@reetha.example",
        display_name="Reetha Sales",
        tenant_id="reetha",
        role=Role.SALES_USER,
    )

    records = build_reetha_records()

    lead = Lead360Service().get_lead(
        user=user,
        tenant_id="reetha",
        lead_id="LEAD-0001",
        leads=records[0],
        engagements=records[1],
        registrations=records[2],
        enrollments=records[3],
    )

    assert lead.tenant_id == "reetha"
    assert lead.lead_id == "LEAD-0001"


def test_cross_tenant_lead_360_is_denied():
    user = User(
        user_id="demo-user",
        email="demo@example.com",
        display_name="Demo User",
        tenant_id="demo",
        role=Role.SALES_USER,
    )

    records = build_reetha_records()

    with pytest.raises(AuthorizationError):
        Lead360Service().get_lead(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-0001",
            leads=records[0],
            engagements=records[1],
            registrations=records[2],
            enrollments=records[3],
        )


def test_viewer_can_view_lead_360():
    user = User(
        user_id="reetha-viewer",
        email="viewer@reetha.example",
        display_name="Reetha Viewer",
        tenant_id="reetha",
        role=Role.VIEWER,
    )

    records = build_reetha_records()

    with pytest.raises(AuthorizationError):
        Lead360Service().get_lead(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-0001",
            leads=records[0],
            engagements=records[1],
            registrations=records[2],
            enrollments=records[3],
        )


def test_unknown_lead_is_rejected():
    user = User(
        user_id="reetha-sales",
        email="sales@reetha.example",
        display_name="Reetha Sales",
        tenant_id="reetha",
        role=Role.SALES_USER,
    )

    records = build_reetha_records()

    with pytest.raises(ValueError, match="was not found"):
        Lead360Service().get_lead(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-9999",
            leads=records[0],
            engagements=records[1],
            registrations=records[2],
            enrollments=records[3],
        )

from dataclasses import replace

import pytest

from src.auth.authorization import AuthorizationError
from src.auth.models import Role, User
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.next_best_action import NextBestActionService
from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.lead_360.builder import Lead360Builder


def build_reetha_snapshot():
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

    records = Lead360Builder(
        tenant_id=tenant_id,
    ).build(
        leads=leads,
        engagements=engagements,
        registrations=registrations,
        enrollments=enrollments,
    )

    return GTMIntelligenceSnapshotBuilder(
        tenant_id=tenant_id,
    ).build(records)


def test_reetha_marketing_manager_can_generate_nba():
    user = User(
        user_id="reetha-marketing",
        email="marketing@reetha.example",
        display_name="Reetha Marketing",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    snapshot = build_reetha_snapshot()

    action = NextBestActionService().recommend(
        user=user,
        tenant_id="reetha",
        lead_id="LEAD-0001",
        snapshot=snapshot,
    )

    assert action.tenant_id == "reetha"
    assert action.action_type == "registration_follow_up"
    assert action.priority == "high"
    assert action.recommendation == "Prioritize registration conversion"


def test_cross_tenant_nba_is_denied():
    user = User(
        user_id="demo-user",
        email="demo@example.com",
        display_name="Demo User",
        tenant_id="demo",
        role=Role.MARKETING_MANAGER,
    )

    snapshot = build_reetha_snapshot()

    with pytest.raises(AuthorizationError):
        NextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-0001",
            snapshot=snapshot,
        )


def test_viewer_cannot_generate_nba():
    user = User(
        user_id="reetha-viewer",
        email="viewer@reetha.example",
        display_name="Reetha Viewer",
        tenant_id="reetha",
        role=Role.VIEWER,
    )

    snapshot = build_reetha_snapshot()

    with pytest.raises(AuthorizationError):
        NextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-0001",
            snapshot=snapshot,
        )


def test_inactive_user_cannot_generate_nba():
    user = User(
        user_id="reetha-inactive",
        email="inactive@reetha.example",
        display_name="Inactive User",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
        active=False,
    )

    snapshot = build_reetha_snapshot()

    with pytest.raises(AuthorizationError):
        NextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-0001",
            snapshot=snapshot,
        )


def test_snapshot_tenant_mismatch_is_denied():
    user = User(
        user_id="reetha-marketing",
        email="marketing@reetha.example",
        display_name="Reetha Marketing",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    snapshot = build_reetha_snapshot()
    mismatched_snapshot = replace(snapshot, tenant_id="demo")

    with pytest.raises(ValueError, match="Snapshot tenant does not match"):
        NextBestActionService().recommend(
            user=user,
            tenant_id="reetha",
            lead_id="LEAD-0001",
            snapshot=mismatched_snapshot,
        )

from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.gtm_intelligence.signals import GTMExplainableSignalBuilder
from src.lead_360.builder import Lead360Builder
from src.next_best_action import NextBestActionEngine
from src.ai_governance import (
    ActionLifecycleEngine,
    GovernedActionFactory,
)


def test_reetha_nba_becomes_governed_action():
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

    lead_360_records = Lead360Builder(
        tenant_id=tenant_id
    ).build(
        leads=leads,
        engagements=engagements,
        registrations=registrations,
        enrollments=enrollments,
    )

    snapshot = GTMIntelligenceSnapshotBuilder(
        tenant_id=tenant_id
    ).build(lead_360_records)

    signals = GTMExplainableSignalBuilder(snapshot).build()

    nba = NextBestActionEngine().recommend(
        lead_id="LEAD-0001",
        tenant_id=tenant_id,
        signals=signals,
    )

    governed = GovernedActionFactory().create(
        action=nba,
        action_id="ACT-REETHA-0001",
    )

    pending = ActionLifecycleEngine().submit_for_approval(
        governed
    )

    assert nba.tenant_id == "reetha"
    assert nba.action_type == "registration_follow_up"

    assert governed.tenant_id == "reetha"
    assert governed.lead_id == "LEAD-0001"
    assert governed.status == "recommended"

    assert pending.status == "pending_approval"
    assert pending.tenant_id == "reetha"
    assert pending.action_type == nba.action_type

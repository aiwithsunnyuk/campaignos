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
from src.execution import DryRunExecutionAdapter


def test_reetha_governed_action_reaches_dry_run_execution():
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
        action_id="ACT-REETHA-EXEC-0001",
    )

    lifecycle = ActionLifecycleEngine()

    pending = lifecycle.submit_for_approval(governed)

    approved = lifecycle.approve(
        pending,
        approved_by="reetha-director",
    )

    ready = lifecycle.mark_ready_for_execution(
        approved
    )

    result = DryRunExecutionAdapter().execute(
        action=ready,
        execution_id="EXE-REETHA-0001",
    )

    assert result.tenant_id == "reetha"
    assert result.action_id == "ACT-REETHA-EXEC-0001"
    assert result.status == "dry_run"
    assert result.action_type == "registration_follow_up"
    assert "No external system was contacted." in result.message

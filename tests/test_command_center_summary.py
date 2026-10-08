from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.lead_360.builder import Lead360Builder
from src.marketing_intelligence import (
    CommandCenterSummaryBuilder,
    MarketingIntelligenceEngine,
)


def test_reetha_command_center_summary():
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

    snapshot = GTMIntelligenceSnapshotBuilder(
        tenant_id=tenant_id,
    ).build(records)

    intelligence = MarketingIntelligenceEngine().build(snapshot)

    summary = CommandCenterSummaryBuilder().build(intelligence)

    assert summary.tenant_id == "reetha"

    assert len(summary.kpis) == 8
    assert len(summary.intelligence_feed) == 2

    assert summary.kpis[0].key == "total_leads"
    assert summary.kpis[0].value == 250

    assert summary.intelligence_feed[0].priority == "critical"
    assert summary.intelligence_feed[0].title == (
        "Registration Conversion Bottleneck"
    )

    assert summary.intelligence_feed[0].value == "31.33%"

    assert "reetha" in summary.headline
    assert "registration" in summary.headline.lower()

from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.marketing_intelligence import MarketingIntelligenceEngine
from src.lead_360.builder import Lead360Builder


def test_reetha_marketing_intelligence():
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
        tenant_id=tenant_id,
    ).build(
        leads=leads,
        engagements=engagements,
        registrations=registrations,
        enrollments=enrollments,
    )

    snapshot = GTMIntelligenceSnapshotBuilder(
        tenant_id=tenant_id,
    ).build(lead_360_records)

    intelligence = MarketingIntelligenceEngine().build(snapshot)

    assert intelligence.tenant_id == "reetha"
    assert intelligence.total_leads == 250
    assert intelligence.engaged_leads == 249
    assert intelligence.registered_leads == 78
    assert intelligence.enrolled_leads == 47

    assert intelligence.engagement_rate == 99.6
    assert intelligence.registration_rate == 31.33
    assert intelligence.enrollment_rate == 60.26

    assert intelligence.funnel_bottleneck == "registration"

    assert len(intelligence.top_channels) > 0
    assert len(intelligence.top_event_types) > 0

    assert "reetha" in intelligence.headline
    assert "registration" in intelligence.headline.lower()

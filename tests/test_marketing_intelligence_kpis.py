from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.lead_360.builder import Lead360Builder
from src.marketing_intelligence import (
    MarketingIntelligenceEngine,
    MarketingIntelligenceKPIBuilder,
)


def test_reetha_marketing_intelligence_kpis():
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

    kpis = MarketingIntelligenceKPIBuilder().build(intelligence)

    assert len(kpis) == 8

    by_key = {kpi.key: kpi for kpi in kpis}

    assert by_key["total_leads"].value == 250
    assert by_key["engaged_leads"].value == 249
    assert by_key["registered_leads"].value == 78
    assert by_key["enrolled_leads"].value == 47

    assert by_key["engagement_rate"].value == 99.6
    assert by_key["registration_rate"].value == 31.33
    assert by_key["enrollment_rate"].value == 60.26

    assert by_key["funnel_bottleneck"].value == "registration"
    assert by_key["funnel_bottleneck"].priority == "critical"
    assert by_key["registration_rate"].priority == "critical"

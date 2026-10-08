from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.lead_360.builder import Lead360Builder
from src.marketing_intelligence import (
    MarketingIntelligenceCardBuilder,
    MarketingIntelligenceEngine,
)


def test_reetha_prioritized_intelligence_cards():
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

    cards = MarketingIntelligenceCardBuilder().build(intelligence)

    assert len(cards) == 2

    bottleneck = cards[0]

    assert bottleneck.card_id == "FUNNEL-REGISTRATION"
    assert bottleneck.tenant_id == "reetha"
    assert bottleneck.priority == "critical"
    assert bottleneck.metric == "Registration Conversion"
    assert bottleneck.value == "31.33%"
    assert "249 engaged leads" in bottleneck.evidence
    assert "78 registered leads" in bottleneck.evidence
    assert "Prioritize registration conversion" in bottleneck.recommendation

    engagement = cards[1]

    assert engagement.card_id == "ENGAGEMENT-COVERAGE"
    assert engagement.priority == "low"
    assert engagement.value == "99.60%"

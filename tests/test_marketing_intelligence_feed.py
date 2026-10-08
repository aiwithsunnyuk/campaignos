from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.lead_360.builder import Lead360Builder
from src.marketing_intelligence import (
    MarketingIntelligenceCardBuilder,
    MarketingIntelligenceEngine,
    MarketingIntelligenceFeedBuilder,
)


def test_reetha_marketing_intelligence_feed_is_prioritized():
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

    feed = MarketingIntelligenceFeedBuilder().build(cards)

    assert len(feed) == 2

    first = feed[0]
    second = feed[1]

    assert first.feed_id == "FEED-FUNNEL-REGISTRATION"
    assert first.tenant_id == "reetha"
    assert first.priority == "critical"
    assert first.title == "Registration Conversion Bottleneck"
    assert first.value == "31.33%"
    assert "249 engaged leads" in first.evidence

    assert second.feed_id == "FEED-ENGAGEMENT-COVERAGE"
    assert second.priority == "low"

    assert (
        first.priority == "critical"
        and second.priority == "low"
    )

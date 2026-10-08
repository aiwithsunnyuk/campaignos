from src.data_adapters import (
    CSVLeadAdapter,
    CSVEngagementAdapter,
    CSVRegistrationAdapter,
    CSVEnrollmentAdapter,
)
from src.lead_360 import Lead360Builder
from src.gtm_intelligence import GTMIntelligenceSnapshotBuilder


def test_reetha_gtm_snapshot_from_full_dataset():
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
    ).build(
        records=records,
        as_of="2026-10-08T00:00:00",
    )

    assert len(leads) == 250
    assert len(engagements) == 1500
    assert len(registrations) == 100
    assert len(enrollments) == 50
    assert len(records) == 250

    assert snapshot.tenant_id == "reetha"
    assert snapshot.total_leads == 250
    assert snapshot.leads_with_engagement == 249
    assert snapshot.leads_with_registration == 78
    assert snapshot.leads_with_enrollment == 47

    assert snapshot.funnel_progression == (
        ("Lead", 250),
        ("Engaged", 249),
        ("Registered", 78),
        ("Enrolled", 47),
    )

    assert len(snapshot.top_engaged_leads) > 0
    assert len(snapshot.channel_coverage) > 0
    assert len(snapshot.event_type_coverage) > 0

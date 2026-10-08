from pathlib import Path

from src.data_adapters import (
    CSVLeadAdapter,
    CSVCampaignAdapter,
    CSVRegistrationAdapter,
    CSVEnrollmentAdapter,
    CSVEngagementAdapter,
)
from src.gtm_intelligence import (
    GTMIntelligenceSnapshotBuilder,
    GTMExplainableSignalBuilder,
)
from src.lead_360.builder import Lead360Builder


def test_reetha_explainable_signals_from_full_dataset():
    tenant_id = "reetha"

    leads = CSVLeadAdapter(
        tenant_id=tenant_id,
        path="data/reetha/leads.csv",
    ).load()

    campaigns = CSVCampaignAdapter(
        tenant_id=tenant_id,
        path="data/reetha/campaigns.csv",
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

    lead360_records = Lead360Builder(
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
        records=lead360_records,
        as_of="2026-10-08T00:00:00",
    )

    signals = GTMExplainableSignalBuilder(snapshot).build()

    assert len(signals) == 6

    signal_ids = {signal.signal_id for signal in signals}

    assert signal_ids == {
        "ENGAGEMENT_COVERAGE",
        "REGISTRATION_CONVERSION",
        "ENROLLMENT_CONVERSION",
        "ENGAGEMENT_RECENCY",
        "CHANNEL_BREADTH",
        "FUNNEL_BOTTLENECK",
    }

    engagement = next(
        signal for signal in signals
        if signal.signal_id == "ENGAGEMENT_COVERAGE"
    )

    assert engagement.value == "99.6%"
    assert engagement.level == "strong"

    registration = next(
        signal for signal in signals
        if signal.signal_id == "REGISTRATION_CONVERSION"
    )

    assert registration.value == "31.2%"
    assert registration.level == "moderate"

    enrollment = next(
        signal for signal in signals
        if signal.signal_id == "ENROLLMENT_CONVERSION"
    )

    assert enrollment.value == "18.8%"

    funnel = next(
        signal for signal in signals
        if signal.signal_id == "FUNNEL_BOTTLENECK"
    )

    assert funnel.value == "registration"

    assert all(signal.evidence for signal in signals)

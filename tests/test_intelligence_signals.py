from src.lead_360.models import Lead360
from src.lead_360.signal_builder import IntelligenceSignalBuilder


def make_lead(
    *,
    total_engagements=0,
    unique_campaigns=0,
    unique_courses=0,
    last_engagement_at=None,
    registration_count=0,
    enrollment_count=0,
):
    return Lead360(
        lead_id="LEAD-TEST",
        tenant_id="reetha",
        first_name="Test",
        last_name="Lead",
        email="test@example.com",
        phone="9000000000",
        source="LinkedIn",
        lifecycle_stage="qualified",
        interest="CRS-001",
        course_id="CRS-001",
        lead_score=50.0,
        total_engagements=total_engagements,
        unique_campaigns=unique_campaigns,
        unique_courses=unique_courses,
        last_engagement_at=last_engagement_at,
        registration_count=registration_count,
        enrollment_count=enrollment_count,
        engagement_channels=(),
        engagement_event_types=(),
    )


def test_new_lead_has_cold_behavioral_signals():
    lead = make_lead()

    signals = IntelligenceSignalBuilder().build(
        lead,
        as_of="2026-10-08T00:00:00",
    )

    assert signals.engagement_intensity == "none"
    assert signals.campaign_breadth == "none"
    assert signals.course_breadth == "none"
    assert signals.recency == "no_activity"
    assert signals.registration_signal == "not_registered"
    assert signals.enrollment_signal == "not_enrolled"
    assert signals.funnel_progression == "new"


def test_highly_engaged_lead_gets_strong_behavioral_signals():
    lead = make_lead(
        total_engagements=14,
        unique_campaigns=10,
        unique_courses=8,
        last_engagement_at="2026-10-05T00:00:00",
    )

    signals = IntelligenceSignalBuilder().build(
        lead,
        as_of="2026-10-08T00:00:00",
    )

    assert signals.engagement_intensity == "very_high"
    assert signals.campaign_breadth == "very_broad"
    assert signals.course_breadth == "very_broad"
    assert signals.recency == "very_recent"
    assert signals.funnel_progression == "engaged"


def test_registered_lead_progresses_beyond_engagement():
    lead = make_lead(
        total_engagements=8,
        unique_campaigns=4,
        unique_courses=3,
        last_engagement_at="2026-09-20T00:00:00",
        registration_count=1,
    )

    signals = IntelligenceSignalBuilder().build(
        lead,
        as_of="2026-10-08T00:00:00",
    )

    assert signals.registration_signal == "registered"
    assert signals.enrollment_signal == "not_enrolled"
    assert signals.funnel_progression == "registered"


def test_enrolled_lead_reaches_enrollment_stage():
    lead = make_lead(
        total_engagements=12,
        unique_campaigns=7,
        unique_courses=5,
        last_engagement_at="2026-10-01T00:00:00",
        registration_count=1,
        enrollment_count=1,
    )

    signals = IntelligenceSignalBuilder().build(
        lead,
        as_of="2026-10-08T00:00:00",
    )

    assert signals.registration_signal == "registered"
    assert signals.enrollment_signal == "enrolled"
    assert signals.funnel_progression == "enrolled"


def test_stale_engagement_is_explicitly_identified():
    lead = make_lead(
        total_engagements=4,
        unique_campaigns=2,
        unique_courses=2,
        last_engagement_at="2026-05-01T00:00:00",
    )

    signals = IntelligenceSignalBuilder().build(
        lead,
        as_of="2026-10-08T00:00:00",
    )

    assert signals.recency == "stale"

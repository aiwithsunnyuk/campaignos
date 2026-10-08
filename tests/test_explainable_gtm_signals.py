from src.gtm_intelligence.models import GTMIntelligenceSnapshot
from src.gtm_intelligence.signals import GTMExplainableSignalBuilder


def make_snapshot() -> GTMIntelligenceSnapshot:
    return GTMIntelligenceSnapshot(
        tenant_id="reetha",
        total_leads=250,
        leads_with_engagement=249,
        leads_with_registration=78,
        leads_with_enrollment=47,
        engagement_intensity_distribution=(
            ("high", 65),
            ("low", 105),
            ("medium", 79),
        ),
        campaign_breadth_distribution=(
            (1, 1),
            (2, 21),
            (3, 27),
            (4, 43),
            (5, 46),
        ),
        course_breadth_distribution=(
            (1, 2),
            (2, 5),
            (3, 11),
            (4, 45),
            (5, 49),
        ),
        recency_distribution=(
            ("aging", 105),
            ("never", 1),
            ("recent", 112),
            ("stale", 32),
        ),
        top_engaged_leads=(
            ("LEAD-0081", "Aditya Patel", 14),
            ("LEAD-0118", "Meera Sharma", 14),
        ),
        channel_coverage=(
            ("Email", 164),
            ("Google Ads", 132),
            ("Instagram", 152),
            ("LinkedIn", 133),
            ("Meta", 149),
            ("Organic Search", 146),
            ("WhatsApp", 137),
        ),
        event_type_coverage=(
            ("ad_click", 112),
            ("course_page_view", 119),
            ("demo_requested", 121),
            ("email_clicked", 121),
            ("form_started", 106),
            ("form_submitted", 111),
            ("landing_page_view", 118),
            ("webinar_registered", 114),
            ("whatsapp_message", 112),
        ),
        funnel_progression=(
            ("Lead", 250),
            ("Engaged", 249),
            ("Registered", 78),
            ("Enrolled", 47),
        ),
    )


def test_builds_explainable_signals():
    signals = GTMExplainableSignalBuilder(make_snapshot()).build()

    assert len(signals) == 6
    assert all(signal.signal_id for signal in signals)
    assert all(signal.evidence for signal in signals)


def test_engagement_signal_is_strong():
    signals = GTMExplainableSignalBuilder(make_snapshot()).build()

    signal = next(
        item for item in signals
        if item.signal_id == "ENGAGEMENT_COVERAGE"
    )

    assert signal.level == "strong"
    assert signal.value == "99.6%"
    assert "249 of 250" in signal.evidence


def test_registration_signal_is_moderate():
    signals = GTMExplainableSignalBuilder(make_snapshot()).build()

    signal = next(
        item for item in signals
        if item.signal_id == "REGISTRATION_CONVERSION"
    )

    assert signal.level == "moderate"
    assert signal.value == "31.2%"


def test_signals_do_not_change_snapshot():
    snapshot = make_snapshot()
    before = snapshot

    GTMExplainableSignalBuilder(snapshot).build()

    assert snapshot == before

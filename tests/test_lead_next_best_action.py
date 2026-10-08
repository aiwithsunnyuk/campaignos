from src.lead_360.models import Lead360
from src.next_best_action.lead_engine import LeadNextBestActionEngine


def make_lead(
    *,
    lead_id="LEAD-0001",
    engagements=5,
    registrations=0,
    enrollments=0,
):
    return Lead360(
        lead_id=lead_id,
        tenant_id="reetha",
        first_name="Test",
        last_name="Lead",
        email="test.lead@reetha.example",
        phone="+919999999999",
        source="website",
        lifecycle_stage="lead",
        interest="technology",
        course_id="COURSE-0001",
        lead_score=80,
        total_engagements=engagements,
        unique_campaigns=2,
        unique_courses=1,
        last_engagement_at="2026-10-09T00:00:00",
        registration_count=registrations,
        enrollment_count=enrollments,
        engagement_channels=("email", "web"),
        engagement_event_types=("click", "page_view"),
    )


def test_engaged_unregistered_lead_gets_registration_follow_up():
    action = LeadNextBestActionEngine().recommend(
        make_lead(engagements=5, registrations=0)
    )

    assert action.action_type == "registration_follow_up"
    assert action.priority == "high"
    assert action.lead_id == "LEAD-0001"


def test_registered_not_enrolled_lead_gets_enrollment_follow_up():
    action = LeadNextBestActionEngine().recommend(
        make_lead(engagements=5, registrations=1, enrollments=0)
    )

    assert action.action_type == "enrollment_follow_up"
    assert action.priority == "high"


def test_unengaged_lead_gets_reengagement():
    action = LeadNextBestActionEngine().recommend(
        make_lead(engagements=0)
    )

    assert action.action_type == "re_engagement"
    assert action.priority == "medium"


def test_low_engagement_lead_gets_nurture():
    action = LeadNextBestActionEngine().recommend(
        make_lead(engagements=2)
    )

    assert action.action_type == "nurture"
    assert action.priority == "medium"


def test_active_lead_without_immediate_intervention_is_monitored():
    action = LeadNextBestActionEngine().recommend(
        make_lead(engagements=5, registrations=1, enrollments=1)
    )

    assert action.action_type == "monitor"
    assert action.priority == "low"

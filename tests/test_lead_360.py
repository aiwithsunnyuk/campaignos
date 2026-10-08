from src.lead_360 import Lead360


def test_lead_360_contract():
    lead = Lead360(
        lead_id="LEAD-0001",
        tenant_id="reetha",
        first_name="Aditya",
        last_name="Patel",
        email="aditya.patel1@example.com",
        phone="9219778234",
        source="LinkedIn",
        lifecycle_stage="qualified",
        interest="CRS-003",
        course_id="CRS-008",
        lead_score=20.24,
        total_engagements=5,
        unique_campaigns=2,
        unique_courses=1,
        last_engagement_at="2026-07-17T12:00:00",
        registration_count=1,
        enrollment_count=0,
        engagement_channels=("LinkedIn", "Email"),
        engagement_event_types=("form_started", "email_opened"),
    )

    assert lead.lead_id == "LEAD-0001"
    assert lead.tenant_id == "reetha"
    assert lead.lead_score == 20.24
    assert lead.total_engagements == 5
    assert lead.unique_campaigns == 2
    assert lead.unique_courses == 1
    assert lead.registration_count == 1
    assert lead.enrollment_count == 0


def test_lead_360_is_tenant_scoped():
    lead = Lead360(
        lead_id="LEAD-0001",
        tenant_id="reetha",
        first_name="Aditya",
        last_name="Patel",
        email="aditya.patel1@example.com",
        phone="9219778234",
        source="LinkedIn",
        lifecycle_stage="qualified",
        interest="CRS-003",
        course_id="CRS-008",
        lead_score=20.24,
        total_engagements=0,
        unique_campaigns=0,
        unique_courses=0,
        last_engagement_at=None,
        registration_count=0,
        enrollment_count=0,
        engagement_channels=(),
        engagement_event_types=(),
    )

    assert lead.tenant_id == "reetha"

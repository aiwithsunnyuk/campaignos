from src.data_contract import (
    Campaign,
    Course,
    Engagement,
    Enrollment,
    Lead,
    Registration,
)


def test_lead_contract_creation():
    lead = Lead(
        lead_id="L001",
        tenant_id="reetha",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="9876543210",
        source="website",
        lifecycle_stage="new",
        interest="AI",
        course_id="AI-001",
        lead_score=72.5,
        created_at="2026-10-08T10:00:00",
        updated_at="2026-10-08T10:00:00",
    )

    assert lead.lead_id == "L001"
    assert lead.tenant_id == "reetha"
    assert lead.lead_score == 72.5


def test_lead_is_tenant_scoped():
    lead = Lead(
        lead_id="L002",
        tenant_id="demo",
        first_name="Jane",
        last_name=None,
        email=None,
        phone=None,
        source="csv",
        lifecycle_stage="new",
        interest=None,
        course_id=None,
        lead_score=None,
        created_at="2026-10-08T10:00:00",
        updated_at="2026-10-08T10:00:00",
    )

    assert lead.tenant_id == "demo"


def test_campaign_contract():
    campaign = Campaign(
        campaign_id="CMP001",
        tenant_id="reetha",
        name="AI Certification Campaign",
        channel="linkedin",
        campaign_type="lead_generation",
        status="active",
        start_date="2026-10-01",
        end_date=None,
        budget=50000.0,
        created_at="2026-10-08T10:00:00",
        updated_at="2026-10-08T10:00:00",
    )

    assert campaign.campaign_id == "CMP001"
    assert campaign.tenant_id == "reetha"


def test_course_contract():
    course = Course(
        course_id="CRS001",
        tenant_id="reetha",
        name="Generative AI",
        category="AI",
        delivery_mode="online",
        duration="8 weeks",
        price=25000.0,
        status="active",
        created_at="2026-10-08T10:00:00",
        updated_at="2026-10-08T10:00:00",
    )

    assert course.course_id == "CRS001"
    assert course.name == "Generative AI"


def test_engagement_contract():
    engagement = Engagement(
        engagement_id="ENG001",
        tenant_id="reetha",
        lead_id="L001",
        channel="website",
        event_type="course_page_view",
        campaign_id="CMP001",
        course_id="CRS001",
        occurred_at="2026-10-08T10:00:00",
    )

    assert engagement.lead_id == "L001"
    assert engagement.course_id == "CRS001"


def test_registration_contract():
    registration = Registration(
        registration_id="REG001",
        tenant_id="reetha",
        lead_id="L001",
        course_id="CRS001",
        registration_type="demo",
        status="registered",
        registered_at="2026-10-08T10:00:00",
    )

    assert registration.lead_id == "L001"
    assert registration.course_id == "CRS001"


def test_enrollment_contract():
    enrollment = Enrollment(
        enrollment_id="ENR001",
        tenant_id="reetha",
        lead_id="L001",
        course_id="CRS001",
        enrollment_status="active",
        enrollment_date="2026-10-08T10:00:00",
        amount=25000.0,
        payment_status="paid",
        registration_id="REG001",
    )

    assert enrollment.enrollment_id == "ENR001"
    assert enrollment.tenant_id == "reetha"
    assert enrollment.lead_id == "L001"
    assert enrollment.course_id == "CRS001"
    assert enrollment.amount == 25000.0

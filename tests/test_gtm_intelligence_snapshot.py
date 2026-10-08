from src.gtm_intelligence import GTMIntelligenceSnapshotBuilder


def test_snapshot_builds_from_lead360_records():
    from src.lead_360.models import Lead360

    records = [
        Lead360(
            lead_id="LEAD-001",
            tenant_id="reetha",
            first_name="A",
            last_name="One",
            email="a@example.com",
            phone="1",
            source="LinkedIn",
            lifecycle_stage="qualified",
            interest="CRS-001",
            course_id="CRS-001",
            lead_score=80.0,
            total_engagements=10,
            unique_campaigns=4,
            unique_courses=2,
            last_engagement_at="2026-10-05T00:00:00",
            registration_count=1,
            enrollment_count=1,
            engagement_channels=("LinkedIn",),
            engagement_event_types=("form_submitted",),
        ),
        Lead360(
            lead_id="LEAD-002",
            tenant_id="reetha",
            first_name="B",
            last_name="Two",
            email="b@example.com",
            phone="2",
            source="Meta",
            lifecycle_stage="new",
            interest="CRS-002",
            course_id="CRS-002",
            lead_score=30.0,
            total_engagements=0,
            unique_campaigns=0,
            unique_courses=0,
            last_engagement_at=None,
            registration_count=0,
            enrollment_count=0,
            engagement_channels=(),
            engagement_event_types=(),
        ),
    ]

    snapshot = GTMIntelligenceSnapshotBuilder(
        tenant_id="reetha"
    ).build(
        records,
        as_of="2026-10-08T00:00:00",
    )

    assert snapshot.tenant_id == "reetha"
    assert snapshot.total_leads == 2
    assert snapshot.leads_with_engagement == 1
    assert snapshot.leads_with_registration == 1
    assert snapshot.leads_with_enrollment == 1
    assert snapshot.funnel_progression == (
        ("Lead", 2),
        ("Engaged", 1),
        ("Registered", 1),
        ("Enrolled", 1),
    )


def test_snapshot_rejects_cross_tenant_records():
    from src.lead_360.models import Lead360

    record = Lead360(
        lead_id="LEAD-001",
        tenant_id="demo",
        first_name="A",
        last_name="One",
        email="a@example.com",
        phone="1",
        source="LinkedIn",
        lifecycle_stage="new",
        interest="CRS-001",
        course_id="CRS-001",
        lead_score=20.0,
        total_engagements=0,
        unique_campaigns=0,
        unique_courses=0,
        last_engagement_at=None,
        registration_count=0,
        enrollment_count=0,
        engagement_channels=(),
        engagement_event_types=(),
    )

    try:
        GTMIntelligenceSnapshotBuilder("reetha").build([record])
    except ValueError as exc:
        assert "Tenant mismatch" in str(exc)
    else:
        raise AssertionError("Expected tenant isolation failure")

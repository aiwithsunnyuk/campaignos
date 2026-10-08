import pytest

from src.data_adapters import (
    CSVEngagementAdapter,
    CSVLeadAdapter,
)
from src.data_contract import (
    Enrollment,
    Registration,
)
from src.lead_360 import Lead360Builder


def _load_reetha_leads():
    return CSVLeadAdapter(
        tenant_id="reetha",
        path="data/reetha/leads.csv",
    ).load()


def _load_reetha_engagements():
    return CSVEngagementAdapter(
        tenant_id="reetha",
        path="data/reetha/engagements.csv",
    ).load()


def test_reetha_lead_360_builds_one_view_per_lead():
    leads = _load_reetha_leads()
    engagements = _load_reetha_engagements()

    registrations = [
        Registration(
            registration_id="REG-001",
            tenant_id="reetha",
            lead_id="LEAD-0001",
            course_id="CRS-003",
            registration_type="demo",
            status="registered",
            registered_at="2026-07-01T00:00:00",
            converted_at=None,
        )
    ]

    enrollments = [
        Enrollment(
            enrollment_id="ENR-001",
            tenant_id="reetha",
            lead_id="LEAD-0001",
            course_id="CRS-003",
            enrollment_status="in_progress",
            enrollment_date="2026-07-10T00:00:00",
            amount=12000.0,
            payment_status="paid",
        )
    ]

    builder = Lead360Builder(tenant_id="reetha")

    lead360 = builder.build(
        leads=leads,
        engagements=engagements,
        registrations=registrations,
        enrollments=enrollments,
    )

    assert len(lead360) == 250
    assert all(
        record.tenant_id == "reetha"
        for record in lead360
    )

    first = next(
        record
        for record in lead360
        if record.lead_id == "LEAD-0001"
    )

    assert first.first_name == "Aditya"
    assert first.last_name == "Patel"
    assert first.total_engagements >= 0
    assert first.registration_count == 1
    assert first.enrollment_count == 1


def test_lead_360_rejects_cross_tenant_records():
    leads = _load_reetha_leads()

    builder = Lead360Builder(tenant_id="reetha")

    with pytest.raises(ValueError, match="Tenant mismatch"):
        builder.build(
            leads=leads,
            engagements=[],
            registrations=[],
            enrollments=[
                Enrollment(
                    enrollment_id="ENR-001",
                    tenant_id="demo",
                    lead_id="LEAD-0001",
                    course_id="CRS-001",
                    enrollment_status="completed",
                    enrollment_date="2026-01-01T00:00:00",
                    amount=12000.0,
                    payment_status="paid",
                )
            ],
        )


def test_lead_360_rejects_unknown_lead_reference():
    leads = _load_reetha_leads()

    builder = Lead360Builder(tenant_id="reetha")

    bad_registration = Registration(
        registration_id="REG-999",
        tenant_id="reetha",
        lead_id="LEAD-9999",
        course_id="CRS-001",
        registration_type="demo",
        status="registered",
        registered_at="2026-01-01T00:00:00",
        converted_at=None,
    )

    with pytest.raises(
        ValueError,
        match="unknown lead",
    ):
        builder.build(
            leads=leads,
            engagements=[],
            registrations=[bad_registration],
            enrollments=[],
        )


def test_lead_360_aggregates_engagement_behavior():
    leads = _load_reetha_leads()

    engagements = _load_reetha_engagements()

    builder = Lead360Builder(tenant_id="reetha")

    lead360 = builder.build(
        leads=leads,
        engagements=engagements,
        registrations=[],
        enrollments=[],
    )

    engaged_records = [
        record
        for record in lead360
        if record.total_engagements > 0
    ]

    assert engaged_records
    assert all(
        record.unique_campaigns >= 0
        for record in engaged_records
    )
    assert all(
        record.unique_courses >= 0
        for record in engaged_records
    )
    assert all(
        record.last_engagement_at is not None
        for record in engaged_records
    )

from pathlib import Path

import pytest

from src.data_adapters import CSVEnrollmentAdapter


def test_reetha_enrollments_load_into_canonical_contract():
    adapter = CSVEnrollmentAdapter(
        tenant_id="reetha",
        path="data/reetha/enrollments.csv",
    )

    enrollments = adapter.load()

    assert len(enrollments) == 50
    assert all(
        enrollment.tenant_id == "reetha"
        for enrollment in enrollments
    )

    first = enrollments[0]

    assert first.enrollment_id == "ENR-0001"
    assert first.tenant_id == "reetha"
    assert first.lead_id == "LEAD-0065"
    assert first.course_id == "CRS-006"
    assert first.enrollment_status == "completed"
    assert first.enrollment_date == "2026-09-27T00:00:00"
    assert first.amount == 12000.0
    assert first.payment_status == "partial"


def test_reetha_enrollment_adapter_rejects_wrong_tenant():
    path = Path("data/reetha/wrong_tenant_enrollments.csv")

    path.write_text(
        """enrollment_id,tenant_id,lead_id,course_id,enrollment_status,enrollment_date,amount,payment_status
ENR-X001,demo,LEAD-0001,CRS-001,completed,2026-01-01T00:00:00,12000,paid
""",
        encoding="utf-8",
    )

    try:
        adapter = CSVEnrollmentAdapter(
            tenant_id="reetha",
            path=path,
        )

        with pytest.raises(ValueError, match="Tenant"):
            adapter.load()
    finally:
        path.unlink(missing_ok=True)


def test_reetha_enrollment_adapter_rejects_missing_columns():
    path = Path("data/reetha/invalid_enrollments.csv")

    path.write_text(
        """enrollment_id,tenant_id,lead_id
ENR-X001,reetha,LEAD-0001
""",
        encoding="utf-8",
    )

    try:
        adapter = CSVEnrollmentAdapter(
            tenant_id="reetha",
            path=path,
        )

        with pytest.raises(
            ValueError,
            match="Missing required columns",
        ):
            adapter.load()
    finally:
        path.unlink(missing_ok=True)

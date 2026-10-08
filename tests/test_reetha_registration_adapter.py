from pathlib import Path

import pytest

from src.data_adapters import CSVRegistrationAdapter


def test_reetha_registrations_load_into_canonical_contract():
    adapter = CSVRegistrationAdapter(
        tenant_id="reetha",
        path="data/reetha/registrations.csv",
    )

    registrations = adapter.load()

    assert len(registrations) == 100
    assert all(
        registration.tenant_id == "reetha"
        for registration in registrations
    )

    first = registrations[0]

    assert first.registration_id == "REG-0001"
    assert first.tenant_id == "reetha"
    assert first.lead_id == "LEAD-0234"
    assert first.course_id == "CRS-004"
    assert first.registration_type == "webinar"
    assert first.status == "registered"
    assert first.registered_at == "2026-07-15T00:00:00"
    assert first.converted_at is None


def test_reetha_registration_adapter_rejects_wrong_tenant():
    path = Path("data/reetha/wrong_tenant_registrations.csv")

    path.write_text(
        """registration_id,tenant_id,lead_id,course_id,registration_type,status,registered_at,converted_at
REG-X001,demo,LEAD-0001,CRS-001,webinar,registered,2026-01-01T00:00:00,
""",
        encoding="utf-8",
    )

    try:
        adapter = CSVRegistrationAdapter(
            tenant_id="reetha",
            path=path,
        )

        with pytest.raises(ValueError, match="Tenant"):
            adapter.load()
    finally:
        path.unlink(missing_ok=True)


def test_reetha_registration_adapter_rejects_missing_columns():
    path = Path("data/reetha/invalid_registrations.csv")

    path.write_text(
        """registration_id,tenant_id,lead_id
REG-X001,reetha,LEAD-0001
""",
        encoding="utf-8",
    )

    try:
        adapter = CSVRegistrationAdapter(
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

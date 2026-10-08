from pathlib import Path

from src.data_sources import (
    DataSourceAdapterFactory,
    TenantDataService,
    build_default_registry,
)


def build_service():
    return TenantDataService(
        registry=build_default_registry(),
        factory=DataSourceAdapterFactory(),
        base_path=Path("data/reetha"),
    )


def test_reetha_service_returns_all_canonical_sources():
    data = build_service().load_reetha()

    assert set(data.keys()) == {
        "leads",
        "engagements",
        "registrations",
        "enrollments",
    }


def test_reetha_service_record_counts():
    data = build_service().load_reetha()

    assert len(data["leads"]) == 250
    assert len(data["engagements"]) == 1500
    assert len(data["registrations"]) == 100
    assert len(data["enrollments"]) == 50


def test_reetha_service_preserves_tenant_boundary():
    data = build_service().load_reetha()

    for records in data.values():
        assert all(
            record["tenant_id"] == "reetha"
            for record in records
        )


def test_reetha_service_preserves_lead_identity():
    data = build_service().load_reetha()

    assert data["leads"][0]["lead_id"] == "LEAD-0001"

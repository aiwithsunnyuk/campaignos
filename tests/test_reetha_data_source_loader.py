from pathlib import Path

from src.data_sources import (
    DataSourceAdapterFactory,
    ReethaDataSourceLoader,
    build_default_registry,
)


BASE = Path("data/reetha")


def build_loader():
    return ReethaDataSourceLoader(
        registry=build_default_registry(),
        factory=DataSourceAdapterFactory(),
        base_path=BASE,
    )


def test_reetha_leads_load_through_source_layer():
    records = build_loader().load_leads()

    assert len(records) == 250
    assert records[0]["tenant_id"] == "reetha"


def test_reetha_engagements_load_through_source_layer():
    records = build_loader().load_engagements()

    assert len(records) == 1500
    assert all(record["tenant_id"] == "reetha" for record in records)


def test_reetha_registrations_load_through_source_layer():
    records = build_loader().load_registrations()

    assert len(records) == 100
    assert all(record["tenant_id"] == "reetha" for record in records)


def test_reetha_enrollments_load_through_source_layer():
    records = build_loader().load_enrollments()

    assert len(records) == 50
    assert all(record["tenant_id"] == "reetha" for record in records)

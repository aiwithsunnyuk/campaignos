import pytest

from src.data_sources.factory import DataSourceAdapterFactory
from src.data_sources.models import DataSource


def make_source(source_type="csv"):
    return DataSource(
        source_id="reetha-leads",
        tenant_id="reetha",
        name="Reetha Leads",
        source_type=source_type,
        status="active",
        description="Test source",
    )


def test_factory_creates_csv_adapter():
    adapter = DataSourceAdapterFactory().create(
        make_source("csv"),
        csv_loader=lambda: [
            {"lead_id": "LEAD-001"}
        ],
    )

    records = adapter.load()

    assert records == [
        {"lead_id": "LEAD-001"}
    ]


def test_factory_requires_csv_loader():
    with pytest.raises(ValueError):
        DataSourceAdapterFactory().create(
            make_source("csv")
        )


def test_factory_rejects_unimplemented_source():
    with pytest.raises(NotImplementedError):
        DataSourceAdapterFactory().create(
            make_source("api")
        )


def test_factory_rejects_database_until_implemented():
    with pytest.raises(NotImplementedError):
        DataSourceAdapterFactory().create(
            make_source("database")
        )

import pytest

from src.data_sources.models import DataSource
from src.data_sources.registry import DataSourceRegistry


def make_source(
    source_id="reetha-leads-csv",
    tenant_id="reetha",
    source_type="csv",
):
    return DataSource(
        source_id=source_id,
        tenant_id=tenant_id,
        name="Reetha Leads",
        source_type=source_type,
        status="active",
        description="Authorized lead data source",
    )


def test_register_and_get_source():
    registry = DataSourceRegistry()
    source = make_source()

    registry.register(source)

    assert registry.get("reetha-leads-csv") == source


def test_duplicate_source_rejected():
    registry = DataSourceRegistry()

    registry.register(make_source())

    with pytest.raises(ValueError):
        registry.register(make_source())


def test_list_sources_is_tenant_scoped():
    registry = DataSourceRegistry()

    registry.register(make_source("reetha-leads"))
    registry.register(
        make_source(
            "demo-leads",
            tenant_id="demo",
        )
    )

    sources = registry.list_for_tenant("reetha")

    assert len(sources) == 1
    assert sources[0].tenant_id == "reetha"


def test_unknown_source_rejected():
    registry = DataSourceRegistry()

    with pytest.raises(KeyError):
        registry.get("does-not-exist")

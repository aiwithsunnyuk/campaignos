import pytest

from src.data_ingestion import (
    DatasetVersion,
    DatasetVersionService,
)


def test_first_version_is_v1():
    version = DatasetVersionService().create_version(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        file_name="leads_oct.xlsx",
    )

    assert version.version == 1
    assert version.previous_version is None
    assert version.file_name == "leads_oct.xlsx"


def test_second_version_links_to_previous():
    service = DatasetVersionService()

    first = service.create_version(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        file_name="leads_oct.xlsx",
    )

    second = service.create_version(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        file_name="leads_nov.xlsx",
        existing_versions=(first,),
    )

    assert second.version == 2
    assert second.previous_version == 1


def test_versioning_is_tenant_safe():
    service = DatasetVersionService()

    reetha_v1 = service.create_version(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        file_name="reetha_leads.xlsx",
    )

    demo_v1 = service.create_version(
        dataset_id="LEADS",
        tenant_id="demo",
        dataset_type="lead",
        file_name="demo_leads.xlsx",
        existing_versions=(reetha_v1,),
    )

    assert demo_v1.version == 1
    assert demo_v1.previous_version is None


def test_promote_version():
    service = DatasetVersionService()

    version = service.create_version(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        file_name="leads_oct.xlsx",
    )

    promoted = service.promote(
        version,
        promoted_by="reetha-marketing",
    )

    assert promoted.version == 1
    assert promoted.promoted_by == "reetha-marketing"
    assert version.promoted_by is None


def test_promotion_requires_user():
    service = DatasetVersionService()

    version = service.create_version(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        file_name="leads_oct.xlsx",
    )

    with pytest.raises(ValueError, match="promoted_by is required"):
        service.promote(version, " ")

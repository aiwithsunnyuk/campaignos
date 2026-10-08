import pytest

from src.tenancy import get_tenant, list_tenants


def test_demo_tenant_exists():
    tenant = get_tenant("demo")

    assert tenant.tenant_id == "demo"
    assert tenant.status == "active"
    assert tenant.data_mode == "synthetic"


def test_reetha_tenant_exists():
    tenant = get_tenant("reetha")

    assert tenant.tenant_id == "reetha"
    assert tenant.name == "Reetha IT Hub"
    assert tenant.status == "active"
    assert tenant.data_mode == "synthetic"


def test_unknown_tenant_is_rejected():
    with pytest.raises(ValueError, match="Unknown CampaignOS tenant"):
        get_tenant("unknown")


def test_registered_tenants_are_distinct():
    tenants = list_tenants()

    tenant_ids = {tenant.tenant_id for tenant in tenants}

    assert "demo" in tenant_ids
    assert "reetha" in tenant_ids
    assert len(tenant_ids) == len(tenants)

from .models import Tenant


TENANTS: dict[str, Tenant] = {
    "demo": Tenant(
        tenant_id="demo",
        name="CampaignOS Demo",
        status="active",
        data_mode="synthetic",
        description="Synthetic demonstration tenant for CampaignOS.",
    ),
    "reetha": Tenant(
        tenant_id="reetha",
        name="Reetha IT Hub",
        status="active",
        data_mode="synthetic",
        description=(
            "Reetha IT Hub tenant. Synthetic data is used initially; "
            "authorized real-data integration will be introduced later."
        ),
    ),
}


def get_tenant(tenant_id: str) -> Tenant:
    try:
        tenant = TENANTS[tenant_id]
    except KeyError as exc:
        raise ValueError(
            f"Unknown CampaignOS tenant: {tenant_id}"
        ) from exc

    if tenant.status != "active":
        raise ValueError(f"Tenant is not active: {tenant_id}")

    return tenant


def list_tenants() -> list[Tenant]:
    return list(TENANTS.values())

from collections.abc import Iterable

from src.data_contract import Lead


class DataContractValidationError(ValueError):
    """Raised when canonical GTM data violates its contract."""


def validate_leads(
    leads: Iterable[Lead],
    tenant_id: str,
) -> list[Lead]:
    """
    Validate canonical leads before they enter CampaignOS.

    Every lead must belong to the expected tenant.
    Duplicate lead IDs are rejected within the supplied batch.
    """

    if not tenant_id:
        raise DataContractValidationError(
            "tenant_id is required"
        )

    validated = list(leads)
    seen_ids: set[str] = set()

    for lead in validated:
        if lead.tenant_id != tenant_id:
            raise DataContractValidationError(
                f"Tenant mismatch for lead {lead.lead_id}: "
                f"expected '{tenant_id}', "
                f"received '{lead.tenant_id}'"
            )

        if not lead.lead_id:
            raise DataContractValidationError(
                "lead_id is required"
            )

        if lead.lead_id in seen_ids:
            raise DataContractValidationError(
                f"Duplicate lead_id: {lead.lead_id}"
            )

        seen_ids.add(lead.lead_id)

    return validated

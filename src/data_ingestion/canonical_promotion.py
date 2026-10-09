from dataclasses import dataclass

from .canonical import CanonicalLead
from .mapping import MappingDecision
from .promotion import DatasetPromotion
from .versioning import DatasetVersion


@dataclass(frozen=True)
class CanonicalPromotionResult:
    dataset_id: str
    tenant_id: str
    version: int
    record_count: int
    leads: tuple[CanonicalLead, ...]


class CanonicalDatasetPromotionService:
    def promote_leads(
        self,
        promotion: DatasetPromotion,
        version: DatasetVersion,
        mapping: MappingDecision,
        leads: tuple[CanonicalLead, ...],
    ) -> CanonicalPromotionResult:
        if promotion.status != "promoted":
            raise ValueError(
                "Dataset must be promoted before canonical ingestion."
            )

        if version.tenant_id != promotion.tenant_id:
            raise ValueError("Version tenant does not match promotion.")

        if mapping.tenant_id != promotion.tenant_id:
            raise ValueError("Mapping tenant does not match promotion.")

        if not mapping.approved:
            raise ValueError(
                "Column mapping must be approved before ingestion."
            )

        if version.dataset_id != promotion.dataset_id:
            raise ValueError("Version does not match dataset promotion.")

        if mapping.dataset_id != promotion.dataset_id:
            raise ValueError("Mapping does not match dataset promotion.")

        return CanonicalPromotionResult(
            dataset_id=promotion.dataset_id,
            tenant_id=promotion.tenant_id,
            version=version.version,
            record_count=len(leads),
            leads=leads,
        )

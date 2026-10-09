from dataclasses import dataclass
from typing import Literal

from .validation import DataQualityReport


PromotionStatus = Literal["pending", "promoted", "rejected"]


@dataclass(frozen=True)
class DatasetPromotion:
    dataset_id: str
    tenant_id: str
    status: PromotionStatus
    promoted_by: str | None = None
    rejection_reason: str | None = None


class DatasetPromotionService:
    def create(
        self,
        dataset_id: str,
        tenant_id: str,
        report: DataQualityReport,
    ) -> DatasetPromotion:
        if report.dataset_id != dataset_id:
            raise ValueError("Dataset does not match validation report.")

        if report.tenant_id != tenant_id:
            raise ValueError("Dataset tenant does not match validation report.")

        return DatasetPromotion(
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            status="pending",
        )

    def promote(
        self,
        promotion: DatasetPromotion,
        approved_by: str,
    ) -> DatasetPromotion:
        if promotion.status != "pending":
            raise ValueError("Only pending datasets can be promoted.")

        if not approved_by.strip():
            raise ValueError("approved_by is required.")

        return DatasetPromotion(
            dataset_id=promotion.dataset_id,
            tenant_id=promotion.tenant_id,
            status="promoted",
            promoted_by=approved_by,
        )

    def reject(
        self,
        promotion: DatasetPromotion,
        rejected_by: str,
        reason: str,
    ) -> DatasetPromotion:
        if promotion.status != "pending":
            raise ValueError("Only pending datasets can be rejected.")

        if not rejected_by.strip():
            raise ValueError("rejected_by is required.")

        if not reason.strip():
            raise ValueError("rejection reason is required.")

        return DatasetPromotion(
            dataset_id=promotion.dataset_id,
            tenant_id=promotion.tenant_id,
            status="rejected",
            rejection_reason=reason,
        )

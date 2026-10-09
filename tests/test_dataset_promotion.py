import pytest

from src.data_ingestion import (
    DataQualityReport,
    DatasetPromotionService,
)


def quality_report(dataset_id="DATASET-001", tenant_id="reetha"):
    return DataQualityReport(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        total_rows=100,
        valid_rows=100,
        duplicate_rows=0,
        quality_score=100.0,
        issues=(),
    )


def test_create_promotion():
    service = DatasetPromotionService()

    promotion = service.create(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        report=quality_report(),
    )

    assert promotion.status == "pending"
    assert promotion.promoted_by is None


def test_promote_dataset():
    service = DatasetPromotionService()

    promotion = service.create(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        report=quality_report(),
    )

    promoted = service.promote(
        promotion,
        approved_by="reetha-marketing",
    )

    assert promoted.status == "promoted"
    assert promoted.promoted_by == "reetha-marketing"


def test_reject_dataset():
    service = DatasetPromotionService()

    promotion = service.create(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        report=quality_report(),
    )

    rejected = service.reject(
        promotion,
        rejected_by="reetha-marketing",
        reason="Source contains incomplete lead records.",
    )

    assert rejected.status == "rejected"
    assert rejected.rejection_reason == (
        "Source contains incomplete lead records."
    )


def test_cannot_promote_twice():
    service = DatasetPromotionService()

    promotion = service.create(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        report=quality_report(),
    )

    promoted = service.promote(
        promotion,
        approved_by="reetha-marketing",
    )

    with pytest.raises(ValueError, match="Only pending"):
        service.promote(
            promoted,
            approved_by="reetha-director",
        )


def test_tenant_mismatch_is_rejected():
    service = DatasetPromotionService()

    with pytest.raises(
        ValueError,
        match="tenant does not match",
    ):
        service.create(
            dataset_id="DATASET-001",
            tenant_id="reetha",
            report=quality_report(
                dataset_id="DATASET-001",
                tenant_id="another-tenant",
            ),
        )

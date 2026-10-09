from src.data_ingestion import DatasetValidator


def test_valid_dataset_scores_100():
    rows = [
        {"lead_id": "L1", "email": "one@example.com"},
        {"lead_id": "L2", "email": "two@example.com"},
        {"lead_id": "L3", "email": "three@example.com"},
    ]

    report = DatasetValidator().validate(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        rows=rows,
        required_fields=("lead_id", "email"),
        unique_key="lead_id",
    )

    assert report.total_rows == 3
    assert report.valid_rows == 3
    assert report.duplicate_rows == 0
    assert report.quality_score == 100.0
    assert report.issues == ()


def test_missing_required_values_are_reported():
    rows = [
        {"lead_id": "L1", "email": "one@example.com"},
        {"lead_id": "L2", "email": ""},
        {"lead_id": "", "email": "three@example.com"},
    ]

    report = DatasetValidator().validate(
        dataset_id="DATASET-002",
        tenant_id="reetha",
        rows=rows,
        required_fields=("lead_id", "email"),
        unique_key="lead_id",
    )

    assert report.total_rows == 3
    assert report.valid_rows == 1
    assert report.quality_score < 100.0

    issue_types = {issue.issue_type for issue in report.issues}

    assert "missing_required" in issue_types


def test_duplicate_keys_are_reported():
    rows = [
        {"lead_id": "L1", "email": "one@example.com"},
        {"lead_id": "L1", "email": "duplicate@example.com"},
        {"lead_id": "L2", "email": "two@example.com"},
    ]

    report = DatasetValidator().validate(
        dataset_id="DATASET-003",
        tenant_id="reetha",
        rows=rows,
        required_fields=("lead_id", "email"),
        unique_key="lead_id",
    )

    assert report.duplicate_rows == 1
    assert report.quality_score < 100.0

    duplicate_issues = [
        issue
        for issue in report.issues
        if issue.issue_type == "duplicate_key"
    ]

    assert len(duplicate_issues) == 1
    assert duplicate_issues[0].field == "lead_id"


def test_empty_dataset_has_zero_quality():
    report = DatasetValidator().validate(
        dataset_id="DATASET-004",
        tenant_id="reetha",
        rows=[],
        required_fields=("lead_id", "email"),
        unique_key="lead_id",
    )

    assert report.total_rows == 0
    assert report.valid_rows == 0
    assert report.quality_score == 0.0

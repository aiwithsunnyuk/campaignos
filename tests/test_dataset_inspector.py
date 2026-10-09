from pathlib import Path

import pandas as pd
import pytest

from src.data_ingestion import DatasetInspector


def test_inspect_csv(tmp_path: Path):
    path = tmp_path / "leads.csv"

    pd.DataFrame(
        [
            {"lead_id": "L1", "email": "one@example.com"},
            {"lead_id": "L2", "email": "two@example.com"},
        ]
    ).to_csv(path, index=False)

    dataset = DatasetInspector().inspect(
        file_path=path,
        dataset_id="DATASET-001",
        tenant_id="reetha",
    )

    assert dataset.dataset_id == "DATASET-001"
    assert dataset.tenant_id == "reetha"
    assert dataset.file_name == "leads.csv"
    assert dataset.file_type == "csv"
    assert dataset.status == "uploaded"
    assert dataset.row_count == 2
    assert dataset.column_count == 2
    assert dataset.columns == ("lead_id", "email")


def test_inspect_excel(tmp_path: Path):
    path = tmp_path / "leads.xlsx"

    pd.DataFrame(
        [
            {"lead_id": "L1", "name": "Sunny"},
        ]
    ).to_excel(path, index=False)

    dataset = DatasetInspector().inspect(
        file_path=path,
        dataset_id="DATASET-002",
        tenant_id="reetha",
    )

    assert dataset.file_type == "excel"
    assert dataset.row_count == 1
    assert dataset.columns == ("lead_id", "name")


def test_rejects_unsupported_file_type(tmp_path: Path):
    path = tmp_path / "leads.json"
    path.write_text("{}")

    with pytest.raises(ValueError, match="Unsupported file type"):
        DatasetInspector().inspect(
            file_path=path,
            dataset_id="DATASET-003",
            tenant_id="reetha",
        )

from pathlib import Path

import pandas as pd

from .models import UploadedDataset


class DatasetInspector:
    def inspect(
        self,
        file_path: str | Path,
        dataset_id: str,
        tenant_id: str,
    ) -> UploadedDataset:
        path = Path(file_path)

        suffix = path.suffix.lower()

        if suffix == ".csv":
            frame = pd.read_csv(path)
            file_type = "csv"
        elif suffix in {".xlsx", ".xls"}:
            frame = pd.read_excel(path)
            file_type = "excel"
        else:
            raise ValueError(
                f"Unsupported file type: {suffix}. "
                "Supported types are CSV and Excel."
            )

        columns = tuple(str(column) for column in frame.columns)

        return UploadedDataset(
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            file_name=path.name,
            file_type=file_type,
            status="uploaded",
            row_count=len(frame),
            column_count=len(columns),
            columns=columns,
        )

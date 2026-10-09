from dataclasses import dataclass
from typing import Literal


UploadFileType = Literal["csv", "excel"]
UploadStatus = Literal["uploaded", "validated", "rejected"]


@dataclass(frozen=True)
class UploadedDataset:
    dataset_id: str
    tenant_id: str
    file_name: str
    file_type: UploadFileType
    status: UploadStatus
    row_count: int
    column_count: int
    columns: tuple[str, ...]

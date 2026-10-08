from dataclasses import dataclass
from typing import Literal


DataSourceType = Literal[
    "csv",
    "excel",
    "api",
    "database",
    "synthetic",
]

DataSourceStatus = Literal[
    "active",
    "inactive",
    "error",
]


@dataclass(frozen=True)
class DataSource:
    source_id: str
    tenant_id: str
    name: str
    source_type: DataSourceType
    status: DataSourceStatus
    description: str

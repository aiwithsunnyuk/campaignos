from dataclasses import dataclass
from typing import Literal


TenantStatus = Literal["active", "inactive"]
DataMode = Literal["synthetic", "realtime", "shadow"]


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    name: str
    status: TenantStatus
    data_mode: DataMode
    description: str

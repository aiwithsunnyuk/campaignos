import csv
from pathlib import Path

from src.data_contract import Enrollment


class CSVEnrollmentAdapter:
    REQUIRED_COLUMNS = {
        "enrollment_id",
        "tenant_id",
        "lead_id",
        "course_id",
        "enrollment_status",
        "enrollment_date",
        "amount",
        "payment_status",
    }

    def __init__(self, tenant_id: str, path: str | Path):
        self.tenant_id = tenant_id
        self.path = Path(path)

    def load(self) -> list[Enrollment]:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        with self.path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            columns = set(reader.fieldnames or [])
            missing = self.REQUIRED_COLUMNS - columns

            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            return [self._to_enrollment(row) for row in reader]

    def _to_enrollment(
        self,
        row: dict[str, str],
    ) -> Enrollment:
        row_tenant_id = row.get("tenant_id")

        if row_tenant_id != self.tenant_id:
            raise ValueError(
                f"Tenant mismatch: adapter={self.tenant_id}, "
                f"row={row_tenant_id}"
            )

        return Enrollment(
            enrollment_id=row["enrollment_id"],
            tenant_id=self.tenant_id,
            lead_id=row["lead_id"],
            course_id=row["course_id"],
            enrollment_status=row["enrollment_status"],
            enrollment_date=row["enrollment_date"],
            amount=float(row["amount"]),
            payment_status=row["payment_status"],
        )

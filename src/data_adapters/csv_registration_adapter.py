import csv
from pathlib import Path

from src.data_contract import Registration


class CSVRegistrationAdapter:
    REQUIRED_COLUMNS = {
        "registration_id",
        "tenant_id",
        "lead_id",
        "course_id",
        "registration_type",
        "status",
        "registered_at",
        "converted_at",
    }

    def __init__(self, tenant_id: str, path: str | Path):
        self.tenant_id = tenant_id
        self.path = Path(path)

    def load(self) -> list[Registration]:
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

            return [self._to_registration(row) for row in reader]

    def _to_registration(
        self,
        row: dict[str, str],
    ) -> Registration:
        row_tenant_id = row.get("tenant_id")

        if row_tenant_id != self.tenant_id:
            raise ValueError(
                f"Tenant mismatch: adapter={self.tenant_id}, "
                f"row={row_tenant_id}"
            )

        return Registration(
            registration_id=row["registration_id"],
            tenant_id=self.tenant_id,
            lead_id=row["lead_id"],
            course_id=row["course_id"],
            registration_type=row["registration_type"],
            status=row["status"],
            registered_at=row["registered_at"],
            converted_at=row["converted_at"] or None,
        )

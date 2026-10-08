import csv
from pathlib import Path

from src.data_contract import Course


class CSVCourseAdapter:
    REQUIRED_COLUMNS = {
        "course_id",
        "tenant_id",
        "name",
        "category",
        "delivery_mode",
        "duration",
        "price",
        "status",
        "created_at",
        "updated_at",
    }

    def __init__(self, tenant_id: str, path: str | Path):
        self.tenant_id = tenant_id
        self.path = Path(path)

    def load(self) -> list[Course]:
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

            return [self._to_course(row) for row in reader]

    def _to_course(self, row: dict[str, str]) -> Course:
        row_tenant_id = row.get("tenant_id")

        if row_tenant_id != self.tenant_id:
            raise ValueError(
                f"Tenant mismatch: adapter={self.tenant_id}, "
                f"row={row_tenant_id}"
            )

        price = row.get("price")

        return Course(
            course_id=row["course_id"],
            tenant_id=self.tenant_id,
            name=row["name"],
            category=row.get("category"),
            delivery_mode=row.get("delivery_mode"),
            duration=row.get("duration"),
            price=float(price) if price else None,
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    issue_type: str
    message: str
    affected_rows: int


@dataclass(frozen=True)
class DataQualityReport:
    dataset_id: str
    tenant_id: str
    total_rows: int
    valid_rows: int
    duplicate_rows: int
    quality_score: float
    issues: tuple[ValidationIssue, ...]


class DatasetValidator:
    def validate(
        self,
        dataset_id: str,
        tenant_id: str,
        rows: list[dict[str, Any]],
        required_fields: tuple[str, ...],
        unique_key: str | None = None,
    ) -> DataQualityReport:
        issues: list[ValidationIssue] = []
        total_rows = len(rows)

        missing_counts = {
            field: sum(
                1
                for row in rows
                if row.get(field) is None
                or str(row.get(field)).strip() == ""
            )
            for field in required_fields
        }

        for field, count in missing_counts.items():
            if count:
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue_type="missing_required",
                        message=f"Required field '{field}' contains missing values.",
                        affected_rows=count,
                    )
                )

        duplicate_rows = 0

        if unique_key:
            seen: set[str] = set()

            for row in rows:
                value = row.get(unique_key)

                if value is None or str(value).strip() == "":
                    continue

                normalized = str(value).strip()

                if normalized in seen:
                    duplicate_rows += 1
                else:
                    seen.add(normalized)

            if duplicate_rows:
                issues.append(
                    ValidationIssue(
                        field=unique_key,
                        issue_type="duplicate_key",
                        message=f"Duplicate values found for '{unique_key}'.",
                        affected_rows=duplicate_rows,
                    )
                )

        invalid_rows = set()

        for index, row in enumerate(rows):
            if any(
                row.get(field) is None
                or str(row.get(field)).strip() == ""
                for field in required_fields
            ):
                invalid_rows.add(index)

        valid_rows = total_rows - len(invalid_rows)

        if total_rows == 0:
            quality_score = 0.0
        else:
            missing_penalty = (
                len(invalid_rows) / total_rows
            ) * 70

            duplicate_penalty = (
                duplicate_rows / total_rows
            ) * 30

            quality_score = max(
                0.0,
                round(
                    100.0
                    - missing_penalty
                    - duplicate_penalty,
                    2,
                ),
            )

        return DataQualityReport(
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            total_rows=total_rows,
            valid_rows=valid_rows,
            duplicate_rows=duplicate_rows,
            quality_score=quality_score,
            issues=tuple(issues),
        )

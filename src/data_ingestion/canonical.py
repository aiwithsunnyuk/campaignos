from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CanonicalLead:
    lead_id: str
    tenant_id: str
    email: str
    name: str | None = None
    phone: str | None = None


class CanonicalLeadTransformer:
    def transform(
        self,
        tenant_id: str,
        rows: list[dict[str, Any]],
        mapping: dict[str, str],
    ) -> tuple[CanonicalLead, ...]:
        required = ("lead_id", "email")

        for field in required:
            if field not in mapping:
                raise ValueError(
                    f"Required canonical field '{field}' "
                    "is missing from mapping."
                )

        records = []

        for row in rows:
            lead_id = row.get(mapping["lead_id"])
            email = row.get(mapping["email"])

            if lead_id is None or str(lead_id).strip() == "":
                raise ValueError("Canonical lead_id cannot be empty.")

            if email is None or str(email).strip() == "":
                raise ValueError("Canonical email cannot be empty.")

            name = (
                row.get(mapping["name"])
                if "name" in mapping
                else None
            )

            phone = (
                row.get(mapping["phone"])
                if "phone" in mapping
                else None
            )

            records.append(
                CanonicalLead(
                    lead_id=str(lead_id).strip(),
                    tenant_id=tenant_id,
                    email=str(email).strip(),
                    name=(
                        str(name).strip()
                        if name is not None
                        and str(name).strip()
                        else None
                    ),
                    phone=(
                        str(phone).strip()
                        if phone is not None
                        and str(phone).strip()
                        else None
                    ),
                )
            )

        return tuple(records)

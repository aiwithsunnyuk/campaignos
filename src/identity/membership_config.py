from __future__ import annotations

from pathlib import Path

import yaml

from .models import TenantMembership


class MembershipConfigError(ValueError):
    """Raised when identity membership configuration is invalid."""


class MembershipConfigService:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)

    def load(self) -> list[TenantMembership]:
        if not self.config_path.exists():
            raise MembershipConfigError(
                f"Membership configuration not found: {self.config_path}"
            )

        with self.config_path.open("r", encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}

        entries = payload.get("memberships", [])

        if not isinstance(entries, list):
            raise MembershipConfigError(
                "'memberships' must be a list."
            )

        memberships: list[TenantMembership] = []

        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise MembershipConfigError(
                    f"Membership entry {index} must be an object."
                )

            required = {
                "identity_email",
                "tenant_id",
                "role",
                "status",
            }

            missing = required - set(entry)

            if missing:
                raise MembershipConfigError(
                    f"Membership entry {index} missing: "
                    f"{', '.join(sorted(missing))}"
                )

            identity_email = str(entry["identity_email"]).strip().lower()

            if not identity_email:
                raise MembershipConfigError(
                    f"Membership entry {index} has an empty email."
                )

            memberships.append(
                TenantMembership(
                    identity_id=f"email:{identity_email}",
                    tenant_id=str(entry["tenant_id"]),
                    role=str(entry["role"]),
                    status=str(entry["status"]),
                )
            )

        return memberships

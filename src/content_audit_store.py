"""Local append-only audit persistence for CampaignOS content governance."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4


ALLOWED_EVENT_TYPES = {
    "package_created",
    "content_changed",
    "approval_changed",
}


class ContentAuditStore:
    """Persist governed content audit events in a local SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        if self.database_path == ":memory:":
            raise ValueError(
                "A file-backed database is required for persistent audit history."
            )
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS content_audit_events (
                        event_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL CHECK (length(tenant_id) > 0),
                        occurred_at TEXT NOT NULL,
                        event_type TEXT NOT NULL CHECK (
                            event_type IN (
                                'package_created',
                                'content_changed',
                                'approval_changed'
                            )
                        ),
                        campaign_name TEXT NOT NULL,
                        content_fingerprint TEXT NOT NULL,
                        approved INTEGER CHECK (
                            approved IS NULL OR approved IN (0, 1)
                        ),
                        external_execution_enabled INTEGER NOT NULL DEFAULT 0
                            CHECK (external_execution_enabled = 0),
                        event_json TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_content_audit_tenant_campaign
                    ON content_audit_events (
                        tenant_id, campaign_name, occurred_at
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS content_audit_no_update
                    BEFORE UPDATE ON content_audit_events
                    BEGIN
                        SELECT RAISE(ABORT, 'Audit events are append-only');
                    END
                    """
                )
                connection.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS content_audit_no_delete
                    BEFORE DELETE ON content_audit_events
                    BEGIN
                        SELECT RAISE(ABORT, 'Audit events are append-only');
                    END
                    """
                )

    def append_event(
        self,
        tenant_id: str,
        event: dict[str, Any],
        *,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        """Validate and append one event. Existing events are never replaced."""
        tenant_id = tenant_id.strip()
        if not tenant_id:
            raise ValueError("tenant_id must not be empty.")

        event_type = event.get("event_type")
        if event_type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"Unsupported content audit event: {event_type}")

        campaign_name = event.get("campaign_name")
        fingerprint = event.get("content_fingerprint")
        if not isinstance(campaign_name, str) or not campaign_name.strip():
            raise ValueError("campaign_name must not be empty.")
        if not isinstance(fingerprint, str) or not fingerprint.strip():
            raise ValueError("content_fingerprint must not be empty.")

        approved = event.get("approved")
        if event_type == "approval_changed":
            if not isinstance(approved, bool):
                raise ValueError(
                    "Approval events require an explicit boolean approved value."
                )
        elif "approved" in event:
            raise ValueError(
                "Only approval_changed events may include approval state."
            )

        if event.get("external_execution_enabled", False) is not False:
            raise ValueError("External execution must remain disabled.")

        timestamp = occurred_at or datetime.now(timezone.utc).isoformat()
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "occurred_at must be an ISO 8601 timestamp."
            ) from exc
        if parsed_timestamp.tzinfo is None:
            raise ValueError("occurred_at must include a timezone.")

        stored_event = {
            "event_id": str(uuid4()),
            "tenant_id": tenant_id,
            "occurred_at": timestamp,
            "event_type": event_type,
            "campaign_name": campaign_name,
            "content_fingerprint": fingerprint,
            "approved": approved,
            "external_execution_enabled": False,
        }

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO content_audit_events (
                        event_id, tenant_id, occurred_at, event_type,
                        campaign_name, content_fingerprint, approved,
                        external_execution_enabled, event_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
                    """,
                    (
                        stored_event["event_id"],
                        tenant_id,
                        timestamp,
                        event_type,
                        campaign_name,
                        fingerprint,
                        None if approved is None else int(approved),
                        json.dumps(stored_event, sort_keys=True),
                    ),
                )

        return stored_event

    def list_events(
        self,
        tenant_id: str,
        *,
        campaign_name: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List events for exactly one tenant, oldest first."""
        tenant_id = tenant_id.strip()
        if not tenant_id:
            raise ValueError("tenant_id must not be empty.")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer.")

        query = """
            SELECT event_json FROM content_audit_events
            WHERE tenant_id = ?
        """
        parameters: list[Any] = [tenant_id]

        if campaign_name is not None:
            query += " AND campaign_name = ?"
            parameters.append(campaign_name)

        query += " ORDER BY occurred_at ASC, rowid ASC LIMIT ?"
        parameters.append(limit)

        with closing(self._connect()) as connection:
            rows = connection.execute(query, parameters).fetchall()

        return [json.loads(row["event_json"]) for row in rows]

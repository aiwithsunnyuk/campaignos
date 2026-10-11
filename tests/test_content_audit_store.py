import sqlite3

import pytest

from src.content_audit_store import ContentAuditStore


def _event(
    event_type="package_created",
    *,
    approved=None,
    fingerprint="abc123",
):
    event = {
        "event_type": event_type,
        "campaign_name": "Campaign A",
        "content_fingerprint": fingerprint,
        "external_execution_enabled": False,
    }
    if approved is not None:
        event["approved"] = approved
    return event


def test_event_persists_across_store_instances(tmp_path):
    database = tmp_path / "audit.sqlite3"
    store = ContentAuditStore(database)

    saved = store.append_event("tenant-a", _event())
    reopened = ContentAuditStore(database)

    events = reopened.list_events("tenant-a")
    assert len(events) == 1
    assert events[0] == saved
    assert events[0]["event_id"]
    assert events[0]["occurred_at"]
    assert events[0]["external_execution_enabled"] is False


def test_events_are_isolated_by_tenant(tmp_path):
    store = ContentAuditStore(tmp_path / "audit.sqlite3")
    store.append_event("tenant-a", _event())
    store.append_event(
        "tenant-b",
        _event(fingerprint="tenant-b-content"),
    )

    assert len(store.list_events("tenant-a")) == 1
    assert len(store.list_events("tenant-b")) == 1
    assert store.list_events("tenant-a")[0]["content_fingerprint"] == "abc123"


def test_events_can_be_filtered_by_campaign(tmp_path):
    store = ContentAuditStore(tmp_path / "audit.sqlite3")
    store.append_event("tenant-a", _event())
    other = _event()
    other["campaign_name"] = "Campaign B"
    store.append_event("tenant-a", other)

    events = store.list_events("tenant-a", campaign_name="Campaign B")
    assert len(events) == 1
    assert events[0]["campaign_name"] == "Campaign B"


def test_events_are_returned_oldest_first(tmp_path):
    store = ContentAuditStore(tmp_path / "audit.sqlite3")
    store.append_event(
        "tenant-a",
        _event(fingerprint="later"),
        occurred_at="2026-10-12T10:02:00+00:00",
    )
    store.append_event(
        "tenant-a",
        _event(fingerprint="earlier"),
        occurred_at="2026-10-12T10:01:00+00:00",
    )

    events = store.list_events("tenant-a")
    assert [item["content_fingerprint"] for item in events] == [
        "earlier",
        "later",
    ]


def test_approval_event_requires_explicit_boolean(tmp_path):
    store = ContentAuditStore(tmp_path / "audit.sqlite3")

    with pytest.raises(ValueError, match="explicit boolean"):
        store.append_event(
            "tenant-a",
            _event("approval_changed"),
        )

    saved = store.append_event(
        "tenant-a",
        _event("approval_changed", approved=False),
    )
    assert saved["approved"] is False


def test_invalid_event_shapes_are_rejected(tmp_path):
    store = ContentAuditStore(tmp_path / "audit.sqlite3")

    with pytest.raises(ValueError, match="Unsupported"):
        store.append_event("tenant-a", _event("published"))

    with pytest.raises(ValueError, match="campaign_name"):
        store.append_event("tenant-a", {**_event(), "campaign_name": ""})

    with pytest.raises(ValueError, match="content_fingerprint"):
        store.append_event(
            "tenant-a",
            {**_event(), "content_fingerprint": ""},
        )

    with pytest.raises(ValueError, match="External execution"):
        store.append_event(
            "tenant-a",
            {**_event(), "external_execution_enabled": True},
        )

    with pytest.raises(ValueError, match="timezone"):
        store.append_event(
            "tenant-a",
            _event(),
            occurred_at="2026-10-12T10:00:00",
        )


def test_empty_tenant_and_invalid_limit_are_rejected(tmp_path):
    store = ContentAuditStore(tmp_path / "audit.sqlite3")

    with pytest.raises(ValueError, match="tenant_id"):
        store.append_event(" ", _event())

    with pytest.raises(ValueError, match="tenant_id"):
        store.list_events(" ")

    with pytest.raises(ValueError, match="positive integer"):
        store.list_events("tenant-a", limit=0)


def test_persisted_events_cannot_be_updated_or_deleted(tmp_path):
    database = tmp_path / "audit.sqlite3"
    store = ContentAuditStore(database)
    saved = store.append_event("tenant-a", _event())

    with sqlite3.connect(database) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE content_audit_events SET campaign_name = ? "
                "WHERE event_id = ?",
                ("Tampered", saved["event_id"]),
            )

        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM content_audit_events WHERE event_id = ?",
                (saved["event_id"],),
            )

    assert store.list_events("tenant-a")[0]["campaign_name"] == "Campaign A"

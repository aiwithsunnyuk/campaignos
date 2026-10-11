# M13.13.2 | Content Audit Integration

## Goal
Connect the existing SQLite append-only audit store to Content Studio with idempotent events and tenant-scoped history.

## Scope
- Use the existing `ContentAuditStore`; do not introduce another persistence layer.
- Resolve tenant ID only from the authenticated session.
- Record `package_created`, `content_changed`, and `approval_changed`.
- Deduplicate repeated Streamlit reruns by comparing prior event state in session state.
- Render a timeline scoped to the authenticated tenant and selected campaign.
- Preserve approval reset semantics and keep external execution disabled.

## Acceptance criteria
1. First render records one initial package event for an authenticated tenant.
2. An unchanged rerun creates no additional event.
3. A content fingerprint change creates one content-change event.
4. An approval transition creates one approval event; unchanged reruns create none.
5. Unauthenticated sessions do not write or display tenant audit records.
6. Tenant A cannot retrieve Tenant B's events through the UI.
7. `external_execution_enabled` is always false.
8. Focused and full test suites pass.

## Implementation sequence
1. Extend the event builder to support `content_changed` and validate approval values strictly.
2. Add a store factory with `CAMPAIGNOS_CONTENT_AUDIT_DB` override and a default path under `~/.campaignos/`.
3. Integrate after the final edited `ContentPackage` and approval state are known.
4. Record state transitions only after successful `append_event`.
5. Add the timeline below the export/approval area.
6. Test duplicate reruns, changed content, approval transitions, unauthenticated mode, and tenant isolation.

## Not in scope
- Live publishing, scheduler execution, external connector writes.
- Replacing authentication or tenant registry.
- Committing SQLite data or recovery files.

## Release gate
Run focused tests, then `python -m pytest -q`; inspect `git diff --check` and explicit source diffs before commit.

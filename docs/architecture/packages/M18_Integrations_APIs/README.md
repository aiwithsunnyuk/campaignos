# M18 | Integrations and APIs

## Goal
Connect CampaignOS to external CRM, marketing, analytics, and business systems through replaceable adapters.

## Required capabilities
- Versioned API contracts.
- Adapter interfaces and provider-specific implementations.
- OAuth/token lifecycle or equivalent secure authentication.
- Secret storage outside source control.
- Rate limiting, retries with backoff, timeouts, and circuit breaking where appropriate.
- Idempotency keys and reconciliation for write operations.
- Correlation IDs, structured logs, and redacted error details.

## Execution gates
- Read-only mode first.
- Explicit tenant-level connector configuration.
- Role and approval validation for writes.
- Dry-run preview and audit event before live execution.
- External execution disabled by default and off in tests.

## Deliverables
- `docs/architecture/m18_integration_contract.md`
- Connector interface and fake adapter.
- Contract tests and failure simulations.
- Runbook for credentials, rate limits, and reconciliation.

## Acceptance criteria
A connector can fail, retry, and recover without duplicate external actions or cross-tenant data access.

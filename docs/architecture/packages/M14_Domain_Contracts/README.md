# M14 | Domain Contracts

## Goal
Establish stable, testable service contracts between product surfaces and business logic.

## Suggested contract areas
- Campaign and campaign brief
- Lead and audience
- Content package and content draft
- Approval and audit event
- Measurement and campaign outcome

## Required design rules
- Typed request/response models and explicit validation.
- Tenant ID passed as trusted context, never accepted as an authorization claim from arbitrary UI input.
- Domain services remain independent of Streamlit.
- Side effects are isolated behind interfaces/adapters.
- Stable error types and idempotency rules for write operations.
- Contract tests cover valid, invalid, and cross-tenant requests.

## Deliverables
- `docs/architecture/m14_domain_contracts.md`
- Domain/service boundary map.
- Service-level tests and contract tests.
- Migration compatibility notes for existing callers.

## Acceptance criteria
Existing UI behavior remains compatible while business logic can be tested without running Streamlit. No parallel identity or tenant system is introduced.

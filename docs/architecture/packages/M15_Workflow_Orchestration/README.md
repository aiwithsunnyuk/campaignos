# M15 | Workflow Orchestration

## Goal
Coordinate business operations through explicit, resumable workflow state rather than scattered UI callbacks.

## Core concepts
- Workflow definition and version
- Workflow run and current state
- Step execution record
- Trigger and condition
- Human approval checkpoint
- Retry policy and failure state
- Audit correlation ID

## Safety and reliability
- Persist state transitions before reporting completion.
- Make retryable steps idempotent.
- Separate “approved” from “executed”.
- Apply tenant checks at workflow creation, retrieval, and every step.
- Default external execution to disabled.
- Provide timeout, retry limit, cancellation, and dead-letter/manual recovery behavior.

## Deliverables
- `docs/architecture/m15_workflow_contract.md`
- Minimal workflow service and repository interface.
- In-memory test adapter plus persistence adapter only where justified.
- Tests for retries, duplicate triggers, approval rejection, tenant isolation, and resume after failure.

## Acceptance criteria
A workflow can be inspected, resumed safely, and audited without depending on Streamlit session state as its source of truth.

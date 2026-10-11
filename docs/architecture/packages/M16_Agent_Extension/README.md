# M16 | Governed Agent Extension

## Goal
Extend the existing agent work through bounded tools and measurable outcomes, not an unrestricted autonomous loop.

## Agent contract
- Explicit task and tenant context
- Declared tool allowlist
- Typed input/output schema
- Time/token/cost budgets
- Timeout and retry policy
- Human escalation conditions
- Trace/correlation ID
- Evaluation result

## Architecture rules
- Agents call M14 domain services or M15 workflows; they do not bypass them.
- Retrieval is read-only unless an explicitly authorized tool permits a write.
- Every write tool checks tenant, role, approval, and idempotency.
- Store model/provider metadata and outcome, not secrets or unnecessary sensitive prompt content.
- External actions remain disabled by default.

## Deliverables
- `docs/architecture/m16_agent_contract.md`
- Tool registry and permission policy.
- Golden evaluation set and regression evaluation runner.
- Tests for prompt injection, malformed tool arguments, unauthorized actions, provider failure, and budget exhaustion.

## Acceptance criteria
Agent output is schema-valid, traceable, permission-checked, and evaluated against repeatable test cases.

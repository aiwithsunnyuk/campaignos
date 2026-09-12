# CampaignOS Agentic Architecture

## Purpose

CampaignOS demonstrates an explainable, human-in-the-loop approach to
campaign intelligence and operational decision support using synthetic data.

The agentic layer is deliberately deterministic first. A local LLM may be
used as an optional reasoning/presentation layer, but business decisions are
grounded in supplied CampaignOS signals.

## End-to-end flow

```text
Campaign Context
       |
       v
Campaign Intelligence Analyzer
       |
       v
Observations
       |
       v
Campaign Decision Engine
       |
       v
Agent Decisions
       |
       v
Campaign Agent Orchestrator
       |
       v
Agent Plan
       |
       v
Human Approval
     /   \
 Approve Reject
    |       |
    v       v
Execution  Rejected
-Ready     Decision
 Action
 Plan
```

## Domain responsibilities

| Component | Responsibility |
|---|---|
| Campaign Context | Converts campaign, contact and activity data into decision signals |
| Analyzer | Detects material campaign observations |
| Decision Engine | Maps observations to explainable recommended actions |
| Orchestrator | Coordinates analysis and decisions into an agent plan |
| Approval | Applies human review and determines execution readiness |
| Streamlit UI | Presents the workflow and approval state |
| Local LLM Copilot | Optional natural-language assistance |

## Explainability chain

Every proposed action should be traceable through:

```text
Signal
  -> Observation
  -> Reason
  -> Evidence
  -> Decision
  -> Recommended Action
  -> Confidence
  -> Human Approval
```

This keeps the system auditable and prevents the LLM from becoming an
uncontrolled source of invented campaign performance.

## Human-in-the-loop boundary

CampaignOS can produce an execution-ready action plan after human approval,
but the portfolio application does not execute external production actions.

It does not:

- send email
- update Oracle Eloqua
- update Salesforce
- access Outlook
- modify live campaign records
- require customer API keys

The project uses synthetic data for demonstration and portfolio purposes.

## Why deterministic-first?

A deterministic decision layer provides:

1. repeatable test results
2. explainable business rules
3. safe fallback when a local model is unavailable
4. easier debugging
5. clear separation between business logic and language generation

The local LLM is therefore complementary rather than authoritative.

## Production evolution

A production implementation could add authenticated connectors, persistent
storage, RBAC, approval audit logs, observability, queue-based execution,
provider adapters and policy controls.

Those capabilities are intentionally outside the synthetic portfolio
boundary.

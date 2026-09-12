# CampaignOS M10.5

## Human Approval + Action Plan

M10.5 adds a controlled human-in-the-loop layer after the M10.2 analyzer,
M10.3 decision engine, and M10.4 orchestrator.

Flow:

Campaign Agent Plan
→ Human Review
→ Approved / Rejected Decisions
→ Execution Action Plan

This package is intentionally additive. It does **not** replace existing
CampaignOS agent files.

### Files

- `src/agent/approval.py`
- `tests/test_agent_approval.py`

### Safety boundary

M10.5 does not send email, update Salesforce/Eloqua, call Outlook, or invoke
external systems. It creates an execution-ready representation only. Actual
execution remains a future, controlled integration step.

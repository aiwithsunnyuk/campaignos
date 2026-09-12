# CampaignOS M10.11 - Security & AI Guardrails

M10.11 is the deployment-gate hardening package for CampaignOS.

## What it adds

- `SECURITY.md` with repository security policy and scope.
- `docs/security.md` with deployment/security posture.
- `docs/agentic_guardrails.md` with the AI action and approval boundary.
- `src/agent/guardrails.py` with an explicit action allowlist and parameter
  validation.
- `tests/test_agent_guardrails.py` with regression coverage.
- `.github/workflows/security.yml` for tests, dependency audit, Bandit, and
  CodeQL.

## Guardrail model

```text
AI Output
   |
   v
Schema / Domain Validation
   |
   v
Action Allowlist
   |
   v
Secret + External-Execution Parameter Check
   |
   v
Human Approval
   |
   v
Execution-Ready Plan
   |
   X  No external execution adapter
```

## Apply

Copy the package contents into the CampaignOS repository root, preserving the
directory structure.

Then run:

```bash
python -m pytest -q tests/test_agent_guardrails.py
python -m pytest -q
git restore data/synthetic/activities.csv
git status --short
```

The expected baseline after M10.11 is the existing **104+** test suite plus
the new guardrail tests. The exact count may change as additional tests are
added.

## Important

Only type/run commands in the terminal. Do not paste terminal output back into
the shell.

This milestone does not add external integrations, credentials, autonomous
sending, or production-system mutation.

# CampaignOS M10.7 - Agent Hardening

M10.7 adds isolated safety/readiness helpers and regression tests without
replacing the existing analyzer, decision engine, orchestrator, approval
module, or Streamlit UI.

## Files

```text
src/agent/hardening.py
tests/test_agent_hardening.py
M10_7_README.md
```

No existing file needs to be replaced.

## Validate

```bash
python -m pytest -q tests/test_agent_hardening.py
```

Expected:

```text
5 passed
```

Then run:

```bash
python -m pytest -q
```

If the full suite rewrites synthetic activities:

```bash
git restore data/synthetic/activities.csv
```

## Hardening coverage

- Confidence constrained to 0..1.
- Existing agent decisions validated through the domain model.
- Proposed plans are not execution-ready.
- Fully approved plans are execution-ready.
- Mixed approval/rejection plans are not execution-ready.
- Empty plans are never execution-ready.
- Approval/rejection counts are deterministic.

CampaignOS remains a human-in-the-loop decision-support system. M10.7 does
not send email, update Eloqua/Salesforce, access Outlook, or modify live
campaigns.

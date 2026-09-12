# M10.6 Agentic Campaign Operations UI

M10.6 exposes the M10.2-M10.5 workflow through a Streamlit capstone page.

Flow:

Campaign Selection
→ Campaign Context
→ Intelligence Analyzer
→ Decision Engine
→ Agent Plan
→ Human Approval
→ Execution-Ready Action Plan

The page uses CampaignOS synthetic data only. It does not execute external
marketing or CRM actions.

## Additive files

- `src/agent/campaign_context.py`
- `app/pages/8_Agentic_Campaign_Operations.py`
- `tests/test_campaign_context.py`

No existing M10.1-M10.5 files are replaced.

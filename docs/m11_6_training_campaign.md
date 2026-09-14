# M11.6 • Create Training Campaign

## Purpose

M11.6 turns explicit training-growth inputs into a validated `TrainingCampaign`,
a deterministic execution plan, a training funnel, and a safe promotional
message preview.

## Design boundary

```text
User inputs
    ↓
Validation
    ↓
TrainingCampaign
    ├── Campaign brief
    ├── Execution plan
    ├── Training funnel
    └── Message preview
            ↓
       Human review
            ↓
Authorized external delivery
```

CampaignOS does not send WhatsApp or email messages and does not contain real
meeting credentials.

## Why the implementation is intentionally deterministic

M11.6 is an operational workflow, not an AI-writing experiment. The same
inputs should produce the same campaign structure. AI can be layered on later
for optional recommendations without changing the validated campaign object.

## Acceptance criteria

- Campaign can be created from explicit inputs.
- Program and campaign controls are validated.
- Campaign brief is displayed.
- Six-area execution plan is displayed.
- Training funnel is displayed.
- Synthetic promotional message is displayed.
- Invalid required fields produce a clear UI error.
- No external message is sent.
- No real credentials are embedded.

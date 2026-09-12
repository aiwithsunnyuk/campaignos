# Agentic Guardrails

CampaignOS follows the principle:

> **Calculate first. Explain second. Act only with approval.**

## 1. Action allowlist

The agent may propose only known marketing-operations actions:

- `OPTIMIZE_CONVERSION_PATH`
- `OPTIMIZE_EMAIL_ENGAGEMENT`
- `OPTIMIZE_CTA`
- `REFINE_AUDIENCE`
- `PRIORITIZE_LEADS`
- `REVIEW_JOURNEY`

Anything else is rejected.

This is intentionally narrower than arbitrary tool calling.

## 2. Untrusted model output

The optional local LLM is an explanation/generation component, not a policy
engine.

Model output must not:

- grant itself permissions;
- create new action types;
- bypass approval;
- request secrets;
- invoke arbitrary URLs/tools;
- claim an external action was executed when it was not.

## 3. Human approval

A plan is execution-ready only when:

- it contains at least one decision;
- every decision is valid;
- every action is allowlisted;
- every decision has explicit `APPROVED` status;
- no decision is rejected or merely proposed.

CampaignOS still does not perform the external action.

## 4. External execution boundary

The current application deliberately has no execution adapter for:

- Eloqua;
- Salesforce;
- Outlook;
- CRM/CDP;
- email delivery;
- live campaign mutation.

This makes the agentic demonstration safer and keeps the portfolio scope clear.

## 5. Evidence boundary

Recommendations should be based on supplied campaign context. Missing evidence
must not be invented to make a recommendation look stronger.

## 6. Interview-ready security statement

> “I designed the agent as a decision-support system rather than an
> autonomous production operator. Its action space is allowlisted, AI output
> is untrusted, recommendations require human approval, and there is no direct
> execution path into Eloqua, Salesforce, Outlook, or live campaign systems.”

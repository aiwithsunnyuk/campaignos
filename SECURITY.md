# Security Policy

## Scope

CampaignOS is a security-conscious portfolio application and demonstration
platform. It uses synthetic data and is intentionally designed without direct
access to Oracle Eloqua, Salesforce, Outlook, CRM, CDP, or production campaign
systems.

It is **not** presented as a production enterprise marketing platform.

## Security boundaries

CampaignOS:

- uses synthetic campaign, contact, activity, and account data;
- does not require proprietary platform credentials;
- does not send marketing messages;
- does not modify live campaign records;
- does not execute arbitrary agent-generated tools;
- keeps agent recommendations behind a human approval boundary;
- treats optional local LLM output as untrusted input.

The intended flow is:

```text
Synthetic Data
      |
      v
Campaign Intelligence
      |
      v
Agent Recommendation
      |
      v
Action Allowlist + Domain Validation
      |
      v
Human Approval
      |
      v
Execution-Ready Plan
      |
      X  No direct external execution
```

## Secrets

Never commit:

- `.env`
- `.env.*` except `.env.example`
- API keys or access tokens
- private keys (`*.pem`, `*.key`)
- credential files
- production configuration
- customer or employee data

Use environment variables or the deployment platform's secret store for any
future integration credentials.

## AI safety

LLM output must never be treated as an authorization to execute an operation.
AI-generated text and parameters must pass:

1. schema validation;
2. action allowlist validation;
3. domain/business-rule validation;
4. human approval where required.

Secrets must never be placed in prompts or sent to a model.

## Reporting a vulnerability

For this portfolio repository, please avoid publishing sensitive exploit
details in a public issue. Contact the repository owner privately through the
contact method provided on the repository profile.

For a deployed instance, report only the minimum information required to
reproduce the issue and do not include real customer data.

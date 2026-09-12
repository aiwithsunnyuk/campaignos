# CampaignOS Security & Deployment Notes

## Security posture

CampaignOS is designed as a security-conscious portfolio application, not a
production enterprise marketing system.

The application uses synthetic data only and deliberately contains no direct
connection to proprietary marketing platforms.

### Current controls

| Control | Status | Notes |
|---|---|---|
| Synthetic demo data | Strong | No customer dataset required |
| Secret exclusion | Implemented | Repository ignore rules cover common secret files |
| Agent action allowlist | Implemented | Unknown action types are rejected |
| Human approval boundary | Implemented | Approval is required before a plan is execution-ready |
| External execution | Disabled | No sending or live-system mutation capability |
| LLM optionality | Implemented | Deterministic fallback works without an LLM |
| LLM output validation | Implemented | AI output is treated as untrusted |
| Dependency audit | CI | `pip-audit` runs in the security workflow |
| Static security scan | CI | Bandit runs against Python source |
| CodeQL | CI | GitHub CodeQL analysis is configured |
| Public-app authentication/RBAC | Not implemented | Explicitly outside portfolio scope |

## Deployment guidance

For a public portfolio deployment:

- keep synthetic data only;
- do not add proprietary credentials to the repository;
- configure secrets through the hosting provider if a future integration is
  added;
- expose only the application port;
- keep debug/development modes disabled where the hosting platform permits;
- review Streamlit configuration before public deployment;
- do not treat the application as production-ready without authentication,
  authorization, audit logging, rate limiting, and operational monitoring.

## Content Studio boundary

The Content Studio previews HTML supplied by the application/user. If the
application is later opened to untrusted multi-user input, HTML rendering must
be reviewed and isolated appropriately before production use.

## Future hardening

Potential production controls include:

- non-root container execution;
- read-only container filesystem where practical;
- pinned/locked deployment dependencies;
- authentication and RBAC;
- audit logging;
- rate limiting;
- CSP and additional browser security headers;
- centralized secret management;
- vulnerability management and patch SLAs;
- formal threat modeling.

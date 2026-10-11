# M19+ | Production Hardening

## Goal
Make releases repeatable, recoverable, observable, secure, and supportable.

## Workstreams
- Reproducible environments, dependency pinning, CI gates.
- Deployment configuration and environment separation.
- Database migration/versioning strategy.
- Automated backup and restore drills.
- Centralized structured logs, metrics, traces, and alerting.
- Secret scanning, dependency scanning, authorization tests, and threat modeling.
- Load/performance budgets and resource limits.
- Data retention, deletion, export, and audit policies.
- Incident response, rollback, and operational runbooks.

## Release gates
- Full tests and contract tests pass.
- Static checks and security scans pass.
- Migrations are backward compatible or have an explicit migration window.
- Restore drill has been performed and measured.
- Rollback procedure is documented and tested.
- No secrets, database files, or local recovery artifacts are committed.

## Acceptance criteria
A new environment can be deployed from documented steps, critical data can be restored, and operational failures can be detected and diagnosed.

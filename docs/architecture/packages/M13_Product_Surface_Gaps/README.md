# M13 | Product-Surface Gap Closure

## Goal
Finish the intended user-facing CampaignOS surfaces without expanding the architecture sideways.

## Workstreams
- Inventory existing pages and navigation.
- Map each surface to a domain service and its existing tests.
- Identify incomplete empty states, error states, permissions, and loading states.
- Ensure shared tenant identity and consistent audit behavior.
- Make the primary user journey navigable end to end.

## Required artifacts
- `docs/architecture/m13_surface_inventory.md`
- `docs/architecture/m13_gap_register.md`
- Tests for each fixed user journey.

## Acceptance criteria
- Every shipped navigation item opens without runtime errors.
- Each surface has a defined purpose, input/output contract, and permission boundary.
- No duplicated domain logic is added to Streamlit page files.
- Every gap is classified as fixed, deferred with rationale, or explicitly out of scope.
- The full regression suite passes.

## Guardrails
Do not redesign Lead 360, NBA, identity, or tenant foundations without a reproducible defect or an explicit contract requirement.

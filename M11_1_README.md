# CampaignOS M11.1 — Training Growth & Campaign 360 Foundation

## Objective

M11 turns CampaignOS from a set of campaign modules into a campaign-level operating experience. M11.1 establishes the reusable training-growth domain primitives that will support the Hands-On Agile Coaching (HAC) vertical implementation.

## Included

- `src/training/models.py` — training programs, campaign context, lead profiles and recommendation models.
- `src/training/engine.py` — deterministic training-intent scoring, explainable program recommendations and campaign snapshots.
- `data/training/hac_programs.csv` — a synthetic CampaignOS catalogue seeded from the publicly visible HAC course categories/names. Delivery mode is deliberately `Verify with client`; CampaignOS must not infer that every offering is on-demand.
- `tests/test_training.py` — initial M11 domain tests.

## Design principles

1. Reuse the existing CampaignOS M1–M10 engines rather than rebuilding them.
2. Keep HAC-specific data in a vertical layer, not inside generic campaign logic.
3. Use synthetic lead/engagement data in the public portfolio repository.
4. Treat external execution as out of scope. CampaignOS prepares governed campaign plans and recommendations.
5. Do not store real Zoom credentials, private meeting links, phone numbers or other operational secrets in the repository.
6. Recommendations are deterministic and explainable before optional AI is introduced.

## Next M11 increments

- M11.2 — HAC Training Growth Hub Streamlit page
- M11.3 — Course catalogue and career personas
- M11.4 — Career Path Finder
- M11.5 — Training Intent Scoring UI
- M11.6 — "Create Today's Training Campaign"
- M11.7 — WhatsApp/email content templates
- M11.8 — Training lead funnel and campaign calendar
- M11.9 — Campaign intelligence + M10 agent bridge
- M11.10 — UX, testing, documentation and deployment validation

## Safety boundary

The example HAC WhatsApp/Zoom campaign content supplied during design is treated as a pattern, not as data to copy into the public repository. Real operational details belong in an authorized client environment and should never be committed as secrets.

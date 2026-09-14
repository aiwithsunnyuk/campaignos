# CampaignOS M11.5 — Training Intent Scoring

Adds a dedicated `11_Training_Intent_Scoring.py` Streamlit page.

The user can define a synthetic learner profile, activate engagement signals, calculate a deterministic intent score, inspect signal contributions, and see a recommended next action.

## Validation

```bash
python -m py_compile app/pages/11_Training_Intent_Scoring.py
python -m pytest tests/test_training_intent_scoring.py -q
python -m pytest -q
```

## New files

- `app/pages/11_Training_Intent_Scoring.py`
- `tests/test_training_intent_scoring.py`
- `docs/m11_5_training_intent_scoring.md`

M11.5 is decision support only. No WhatsApp, email, Eloqua, Salesforce, CRM, or external campaign execution is included.

# CampaignOS M11.3

## Career Personas & Recommendation Intelligence

M11.3 improves the M11 Training Growth Hub recommendation layer.

### Added

- Eight reusable career personas.
- Explicit persona identification from background, goal, interest and experience.
- Persona-aware programme ranking.
- Explainable recommendation reasons.
- Persona visibility in the Training Growth Hub.
- Regression tests for data-career and Agile/Product scenarios.

### Validation

```bash
python -m pytest tests/test_training.py tests/test_training_campaign_builder.py tests/test_training_personas.py -q
python -m py_compile app/pages/9_Training_Growth_Hub.py
```

For the full CampaignOS suite:

```bash
python -m pytest -q
```

If the full test suite rewrites the synthetic activity dataset, restore it before
committing:

```bash
git restore data/synthetic/activities.csv
```

### Product outcome

CampaignOS can now explain not only *which* programme it recommends, but also
*why* that programme fits the prospect's declared career path.

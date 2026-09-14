# CampaignOS M11.6 Clean Build

This package replaces the unstable M11.6 builder attempt with a clean,
deterministic implementation.

## Important

This package is designed to be copied into an existing CampaignOS repository
that already contains the M11.1 training domain:

- `src/training/models.py`
- `data/training/hac_programs.csv`

It intentionally does **not** modify `src/training/engine.py`.

## Files

```text
src/training/__init__.py
src/training/campaign_builder.py
tests/test_training_campaign.py
app/pages/12_Create_Training_Campaign.py
docs/m11_6_training_campaign.md
```

## Validation order

Run these commands from the CampaignOS repository root:

```bash
python -m py_compile src/training/campaign_builder.py
python -m pytest tests/test_training_campaign.py -q
python -m pytest -q
git restore data/synthetic/activities.csv
git status --short
```

Only after the Python tests are clean:

```bash
streamlit run app/Home.py
```

Then open:

**Create Training Campaign**

## M11.6 safety boundary

The page prepares a campaign and promotional content for review. It does not
send messages, call WhatsApp, call email, create Zoom meetings, or connect to
Eloqua, Salesforce, Outlook, or other proprietary systems.

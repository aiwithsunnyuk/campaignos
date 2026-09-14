# CampaignOS M11.2

## Training Campaign Creation

M11.2 upgrades the M11.1 Training Growth Hub preview into a functional, portfolio-safe campaign creation workflow.

### Added
- Deterministic training campaign builder.
- Create Today's Training Campaign workflow.
- Region, channel, session and CTA configuration.
- Audience strategy selection.
- Synthetic message preview.
- Explicit no-send / no-credential governance boundary.
- Unit tests for campaign creation and serialization.

### Prerequisite
Apply M11.1 first. This package updates the training domain introduced by M11.1.

### Validation
```bash
python -m pytest tests/test_training.py tests/test_training_campaign_builder.py -q
python -m py_compile app/pages/9_Training_Growth_Hub.py
```

Then run:
```bash
streamlit run app/Home.py
```

The new page appears as **Training Growth Hub** in the sidebar.

### Expected outcome
A hiring manager can see CampaignOS move from a training catalogue to an explicit campaign draft with audience, channel, session, CTA and content-preview decisions, while real communication execution remains outside the public portfolio.

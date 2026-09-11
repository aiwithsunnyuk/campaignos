# CampaignOS Architecture

## M1

```text
Streamlit UI
    |
    v
Application / Analytics
    |
    v
CSV Data Layer
    |
    v
Synthetic Data Generator
```

## Future

```text
Streamlit
    |
FastAPI services
    |
Domain engines
├── Campaign
├── Segmentation
├── Lead scoring
├── Journey
├── Content
├── Analytics
└── AI
    |
SQLite / Parquet
    |
Synthetic + imported datasets
```

The architecture is vendor-neutral. Enterprise platforms can be represented as concepts and workflows without connecting to proprietary systems.

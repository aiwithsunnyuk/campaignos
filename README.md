# CampaignOS

**Unified Campaign Management & Marketing Automation Platform**

CampaignOS is an open-source, vendor-neutral marketing automation portfolio application built with Python and Streamlit. It demonstrates campaign planning, audience segmentation, regional marketing operations, lead management, analytics, synthetic CRM-style data, and a foundation for local LLM/agentic AI capabilities.

> **Portfolio project:** CampaignOS uses synthetic data only. It does not connect to Oracle Eloqua, Salesforce, Outlook, or any other proprietary business system.

## M1 Foundation

- Streamlit marketing operations dashboard
- Synthetic contacts, accounts, products, campaigns and activities
- WW / APAC / AMEA / Europe regional views
- Campaign and engagement KPIs
- Python application structure
- Data generator
- CSV data layer
- Automated tests
- VS Code configuration
- Shell startup script
- Docker / Docker Compose support

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py
streamlit run app/Home.py
```

## Docker

```bash
docker compose up --build
```

Open `http://localhost:8501`.

## Planned milestones

1. Foundation + synthetic data
2. Campaign Planner
3. Audience Segmentation Engine
4. Lead Scoring + Lifecycle
5. Journey Orchestration
6. HTML/CSS Content Studio
7. Campaign Analytics + Regional Reporting
8. Excel/CSV workflows + Docker hardening
9. Local LLM Campaign Copilot
10. Agentic AI + production polish

## Portfolio positioning

CampaignOS demonstrates transferable marketing-automation concepts commonly found in enterprise CRM and marketing automation environments: campaign operations, audience management, segmentation, lead lifecycle, journey orchestration, content operations, regional/global execution, campaign measurement, analytics, and data-driven decision making.

It intentionally avoids claiming direct product integration where none exists.

import io
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.loader import (
    load_activities,
    load_campaigns,
    load_contacts,
)
from src.reporting.excel_export import (
    build_campaign_performance,
    build_executive_summary,
    build_regional_performance,
    export_campaignos_workbook,
)


st.set_page_config(
    page_title="CampaignOS | Operational Exports",
    page_icon="📦",
    layout="wide",
)


st.title("📦 Operational Reporting & Exports")

st.caption(
    "Generate executive, campaign, regional and lead reporting "
    "packages from CampaignOS synthetic data."
)


campaigns = load_campaigns()
activities = load_activities()
contacts = load_contacts()


if campaigns.empty:
    st.error("Campaign data is unavailable.")
    st.stop()

performance = build_campaign_performance(
    campaigns,
    activities,
)

regional = build_regional_performance(
    performance,
)

executive = build_executive_summary(
    performance,
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Campaigns",
    f"{len(campaigns):,}",
)

col2.metric(
    "Contacts",
    f"{len(contacts):,}",
)

col3.metric(
    "Performance Rows",
    f"{len(performance):,}",
)

col4.metric(
    "Regions",
    f"{regional['region'].nunique():,}"
    if not regional.empty
    else "0",
)


st.subheader("Executive Reporting")

st.dataframe(
    executive,
    width="stretch",
    hide_index=True,
)


st.subheader("Campaign Performance")

st.dataframe(
    performance,
    width="stretch",
    hide_index=True,
)


st.subheader("Regional Performance")

st.dataframe(
    regional,
    width="stretch",
    hide_index=True,
)


st.subheader("Excel Reporting Package")

st.write(
    """
CampaignOS can package the operational reporting layer into a
single Excel workbook containing:

- Executive Summary
- Campaign Performance
- Regional Performance
- Lead Export
"""
)


if st.button(
    "📊 Generate Excel Reporting Package",
    type="primary",
):

    output_path = ROOT / "data" / "exports" / "campaignos_reporting.xlsx"

    try:
        export_campaignos_workbook(
            output_path=output_path,
            campaigns=campaigns,
            activities=activities,
            contacts=contacts,
        )

        with open(output_path, "rb") as file:
            workbook_bytes = file.read()

        st.success(
            "CampaignOS Excel reporting package generated successfully."
        )

        st.download_button(
            label="⬇️ Download Excel Reporting Package",
            data=io.BytesIO(workbook_bytes),
            file_name="campaignos_reporting.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            width="stretch",
        )

    except Exception as exc:
        st.error(
            f"Unable to generate Excel workbook: {exc}"
        )


st.subheader("Operational Design")

st.markdown(
    """
### Executive Reporting

Provides a management-level view of campaign volume,
budget, engagement and conversion.

### Campaign Reporting

Provides campaign-level operational metrics suitable
for marketing operations reviews.

### Regional Reporting

Aggregates campaign outcomes by region for WW,
APAC, AMEA and Europe-style operating models.

### Lead Export

Provides a structured contact-level dataset that can
be consumed by downstream operational workflows.

### Deployment Model

CampaignOS remains vendor-neutral and synthetic-only.
The reporting package does not connect to Eloqua,
Salesforce, Outlook or any external business system.
"""
)

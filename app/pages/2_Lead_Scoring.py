import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.loader import load_contacts
from src.scoring.engine import score_contacts


st.set_page_config(
    page_title="CampaignOS | Lead Scoring",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Lead Scoring & Lifecycle")
st.caption(
    "Score synthetic contacts using engagement, lifecycle, profile and consent signals."
)

# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

contacts = load_contacts()

if contacts.empty:
    st.error("No contact data found.")
    st.stop()

# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------

st.sidebar.header("Scoring Filters")

regions = ["All"] + sorted(contacts["region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

lifecycle_values = [
    "All"
] + sorted(contacts["lifecycle_stage"].dropna().unique().tolist())
selected_lifecycle = st.sidebar.selectbox(
    "Lifecycle Stage",
    lifecycle_values,
)

minimum_score = st.sidebar.slider(
    "Minimum Lead Score",
    min_value=0,
    max_value=100,
    value=0,
)

# ---------------------------------------------------------------------
# Filter contacts
# ---------------------------------------------------------------------

filtered = contacts.copy()

if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]

if selected_lifecycle != "All":
    filtered = filtered[
        filtered["lifecycle_stage"] == selected_lifecycle
    ]

# ---------------------------------------------------------------------
# Score contacts
# ---------------------------------------------------------------------

scored = score_contacts(filtered)

scored = scored[
    scored["calculated_lead_score"] >= minimum_score
].copy()

# ---------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------

total_contacts = len(scored)

hot_count = int(
    (scored["score_band"] == "Hot").sum()
)

warm_count = int(
    (scored["score_band"] == "Warm").sum()
)

marketable_count = int(
    (scored["qualification"] != "Not Marketable").sum()
)

average_score = (
    round(scored["calculated_lead_score"].mean(), 1)
    if not scored.empty
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Scored Contacts", f"{total_contacts:,}")
col2.metric("Average Score", average_score)
col3.metric("Hot Leads", f"{hot_count:,}")
col4.metric("Marketable Leads", f"{marketable_count:,}")

# ---------------------------------------------------------------------
# Score distribution
# ---------------------------------------------------------------------

st.subheader("Lead Score Distribution")

if scored.empty:
    st.info("No contacts match the selected filters.")
    st.stop()

distribution = (
    scored["score_band"]
    .value_counts()
    .reindex(
        ["Hot", "Warm", "Nurture", "Cold"],
        fill_value=0,
    )
)

chart_col, table_col = st.columns([2, 1])

with chart_col:
    st.bar_chart(distribution)

with table_col:
    distribution_df = distribution.rename("Contacts").reset_index()
    distribution_df.columns = ["Score Band", "Contacts"]

    distribution_df["Percentage"] = (
        distribution_df["Contacts"]
        / distribution_df["Contacts"].sum()
        * 100
    ).round(1)

    st.dataframe(
        distribution_df,
        width="stretch",
        hide_index=True,
    )

# ---------------------------------------------------------------------
# Regional scoring
# ---------------------------------------------------------------------

st.subheader("Regional Lead Quality")

regional = (
    scored.groupby("region")
    .agg(
        Contacts=("contact_id", "count"),
        Average_Score=("calculated_lead_score", "mean"),
        Hot_Leads=("score_band", lambda x: (x == "Hot").sum()),
    )
    .reset_index()
)

regional["Average_Score"] = regional["Average_Score"].round(1)

st.dataframe(
    regional,
    width="stretch",
    hide_index=True,
)

# ---------------------------------------------------------------------
# Contact-level scoring
# ---------------------------------------------------------------------

st.subheader("Contact-Level Scoring")

display_columns = [
    "contact_id",
    "first_name",
    "last_name",
    "job_title",
    "country",
    "region",
    "industry",
    "lifecycle_stage",
    "engagement_score",
    "calculated_lead_score",
    "score_band",
    "qualification",
    "recommended_action",
]

available_columns = [
    column
    for column in display_columns
    if column in scored.columns
]

display_df = scored[available_columns].sort_values(
    "calculated_lead_score",
    ascending=False,
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)

# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------

csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Export Scored Contacts",
    data=csv_data,
    file_name="campaignos_scored_contacts.csv",
    mime="text/csv",
)

# ---------------------------------------------------------------------
# Business interpretation
# ---------------------------------------------------------------------

st.subheader("Marketing Action Guidance")

st.markdown(
    """
**Hot:** Prioritize for sales follow-up or high-intent nurture.

**Warm:** Continue targeted engagement and monitor progression.

**Nurture:** Build engagement through relevant content and journeys.

**Cold:** Reduce outbound pressure and revisit qualification later.

**Not Marketable:** Suppress from outbound campaigns when consent requirements are not satisfied.
"""
)
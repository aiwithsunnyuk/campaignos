import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from src.data.loader import load_all
from src.analytics.metrics import campaign_metrics, regional_activity

st.set_page_config(page_title="CampaignOS", page_icon="📣", layout="wide")

st.markdown(
    '''
    <style>
    .main-title {font-size:2.4rem;font-weight:700;margin-bottom:0;}
    .subtitle {color:#6b7280;font-size:1.05rem;margin-top:.2rem;}
    .section {font-size:1.25rem;font-weight:650;margin-top:1.5rem;}
    </style>
    ''',
    unsafe_allow_html=True,
)

data = load_all()
contacts, accounts = data["contacts"], data["accounts"]
campaigns, activities = data["campaigns"], data["activities"]

st.markdown('<div class="main-title">📣 CampaignOS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Marketing Automation Command Center • Milestone 1 Foundation</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Campaign Filters")
    regions = ["All"] + sorted(contacts["region"].dropna().unique().tolist()) if not contacts.empty else ["All"]
    businesses = ["All"] + sorted(campaigns["business_type"].dropna().unique().tolist()) if not campaigns.empty else ["All"]
    region = st.selectbox("Region", regions)
    business = st.selectbox("Business Type", businesses)
    st.divider()
    st.caption("Synthetic data only")
    st.caption("No external credentials required")

filtered_contacts = contacts.copy()
filtered_campaigns = campaigns.copy()
if region != "All":
    filtered_contacts = filtered_contacts[filtered_contacts["region"] == region]
    filtered_campaigns = filtered_campaigns[filtered_campaigns["region"] == region]
if business != "All":
    filtered_campaigns = filtered_campaigns[filtered_campaigns["business_type"] == business]

m = campaign_metrics(activities)
active = int((filtered_campaigns["status"] == "Running").sum()) if not filtered_campaigns.empty else 0
mqls = int((filtered_contacts["lifecycle_stage"] == "MQL").sum()) if not filtered_contacts.empty else 0

cols = st.columns(4)
cols[0].metric("Active Campaigns", active)
cols[1].metric("Contacts", f"{len(filtered_contacts):,}")
cols[2].metric("MQLs", f"{mqls:,}")
cols[3].metric("Conversion Rate", f"{m['conversion_rate']*100:.1f}%")

st.markdown('<div class="section">Campaign Operations</div>', unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    st.subheader("Campaign Status")
    if not filtered_campaigns.empty:
        st.bar_chart(filtered_campaigns["status"].value_counts())
    else:
        st.info("No campaigns match the current filters.")

with right:
    st.subheader("Regional Activity")
    regional = regional_activity(activities, contacts)
    if region != "All":
        regional = regional[regional["region"] == region]
    if not regional.empty:
        st.bar_chart(regional.set_index("region"))
    else:
        st.info("No activity available.")

st.markdown('<div class="section">Engagement Funnel</div>', unsafe_allow_html=True)
funnel = pd.DataFrame({
    "Stage": ["Email Sent", "Email Opened", "Email Clicked", "Form Submitted"],
    "Volume": [m["sent"], m["opened"], m["clicked"], m["converted"]],
})
st.dataframe(funnel, width="stretch", hide_index=True)

st.markdown('<div class="section">Portfolio Scenarios</div>', unsafe_allow_html=True)
scenario_cols = st.columns(3)
scenarios = [
    ("🎓 Training & Education", "DevOps, Agentic AI, Gen AI, Azure DevOps, PMP, AI Scrum Master, Product Owner"),
    ("🏭 Industrial", "Farming machinery lead generation, product demos and regional dealer campaigns"),
    ("💼 Professional & Services", "Professional information products, SAP training, legal services and event businesses"),
]
for col, (title, desc) in zip(scenario_cols, scenarios):
    with col:
        st.subheader(title)
        st.write(desc)

st.divider()
st.caption(f"CampaignOS M1 • {len(contacts):,} contacts • {len(accounts):,} accounts • {len(campaigns):,} campaigns • {len(activities):,} activities")

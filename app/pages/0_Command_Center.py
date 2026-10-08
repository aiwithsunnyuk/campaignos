import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter

from src.lead_360.builder import Lead360Builder

from src.gtm_intelligence import GTMIntelligenceSnapshotBuilder

from src.marketing_intelligence import (
    MarketingIntelligenceEngine,
    CommandCenterSummaryBuilder,
)


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CampaignOS | Command Center",
    page_icon="🧭",
    layout="wide",
)


# ---------------------------------------------------------
# Tenant
# ---------------------------------------------------------

TENANT_ID = "reetha"
TENANT_NAME = "Reetha IT Hub"
DATA_MODE = "Synthetic"


# ---------------------------------------------------------
# Reetha data → Lead 360
# ---------------------------------------------------------

@st.cache_data
def load_reetha_lead_360():
    base = ROOT / "data" / "reetha"

    leads = CSVLeadAdapter(
        TENANT_ID,
        base / "leads.csv",
    ).load()

    engagements = CSVEngagementAdapter(
        TENANT_ID,
        base / "engagements.csv",
    ).load()

    registrations = CSVRegistrationAdapter(
        TENANT_ID,
        base / "registrations.csv",
    ).load()

    enrollments = CSVEnrollmentAdapter(
        TENANT_ID,
        base / "enrollments.csv",
    ).load()

    return Lead360Builder(
        tenant_id=TENANT_ID,
    ).build(
        leads=leads,
        engagements=engagements,
        registrations=registrations,
        enrollments=enrollments,
    )


# ---------------------------------------------------------
# M12 intelligence pipeline
# ---------------------------------------------------------

@st.cache_data
def build_command_center_summary():
    lead_360_records = load_reetha_lead_360()

    snapshot = GTMIntelligenceSnapshotBuilder(
        tenant_id=TENANT_ID,
    ).build(
        records=lead_360_records,
    )

    intelligence = MarketingIntelligenceEngine().build(
        snapshot,
    )

    return CommandCenterSummaryBuilder().build(
        intelligence,
    )


summary = build_command_center_summary()


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .command-title {
        font-size: 2.35rem;
        font-weight: 750;
        margin-bottom: 0;
    }

    .command-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-top: .15rem;
    }

    .tenant-strip {
        padding: .7rem 1rem;
        border-radius: .65rem;
        background: rgba(49, 51, 63, .08);
        margin: 1rem 0 1.25rem 0;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: .75rem;
    }

    .feed-card {
        padding: 1rem 1.2rem;
        border-radius: .7rem;
        border: 1px solid rgba(128, 128, 128, .25);
        margin-bottom: .75rem;
    }

    .critical {
        border-left: 5px solid #dc2626;
    }

    .high {
        border-left: 5px solid #ea580c;
    }

    .medium {
        border-left: 5px solid #ca8a04;
    }

    .low {
        border-left: 5px solid #16a34a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="command-title">🧭 CampaignOS</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="command-subtitle">'
    'GTM Command Center • Marketing Intelligence'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="tenant-strip">
        <strong>Tenant:</strong> {TENANT_NAME}
        &nbsp;&nbsp;•&nbsp;&nbsp;
        <strong>Data mode:</strong> {DATA_MODE}
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">Executive Snapshot</div>',
    unsafe_allow_html=True,
)

kpis = {k.key: k for k in summary.kpis}

kpi_cols = st.columns(4, gap="medium")

kpi_cols[0].metric(
    "Total Leads",
    f"{kpis['total_leads'].value:,}",
    border=True,
)

kpi_cols[1].metric(
    "Engaged Leads",
    f"{kpis['engaged_leads'].value:,}",
    border=True,
)

kpi_cols[2].metric(
    "Registered Leads",
    f"{kpis['registered_leads'].value:,}",
    border=True,
)

kpi_cols[3].metric(
    "Enrolled Leads",
    f"{kpis['enrolled_leads'].value:,}",
    border=True,
)


# ---------------------------------------------------------
# Conversion metrics
# ---------------------------------------------------------

conversion_cols = st.columns(3, gap="medium")

conversion_cols[0].metric(
    "Engagement Rate",
    f"{kpis['engagement_rate'].value:.1f}%",
    border=True,
)

conversion_cols[1].metric(
    "Registration Rate",
    f"{kpis['registration_rate'].value:.1f}%",
    border=True,
)

conversion_cols[2].metric(
    "Enrollment Rate",
    f"{kpis['enrollment_rate'].value:.1f}%",
    border=True,
)


# ---------------------------------------------------------
# Intelligence headline
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">What needs attention?</div>',
    unsafe_allow_html=True,
)

st.info(summary.headline)


# ---------------------------------------------------------
# Funnel
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">GTM Funnel</div>',
    unsafe_allow_html=True,
)

funnel_cols = st.columns(4, gap="small")

funnel_values = [
    ("Leads", kpis["total_leads"].value),
    ("Engaged", kpis["engaged_leads"].value),
    ("Registered", kpis["registered_leads"].value),
    ("Enrolled", kpis["enrolled_leads"].value),
]

for col, (label, value) in zip(funnel_cols, funnel_values):
    with col:
        st.metric(
            label,
            f"{value:,}",
            border=True,
        )


# ---------------------------------------------------------
# Intelligence feed
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">Intelligence Feed</div>',
    unsafe_allow_html=True,
)

for item in summary.intelligence_feed:
    priority = item.priority

    icon = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }.get(priority, "🔵")

    evidence_html = "".join(
        f"<li>{evidence}</li>"
        for evidence in item.evidence
    )

    st.markdown(
        f"""
        <div class="feed-card {priority}">
            <strong>{icon} {item.title}</strong>
            <br>
            <strong>{item.metric}:</strong> {item.value}
            <br><br>
            <strong>Evidence</strong>
            <ul>
                {evidence_html}
            </ul>
            <strong>Recommended direction:</strong>
            {item.recommendation}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "CampaignOS M12 • Reetha IT Hub • "
    "Synthetic intelligence dataset • "
    "No external systems contacted"
)

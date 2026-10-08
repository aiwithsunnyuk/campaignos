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


# =========================================================
# Configuration
# =========================================================

TENANT_ID = "reetha"
TENANT_NAME = "Reetha IT Hub"
DATA_MODE = "Synthetic"


st.set_page_config(
    page_title="CampaignOS | Command Center",
    page_icon="🧭",
    layout="wide",
)


# =========================================================
# Data pipeline
# =========================================================

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


@st.cache_data
def build_command_center_summary():
    records = load_reetha_lead_360()

    snapshot = GTMIntelligenceSnapshotBuilder(
        tenant_id=TENANT_ID,
    ).build(
        records=records,
    )

    intelligence = MarketingIntelligenceEngine().build(
        snapshot,
    )

    return CommandCenterSummaryBuilder().build(
        intelligence,
    )


summary = build_command_center_summary()
kpis = {k.key: k for k in summary.kpis}


# =========================================================
# Styling
# =========================================================

st.markdown(
    """
    <style>

    .command-title {
        font-size: 2.35rem;
        font-weight: 750;
        line-height: 1.05;
        margin-bottom: 0;
    }

    .command-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-top: .25rem;
    }

    .tenant-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: .7rem 1rem;
        margin: 1rem 0 1.4rem 0;
        border-radius: .65rem;
        background: rgba(49, 51, 63, .07);
        font-size: .9rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: .7rem;
    }

    .section-caption {
        color: #6b7280;
        font-size: .85rem;
        margin-bottom: .75rem;
    }

    .priority-card {
        padding: 1.25rem;
        border-radius: .75rem;
        border: 1px solid rgba(220, 38, 38, .35);
        background: rgba(220, 38, 38, .06);
        min-height: 185px;
    }

    .priority-label {
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .05em;
        text-transform: uppercase;
    }

    .priority-title {
        font-size: 1.25rem;
        font-weight: 750;
        margin-top: .45rem;
    }

    .priority-value {
        font-size: 2rem;
        font-weight: 750;
        margin-top: .25rem;
    }

    .conversion-card {
        padding: 1.25rem;
        border-radius: .75rem;
        border: 1px solid rgba(128, 128, 128, .25);
        min-height: 185px;
    }

    .conversion-row {
        display: flex;
        justify-content: space-between;
        padding: .45rem 0;
        border-bottom: 1px solid rgba(128, 128, 128, .15);
    }

    .conversion-row:last-child {
        border-bottom: none;
    }

    .conversion-value {
        font-weight: 750;
    }

    .funnel-row {
        display: grid;
        grid-template-columns: 95px 1fr 60px;
        align-items: center;
        gap: .75rem;
        margin-bottom: .65rem;
    }

    .funnel-label {
        font-size: .9rem;
        font-weight: 600;
    }

    .funnel-track {
        height: 22px;
        border-radius: 5px;
        background: rgba(128, 128, 128, .13);
        overflow: hidden;
    }

    .funnel-fill {
        height: 100%;
        border-radius: 5px;
        background: rgba(49, 51, 63, .65);
    }

    .funnel-fill.bottleneck {
        background: rgba(220, 38, 38, .75);
    }

    .funnel-number {
        text-align: right;
        font-weight: 700;
    }

    .next-action {
        padding: 1.25rem;
        border-radius: .75rem;
        border: 1px solid rgba(49, 51, 63, .25);
        background: rgba(49, 51, 63, .04);
    }

    .next-action-title {
        font-size: 1.2rem;
        font-weight: 750;
        margin-bottom: .4rem;
    }

    .next-action-priority {
        display: inline-block;
        padding: .2rem .55rem;
        border-radius: 999px;
        font-size: .72rem;
        font-weight: 750;
        text-transform: uppercase;
        background: rgba(220, 38, 38, .12);
    }

    .feed-card {
        padding: 1rem 1.15rem;
        border-radius: .7rem;
        border: 1px solid rgba(128, 128, 128, .25);
        margin-bottom: .7rem;
    }

    .feed-card.critical {
        border-left: 5px solid #dc2626;
    }

    .feed-card.high {
        border-left: 5px solid #ea580c;
    }

    .feed-card.medium {
        border-left: 5px solid #ca8a04;
    }

    .feed-card.low {
        border-left: 5px solid #16a34a;
    }

    .feed-title {
        font-weight: 750;
    }

    .feed-meta {
        color: #6b7280;
        font-size: .85rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="command-title">🧭 CampaignOS</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="command-subtitle">'
    'GTM Command Center · Marketing Intelligence'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="tenant-strip">
        <span><strong>Tenant:</strong> {TENANT_NAME}</span>
        <span><strong>Data:</strong> {DATA_MODE}</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Executive KPI layer
# =========================================================

st.markdown(
    '<div class="section-title">Executive Snapshot</div>',
    unsafe_allow_html=True,
)

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


# =========================================================
# GTM Funnel
# =========================================================

st.markdown(
    '<div class="section-title">GTM Funnel</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-caption">'
    'Lead progression through engagement, registration and enrollment.'
    '</div>',
    unsafe_allow_html=True,
)

funnel = [
    ("Leads", int(kpis["total_leads"].value)),
    ("Engaged", int(kpis["engaged_leads"].value)),
    ("Registered", int(kpis["registered_leads"].value)),
    ("Enrolled", int(kpis["enrolled_leads"].value)),
]

max_value = max(value for _, value in funnel)

for label, value in funnel:
    width = (value / max_value) * 100 if max_value else 0
    bottleneck = label == "Registered"

    css_class = "funnel-fill bottleneck" if bottleneck else "funnel-fill"

    st.markdown(
        f"""
        <div class="funnel-row">
            <div class="funnel-label">{label}</div>
            <div class="funnel-track">
                <div class="{css_class}" style="width:{width:.1f}%"></div>
            </div>
            <div class="funnel-number">{value:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Priority + Conversion
# =========================================================

st.markdown(
    '<div class="section-title">Decision Snapshot</div>',
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="medium")

with left:
    registration_rate = float(kpis["registration_rate"].value)

    st.html(
        f"""
<div class="priority-card">
    <div class="priority-label">🚨 Priority</div>
    <div class="priority-title">Registration bottleneck</div>
    <div class="priority-value">{registration_rate:.1f}%</div>
    <div>engaged-to-registration conversion</div>
</div>
"""
    )

with right:
    engagement_rate = float(kpis["engagement_rate"].value)
    enrollment_rate = float(kpis["enrollment_rate"].value)

    st.html(
        f"""
<div class="conversion-card">
    <strong>📊 Conversion Performance</strong>

    <div class="conversion-row">
        <span>Engagement</span>
        <span class="conversion-value">{engagement_rate:.1f}%</span>
    </div>

    <div class="conversion-row">
        <span>Registration</span>
        <span class="conversion-value">{registration_rate:.1f}%</span>
    </div>

    <div class="conversion-row">
        <span>Enrollment</span>
        <span class="conversion-value">{enrollment_rate:.1f}%</span>
    </div>
</div>
"""
    )


# =========================================================
# Next Best Action preview
# =========================================================

st.markdown(
    '<div class="section-title">🎯 What Should Happen Next?</div>',
    unsafe_allow_html=True,
)

st.html(
    f"""
<div class="next-action">
    <span class="next-action-priority">High Priority</span>

    <div class="next-action-title">
        Prioritize registration conversion
    </div>

    <div>
        The current funnel indicates that registration is the
        primary conversion bottleneck.
    </div>

    <br>

    <strong>Evidence</strong><br>
    {int(kpis["engaged_leads"].value):,} engaged leads
    →
    {int(kpis["registered_leads"].value):,} registered leads
    →
    {registration_rate:.2f}% conversion
</div>
"""
)


# =========================================================
# Intelligence Feed
# =========================================================

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

    st.html(
        f"""
<div class="feed-card {priority}">
    <div class="feed-title">
        {icon} {item.title}
    </div>

    <div class="feed-meta">
        {item.metric}: {item.value}
    </div>

    <br>

    <strong>Evidence</strong>
    <ul>
        {evidence_html}
    </ul>

    <strong>Recommended direction:</strong>
    {item.recommendation}
</div>
"""
    )


# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "CampaignOS M12 · Reetha IT Hub · "
    "Synthetic intelligence dataset · "
    "No external systems contacted"
)

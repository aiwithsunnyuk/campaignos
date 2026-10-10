from src.reetha_content_studio import render_content_studio
from src.reetha_campaign_planner import render_campaign_planner
from src.reetha_audience_builder import render_ai_audience_builder
from src.reetha_sap_audience_intelligence import render_sap_audience_intelligence
from src.reetha_campaign_opportunities import render_campaign_opportunity_engine
from src.reetha_command_center import render_reetha_business_surface
from src.reetha_demand_intelligence import render_reetha_demand_intelligence
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.reetha_command_center import render_reetha_business_surface
from src.reetha_demand_intelligence import render_reetha_demand_intelligence
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st


from src.lead_360.builder import Lead360Builder
from src.lead_360 import Lead360Service
from src.auth.users import get_user
from src.gtm_intelligence import GTMIntelligenceSnapshotBuilder
from src.marketing_intelligence import (
    MarketingIntelligenceEngine,
    CommandCenterSummaryBuilder,
)
from src.next_best_action import LeadNextBestActionService
from datetime import datetime, timezone

from src.session import get_session
from src.workspace import TenantWorkspaceService

from src.data_sources import (
    DataSourceAdapterFactory,
    TenantDataService,
    build_default_registry,
)
from src.ai_governance.lead_action_service import LeadActionGovernanceService
from src.ai_governance.action_lifecycle import GovernedAction
from src.ai_governance.lifecycle_audit import LifecycleAuditRecorder
from src.ai_governance.execution_audit import ExecutionAuditRecorder
from src.ai_governance.decision_trace_service import DecisionTraceService
from src.execution.dry_run import DryRunExecutionAdapter


# =========================================================
# Configuration
# =========================================================

session = get_session()

if session is None:
    st.warning("Please sign in through the CampaignOS Login page.")
    st.stop()

workspace = TenantWorkspaceService().resolve(session)
TENANT_ID = workspace.tenant_id
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
def load_reetha_source_records():
    service = TenantDataService(
        registry=build_default_registry(),
        factory=DataSourceAdapterFactory(),
        base_path=ROOT / "data" / "reetha",
    )

    data = service.load_reetha()

    return (
        data["leads"],
        data["engagements"],
        data["registrations"],
        data["enrollments"],
    )


@st.cache_data
def load_reetha_lead_360():
    leads, engagements, registrations, enrollments = (
        load_reetha_source_records()
    )

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

# Demo users representing the governed operating model.
# Marketing generates recommendations; the director approves them.
current_user = get_user("reetha-marketing")
approver_user = get_user("reetha-director")

source_leads, source_engagements, source_registrations, source_enrollments = (
    load_reetha_source_records()
)

lead_ids = [lead.lead_id for lead in source_leads]

selected_lead_id = st.selectbox(
    "Select Lead",
    options=lead_ids,
    index=0,
)

# Prevent governed actions or dry-run results from leaking
# across lead selections.
existing_governed_action = st.session_state.get("governed_action")

if (
    existing_governed_action is not None
    and existing_governed_action.lead_id != selected_lead_id
):
    st.session_state.pop("governed_action", None)
    st.session_state.pop("dry_run_result", None)
    st.session_state.pop("decision_events", None)

lead_360 = Lead360Service().get_lead(
    user=current_user,
    tenant_id=TENANT_ID,
    lead_id=selected_lead_id,
    leads=source_leads,
    engagements=source_engagements,
    registrations=source_registrations,
    enrollments=source_enrollments,
)

lead_nba = LeadNextBestActionService().recommend(
    user=current_user,
    tenant_id=TENANT_ID,
    lead=lead_360,
)


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
# Lead-level Next Best Action
# =========================================================

st.markdown(
    '<div class="section-title">🎯 Next Best Action</div>',
    unsafe_allow_html=True,
)

nba_priority_class = {
    "high": "critical",
    "medium": "medium",
    "low": "low",
}.get(lead_nba.priority, "low")

evidence_html = "".join(
    f"<li>{evidence}</li>"
    for evidence in lead_nba.evidence
)

st.html(
    f"""
<div class="feed-card {nba_priority_class}">
    <div class="feed-title">
        {lead_nba.priority.upper()} · {lead_nba.action_type}
    </div>

    <div class="next-action-title">
        {lead_nba.recommendation}
    </div>

    <div>
        {lead_nba.reason}
    </div>

    <br>

    <strong>Evidence</strong>
    <ul>
        {evidence_html}
    </ul>
</div>
"""
)


# =========================================================
# Governed Action + Decision Trace
# =========================================================

st.markdown(
    '<div class="section-title">🛡️ Governed Action</div>',
    unsafe_allow_html=True,
)

if "governed_action" not in st.session_state:
    st.session_state.governed_action = None

if "decision_events" not in st.session_state:
    st.session_state.decision_events = []

if "dry_run_result" not in st.session_state:
    st.session_state.dry_run_result = None

governance = LeadActionGovernanceService()
lifecycle_audit = LifecycleAuditRecorder()
execution_audit = ExecutionAuditRecorder()
decision_trace_service = DecisionTraceService()

governed_action = st.session_state.governed_action


def audit_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_lifecycle_event(action, actor_id: str) -> None:
    event = lifecycle_audit.record(
        action=action,
        event_id=(
            f"AUD-{action.action_id}-"
            f"{action.status.upper()}-"
            f"{len(st.session_state.decision_events) + 1}"
        ),
        actor_id=actor_id,
        timestamp=audit_timestamp(),
    )

    st.session_state.decision_events.append(event)


if governed_action is None:

    st.info(
        "AI recommendation is advisory. "
        "No external system will be contacted."
    )

    if st.button(
        "Submit for Approval",
        type="primary",
        key="submit_governed_action",
    ):

        governed_action = governance.create_governed_action(
            user=current_user,
            action=lead_nba,
        )

        st.session_state.governed_action = governed_action
        st.session_state.decision_events = []
        st.session_state.dry_run_result = None

        append_lifecycle_event(
            action=governed_action,
            actor_id=current_user.user_id,
        )

        st.rerun()

else:

    status_label = governed_action.status.replace(
        "_",
        " ",
    ).title()

    st.html(
        f"""
<div class="conversion-card">
    <strong>Governed Action</strong>

    <div class="conversion-row">
        <span>Action ID</span>
        <span class="conversion-value">
            {governed_action.action_id}
        </span>
    </div>

    <div class="conversion-row">
        <span>Lead</span>
        <span class="conversion-value">
            {governed_action.lead_id}
        </span>
    </div>

    <div class="conversion-row">
        <span>Action</span>
        <span class="conversion-value">
            {governed_action.action_type}
        </span>
    </div>

    <div class="conversion-row">
        <span>Status</span>
        <span class="conversion-value">
            {status_label}
        </span>
    </div>
</div>
"""
    )

    if governed_action.status == "pending_approval":

        st.warning(
            "Approval required. The marketing recommendation has not "
            "been executed."
        )

        approval_left, approval_right = st.columns(
            2,
            gap="medium",
        )

        with approval_left:

            if st.button(
                "Approve Action",
                type="primary",
                key="approve_governed_action",
            ):

                approved_action = governance.approve_action(
                    user=approver_user,
                    action=governed_action,
                )

                st.session_state.governed_action = approved_action

                append_lifecycle_event(
                    action=approved_action,
                    actor_id=approver_user.user_id,
                )

                st.rerun()

        with approval_right:

            if st.button(
                "Reject Action",
                key="reject_governed_action",
            ):

                rejected_action = governance.reject_action(
                    user=approver_user,
                    action=governed_action,
                )

                st.session_state.governed_action = rejected_action

                append_lifecycle_event(
                    action=rejected_action,
                    actor_id=approver_user.user_id,
                )

                st.rerun()

    elif governed_action.status == "approved":

        st.success(
            f"Approved by {governed_action.approved_by}. "
            "The action is approved but has not been executed."
        )

        if st.button(
            "Prepare for Execution",
            type="primary",
            key="prepare_governed_action",
        ):

            ready_action = governance.prepare_for_execution(
                user=approver_user,
                action=governed_action,
            )

            st.session_state.governed_action = ready_action

            append_lifecycle_event(
                action=ready_action,
                actor_id=approver_user.user_id,
            )

            st.rerun()

    elif governed_action.status == "ready_for_execution":

        st.warning(
            "Ready for execution. The next step is a dry-run only."
        )

        if st.button(
            "Run Dry Run",
            type="primary",
            key="dry_run_governed_action",
        ):

            execution_id = (
                f"EXEC-{governed_action.tenant_id.upper()}-"
                f"{governed_action.lead_id}"
            )

            execution_result = DryRunExecutionAdapter().execute(
                action=governed_action,
                execution_id=execution_id,
            )

            st.session_state.dry_run_result = execution_result

            execution_event = execution_audit.record(
                action=governed_action,
                result=execution_result,
                event_id=f"AUD-{execution_id}",
                actor_id=approver_user.user_id,
                timestamp=audit_timestamp(),
            )

            st.session_state.decision_events.append(
                execution_event
            )

            st.rerun()

        if st.session_state.get("dry_run_result"):

            result = st.session_state.dry_run_result

            st.success(
                f"Dry-run completed. {result.message}"
            )

    elif governed_action.status == "rejected":

        st.error(
            "Action rejected. No external action was executed."
        )


# =========================================================
# Decision Trace
# =========================================================

if (
    governed_action is not None
    and st.session_state.decision_events
):

    st.markdown(
        '<div class="section-title">🔎 Decision Trace</div>',
        unsafe_allow_html=True,
    )

    trace = decision_trace_service.build_trace(
        user=current_user,
        action=governed_action,
        events=tuple(
            st.session_state.decision_events
        ),
    )

    st.html(
        f"""
<div class="conversion-card">
    <strong>Why did CampaignOS recommend this action?</strong>

    <div class="conversion-row">
        <span>Tenant</span>
        <span class="conversion-value">
            {trace.tenant_id}
        </span>
    </div>

    <div class="conversion-row">
        <span>Lead</span>
        <span class="conversion-value">
            {trace.lead_id}
        </span>
    </div>

    <div class="conversion-row">
        <span>Action</span>
        <span class="conversion-value">
            {trace.action_id}
        </span>
    </div>
</div>
"""
    )

    for index, event in enumerate(trace.events, start=1):

        event_label = event.event_type.replace(
            "_",
            " ",
        ).title()

        evidence_html = "".join(
            f"<li>{evidence}</li>"
            for evidence in event.evidence
        )

        st.html(
            f"""
<div class="feed-card medium">
    <div class="feed-title">
        {index}. {event_label}
    </div>

    <div class="feed-meta">
        Actor: {event.actor_id}
        · {event.timestamp}
    </div>

    <br>

    <strong>Decision</strong>
    <div>{event.decision}</div>

    <br>

    <strong>Reason</strong>
    <div>{event.reason}</div>

    <br>

    <strong>Evidence</strong>
    <ul>
        {evidence_html}
    </ul>
</div>
"""
        )


st.caption(
    "Governance: recommendation → approval → readiness → dry run. "
    "Decision Trace records the governed lifecycle and execution result. "
    "External execution is intentionally disabled."
)


render_reetha_business_surface()

render_campaign_opportunity_engine()

render_ai_audience_builder()

render_sap_audience_intelligence()
render_campaign_planner()

render_reetha_demand_intelligence()
# Lead 360
st.html(
    f"""


    <div class="section-title">👤 Lead 360 · {lead_360.lead_id}</div>

    <div class="decision-card">
        <div class="decision-card-header">
            <div>
                <div class="decision-label">LEAD INTELLIGENCE</div>
                <div class="decision-title">{lead_360.lead_id}</div>
            </div>
            <div class="decision-badge">REETHA</div>
        </div>

        <div class="decision-grid">
            <div>
                <div class="metric-label">Lead Score</div>
                <div class="metric-value">{lead_360.lead_score}</div>
            </div>

            <div>
                <div class="metric-label">Engagements</div>
                <div class="metric-value">{lead_360.total_engagements}</div>
            </div>

            <div>
                <div class="metric-label">Campaigns</div>
                <div class="metric-value">{lead_360.unique_campaigns}</div>
            </div>

            <div>
                <div class="metric-label">Courses</div>
                <div class="metric-value">{lead_360.unique_courses}</div>
            </div>

            <div>
                <div class="metric-label">Registrations</div>
                <div class="metric-value">{lead_360.registration_count}</div>
            </div>

            <div>
                <div class="metric-label">Enrollments</div>
                <div class="metric-value">{lead_360.enrollment_count}</div>
            </div>
        </div>

        <div class="evidence-box">
            <div class="evidence-title">Lead Evidence</div>

            <div class="evidence-item">
                Engagement channels:
                {", ".join(lead_360.engagement_channels) or "None"}
            </div>

            <div class="evidence-item">
                Event types:
                {", ".join(lead_360.engagement_event_types) or "None"}
            </div>

            <div class="evidence-item">
                Last engagement:
                {lead_360.last_engagement_at or "Unknown"}
            </div>
        </div>
    </div>
    """
)

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

# M13.6 · AI Content Studio

render_content_studio()

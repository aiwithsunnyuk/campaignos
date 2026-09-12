from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.approval import ApprovalStatus, HumanApprovalService
from src.agent.campaign_context import build_campaign_context
from src.agent.models import AgentRequest, DecisionStatus
from src.agent.orchestrator import CampaignAgentOrchestrator


DATA_DIR = ROOT / "data" / "synthetic"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    campaigns = pd.read_csv(DATA_DIR / "campaigns.csv")
    contacts = pd.read_csv(DATA_DIR / "contacts.csv")
    activities = pd.read_csv(DATA_DIR / "activities.csv")
    return campaigns, contacts, activities


st.set_page_config(
    page_title="CampaignOS | Agentic Campaign Operations",
    page_icon="🤖",
    layout="wide",
)

campaigns, contacts, activities = load_data()

st.title("🤖 Agentic Campaign Operations")
st.caption(
    "Analyze campaign signals, generate explainable decisions, and route them "
    "through human approval. No external systems are executed."
)

with st.sidebar:
    st.header("Agent Configuration")
    campaign_name = st.selectbox(
        "Campaign",
        campaigns["campaign_name"].tolist(),
    )
    reviewer = st.text_input("Reviewer", value="Marketing Manager")
    approval_comment = st.text_area(
        "Review comment",
        value="",
        placeholder="Optional approval or rejection rationale",
    )

campaign = campaigns.loc[
    campaigns["campaign_name"] == campaign_name
].iloc[0]

context = build_campaign_context(campaign, contacts, activities)

request = AgentRequest(
    campaign_id=str(campaign["campaign_id"]),
    campaign_name=str(campaign["campaign_name"]),
    business_type=str(campaign["business_type"]),
    region=str(campaign["region"]),
    objective=str(campaign["objective"]),
    context=context,
)

plan = CampaignAgentOrchestrator().run(request, context)

st.subheader("Campaign Intelligence")

metric_cols = st.columns(5)
metric_cols[0].metric("Region", request.region)
metric_cols[1].metric("Open Rate", f"{context['open_rate']:.2%}")
metric_cols[2].metric("Click Rate", f"{context['click_rate']:.2%}")
metric_cols[3].metric("Conversion Rate", f"{context['conversion_rate']:.2%}")
metric_cols[4].metric("Avg Lead Score", f"{context['average_lead_score']:.1f}")

with st.expander("Campaign context", expanded=False):
    context_df = pd.DataFrame(
        [{"Signal": key, "Value": str(value)} for key, value in context.items()]
    )
    st.dataframe(context_df, width="stretch", hide_index=True)

st.subheader("Agent Plan")
st.info(plan.summary)

if not plan.decisions:
    st.success("No proposed actions were generated from the supplied signals.")

service = HumanApprovalService()
reviewed_decisions = []

for index, decision in enumerate(plan.decisions, start=1):
    st.markdown(f"### Decision {index}: {decision.decision_id}")

    left, right = st.columns([2, 1])
    with left:
        st.write(f"**Recommendation:** {decision.action.title}")
        st.write(f"**Reason:** {decision.reason}")
        st.write(
            f"**Priority:** {decision.action.priority}/5  ·  "
            f"**Confidence:** {decision.confidence:.0%}"
        )
    with right:
        evidence_df = pd.DataFrame(
            [{"Evidence": key, "Value": str(value)}
             for key, value in decision.evidence.items()]
        )
        st.dataframe(evidence_df, width="stretch", hide_index=True)

    approve = st.radio(
        f"Review {decision.decision_id}",
        ["Approve", "Reject"],
        key=f"review_{decision.decision_id}",
        horizontal=True,
    )

    if reviewer.strip():
        reviewed, _ = service.review(
            decision,
            approve=approve == "Approve",
            reviewer=reviewer,
            comment=approval_comment,
        )
        reviewed_decisions.append(reviewed)
    else:
        reviewed_decisions.append(decision)

st.divider()
st.subheader("Human Approval Summary")

if plan.decisions and reviewer.strip():
    action_plan = service.build_action_plan(
        plan,
        reviewed_decisions,
        reviewer=reviewer,
    )

    summary_cols = st.columns(4)
    summary_cols[0].metric("Review Status", action_plan.status.value)
    summary_cols[1].metric("Approved Actions", action_plan.action_count)
    summary_cols[2].metric(
        "Rejected Decisions",
        len(action_plan.rejected_decision_ids),
    )
    summary_cols[3].metric(
        "Execution Ready",
        "Yes" if action_plan.ready_for_execution else "No",
    )

    if action_plan.status == ApprovalStatus.APPROVED:
        st.success(
            "All proposed decisions are approved. The action plan is execution-ready "
            "but CampaignOS does not execute external actions."
        )
    elif action_plan.status == ApprovalStatus.PENDING:
        st.warning(
            "The plan contains a mixture of approved and rejected decisions. "
            "It is not execution-ready."
        )
    else:
        st.error("All proposed decisions were rejected. Nothing is execution-ready.")

    if action_plan.actions:
        action_df = pd.DataFrame(
            [
                {
                    "Decision": action.decision_id,
                    "Action": action.title,
                    "Priority": action.priority,
                    "Owner": action.owner,
                }
                for action in action_plan.actions
            ]
        )
        st.dataframe(action_df, width="stretch", hide_index=True)

elif plan.decisions:
    st.warning("Enter a reviewer name to complete the human approval workflow.")
else:
    st.info("No approval workflow is required because there are no proposed actions.")

st.caption(
    "Safety boundary: CampaignOS creates recommendations and execution-ready "
    "plans only. It does not send email, update Eloqua/Salesforce, access Outlook, "
    "or modify live campaigns."
)

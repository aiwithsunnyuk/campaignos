"""M11.6 Create Training Campaign Streamlit page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.campaign_builder import (
    CAMPAIGN_TYPES,
    CHANNELS,
    OBJECTIVES,
    build_training_campaign,
    campaign_brief,
    execution_plan,
    render_training_message,
)
from src.training.models import TrainingProgram


st.set_page_config(page_title="Create Training Campaign", page_icon="📣", layout="wide")

st.title("📣 Create Training Campaign")
st.caption("M11.6 • Deterministic campaign creation for training-growth operations")

st.info(
    "CampaignOS uses synthetic data. This page prepares a campaign and content "
    "for human review. It does not send WhatsApp, email, or meeting invitations."
)

programs_path = ROOT / "data" / "training" / "hac_programs.csv"

if not programs_path.exists():
    st.error(f"Training catalogue not found: {programs_path}")
    st.stop()

catalogue = pd.read_csv(programs_path).fillna("")

if catalogue.empty:
    st.warning("No training programs are available.")
    st.stop()


def row_to_program(row: pd.Series) -> TrainingProgram:
    def split_list(value: str) -> list[str]:
        if pd.isna(value):
            return []
        return [item.strip() for item in str(value).split("|") if item.strip()]

    def first_available(*keys: str, default: str = "") -> str:
        for key in keys:
            if key in row.index and not pd.isna(row[key]):
                return str(row[key])
        return default

    program_id = first_available("program_id")
    program_name = first_available("program_name", "name", default=program_id)
    category = first_available("category")
    subcategory = first_available(
        "subcategory",
        default=category,
    )
    career_paths = split_list(
        first_available("career_paths")
    )
    target_personas = split_list(
        first_available("target_personas", "audience_tags")
    )
    tags = split_list(
        first_available("tags", "audience_tags")
    )
    delivery_mode = first_available(
        "delivery_mode",
        default="Verify with client",
    )

    return TrainingProgram(
        program_id=program_id,
        name=program_name,
        category=category,
        audience_tags=tuple(target_personas),
        career_paths=tuple(career_paths),
        delivery_mode=delivery_mode,
    )


program_map = {
    str(row["program_id"]): row_to_program(row)
    for _, row in catalogue.iterrows()
}

left, right = st.columns(2)

with left:
    selected_id = st.selectbox(
        "Training program",
        options=list(program_map),
        format_func=lambda value: program_map[value].program_name,
    )
    region = st.selectbox("Region", ["India", "Australia", "APAC", "Europe", "Global"])
    campaign_type = st.selectbox("Campaign type", CAMPAIGN_TYPES)
    objective = st.selectbox("Objective", OBJECTIVES)
    career_persona = st.text_input("Career persona", "DATA_SWITCHER")
    audience = st.text_area(
        "Audience",
        "Career switchers interested in data and cloud",
        height=90,
    )

with right:
    session_date = st.date_input("Session date")
    session_time = st.time_input("Session time")
    session_label = st.text_input("Session label", "Live training session")
    primary_channel = st.selectbox("Primary channel", CHANNELS, index=0)
    secondary_channel = st.selectbox("Secondary channel", CHANNELS, index=1)
    cta = st.text_input("CTA", "Join the introductory training session")
    delivery_mode = st.text_input("Delivery mode", "Verify with client")

st.divider()

if st.button("Create Campaign Plan", type="primary", width="stretch"):
    try:
        campaign = build_training_campaign(
            campaign_id="M11-6-UI-001",
            program=program_map[selected_id],
            region=region,
            session_label=session_label,
            channel=primary_channel,
            objective=objective,
            audience=audience,
            campaign_type=campaign_type,
            career_persona=career_persona,
            session_date=session_date.isoformat(),
            session_time=session_time.strftime("%H:%M"),
            delivery_mode=delivery_mode,
            secondary_channel=secondary_channel,
            cta=cta,
        )
    except (ValueError, KeyError) as exc:
        st.error(f"Campaign could not be created: {exc}")
        st.stop()

    st.success("Campaign plan validated and ready for human review.")

    st.subheader("Campaign Brief")
    brief = campaign_brief(campaign)
    brief_df = pd.DataFrame([{"Field": key.replace("_", " ").title(), "Value": value}
                             for key, value in brief.__dict__.items()])
    st.dataframe(brief_df, width="stretch", hide_index=True)

    st.subheader("Execution Plan")
    st.dataframe(pd.DataFrame(execution_plan(campaign)), width="stretch", hide_index=True)

    st.subheader("Training Funnel")
    st.write(" → ".join([
        "Community Reach",
        "Message View / Engagement",
        "Course Interest",
        "Session Registration",
        "Session Attendance",
        "Course Enquiry",
        "High Intent",
        "Counselling",
        "Enrolment",
    ]))

    st.subheader("Promotional Message Preview")
    st.code(
        render_training_message(
            campaign,
            contact_name="there",
            join_details="Synthetic session details",
        ),
        language="text",
    )

    st.warning(
        "Human approval boundary: CampaignOS prepares the plan and content only. "
        "Actual delivery must occur through an authorized external platform after review."
    )

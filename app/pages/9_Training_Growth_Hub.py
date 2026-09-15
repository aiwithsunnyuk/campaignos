"""M11.2 Training Growth Hub."""
from datetime import date
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.campaign_builder import build_training_campaign, render_training_message
from src.training.engine import recommend_programs
from src.training.personas import identify_persona
from src.training.models import TrainingLeadProfile, TrainingProgram

st.set_page_config(page_title="Training Growth Hub", page_icon="🎓", layout="wide")
st.title("Training Growth Hub")
st.caption("M11.2 • training campaign creation, career-path matching and programme catalogue")

catalog_path = ROOT / "data" / "training" / "hac_programs.csv"
if not catalog_path.exists():
    st.error("Training catalogue not found.")
    st.stop()

catalog = pd.read_csv(catalog_path).fillna("")
st.subheader("Hands-On Agile Coaching")
st.info(
    "Portfolio demonstration only. Programme names are based on the public catalogue; "
    "lead, schedule, contact and meeting data are synthetic."
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Programs", len(catalog))
m2.metric("Categories", catalog["category"].nunique())
m3.metric("Career paths", catalog["career_paths"].astype(str).str.split("|").explode().nunique())
m4.metric("Data boundary", "Synthetic")

tabs = st.tabs(["Create Today's Training Campaign", "Career Path Finder", "Programme Catalogue"])

programs = [
    TrainingProgram(
        program_id=row["program_id"],
        name=row["name"],
        category=row["category"],
        audience_tags=tuple(str(row["audience_tags"]).split("|")),
        career_paths=tuple(str(row["career_paths"]).split("|")),
        delivery_mode=row["delivery_mode"],
    )
    for row in catalog.to_dict("records")
]

with tabs[0]:
    st.subheader("Create Today's Training Campaign")
    st.caption("Model the operational workflow without sending messages or connecting to external systems.")
    name_to_program = {program.name: program for program in programs}
    selected_name = st.selectbox("Programme", list(name_to_program))
    selected_program = name_to_program[selected_name]

    c1, c2, c3 = st.columns(3)
    with c1:
        region = st.selectbox("Target region", ["India", "Australia", "APAC", "Europe", "AMEA", "Global"], index=0)
        channel = st.selectbox("Primary channel", ["WhatsApp Community", "Email", "Social", "Website"])
    with c2:
        session_date = st.date_input("Session date", value=date.today())
        session_time = st.text_input("Session time", value="6:30 AM")
    with c3:
        duration = st.text_input("Session duration", value="60 minutes")
        cta = st.selectbox("Call to action", ["Request course details", "Register for session", "Ask for counselling", "Explore programme"])

    audience = st.selectbox(
        "Audience strategy",
        ["Interested and opted-in prospects", "High-intent training leads", "Career switcher audience", "Recent session attendees", "Re-engagement audience"],
    )

    if st.button("Build Campaign Draft", type="primary", width="stretch"):
        session_label = f"{session_date.strftime('%d %b %Y')} • {session_time} • {duration}"
        campaign = build_training_campaign(
            campaign_id=f"M11-{session_date.strftime('%Y%m%d')}-{selected_program.program_id}",
            program=selected_program,
            region=region,
            session_label=session_label,
            channel=channel,
            audience=audience,
            cta=cta,
        )
        st.session_state["m11_campaign"] = campaign

    campaign = st.session_state.get("m11_campaign")
    if campaign:
        st.divider()
        st.subheader("Campaign Draft")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Status", campaign.status)
        k2.metric("Channel", campaign.primary_channel)
        k3.metric("Region", campaign.region)
        k4.metric("Objective", campaign.objective)

        d1, d2 = st.columns([1, 1])
        with d1:
            st.markdown(f"**Campaign**  \n{campaign.campaign_name}")
            st.markdown(f"**Audience**  \n{campaign.audience}")
            st.markdown(f"**Session**  \n{campaign.session_label}")
            st.markdown(f"**CTA**  \n{campaign.cta}")
        with d2:
            st.markdown("**Synthetic message preview**")
            st.code(
                render_training_message(
                    campaign, selected_program, contact_name="there",
                    join_details="Join details intentionally omitted from the public portfolio.",
                ),
                language="text",
            )

        st.warning(
            "Governance boundary: this page creates a campaign draft and message preview only. "
            "It does not send WhatsApp/email messages or expose real meeting credentials."
        )

with tabs[1]:
    st.subheader("Career Path Finder")
    left, right = st.columns([1, 1])
    with left:
        background = st.selectbox("Current background", ["career switcher", "IT professional", "student", "manager", "business professional"])
        goal = st.selectbox("Career goal", ["data engineering", "data analytics", "AI", "cybersecurity", "DevOps", "Scrum Master", "Product Owner", "project management", "software testing", "digital marketing"])
        interest = st.selectbox("Primary interest", ["Azure", "Python", "Power BI", "AI", "Cybersecurity", "DevOps", "Agile", "Business Analysis", "PMP", "Data Science"])
        experience = st.selectbox("Experience level", ["beginner", "intermediate", "advanced"])
        if st.button("Find Recommended Learning Paths", width="stretch"):
            profile = TrainingLeadProfile(background=background, career_goal=goal, interest=interest, experience_level=experience)
            st.session_state["m11_recommendations"] = recommend_programs(profile, programs, limit=3)
    with right:
        st.subheader("Recommended programmes")
        recommendations = st.session_state.get("m11_recommendations", [])
        if not recommendations:
            st.caption("Choose a profile and run the recommendation engine.")
        else:
            for rec in recommendations:
                st.markdown(f"### {rec.program_name}")
                st.progress(rec.score / 100)
                st.write(f"Match score: **{rec.score}/100**")
                for reason in rec.reasons[:3]:
                    st.write(f"• {reason}")

with tabs[2]:
    st.subheader("HAC programme catalogue")
    st.dataframe(catalog[["name", "category", "career_paths", "delivery_mode"]], width="stretch", hide_index=True)

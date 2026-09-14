from __future__ import annotations

from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.engine import score_training_intent
from src.training.models import LeadIntentStage, TrainingLeadProfile

st.set_page_config(page_title="Training Intent Scoring", page_icon="🎯", layout="wide")

st.title("🎯 Training Intent Scoring")
st.caption("M11.5 | Convert explicit learner engagement signals into a transparent 0–100 intent score.")

st.info(
    "Portfolio simulation: CampaignOS uses synthetic learner signals only. "
    "The score is deterministic and does not infer sensitive attributes."
)

st.subheader("1. Learner Profile")
c1, c2, c3, c4 = st.columns(4)
with c1:
    background = st.selectbox("Background", ["career switcher", "IT professional", "student", "business professional"])
with c2:
    career_goal = st.selectbox("Career goal", ["data engineering", "AI / Gen AI", "data analysis", "QA / testing", "cybersecurity", "DevOps", "Product Owner", "Scrum Master", "digital marketing"])
with c3:
    interest = st.selectbox("Interest", ["Azure", "Python", "AI", "Data", "QA", "Cybersecurity", "DevOps", "Agile", "Digital Marketing"])
with c4:
    experience_level = st.selectbox("Experience", ["beginner", "intermediate", "advanced"])

profile = TrainingLeadProfile(
    background=background,
    career_goal=career_goal,
    interest=interest,
    experience_level=experience_level,
)

st.subheader("2. Training Engagement Signals")
s1, s2, s3 = st.columns(3)
with s1:
    campaign_engaged = st.checkbox("Campaign engaged", True)
    course_viewed = st.checkbox("Course viewed", True)
    specific_course_selected = st.checkbox("Specific course selected")
with s2:
    details_requested = st.checkbox("Course details requested")
    session_registered = st.checkbox("Session registered")
    session_attended = st.checkbox("Session attended")
with s3:
    course_question = st.checkbox("Course question asked")
    counselling_requested = st.checkbox("Counselling requested")
    enquiry_submitted = st.checkbox("Enquiry submitted")

signals = {
    "campaign_engaged": campaign_engaged,
    "course_viewed": course_viewed,
    "specific_course_selected": specific_course_selected,
    "details_requested": details_requested,
    "session_registered": session_registered,
    "session_attended": session_attended,
    "course_question": course_question,
    "counselling_requested": counselling_requested,
    "enquiry_submitted": enquiry_submitted,
}

score, stage = score_training_intent(signals)

if stage == LeadIntentStage.ENQUIRY_READY:
    action = "Prioritize enquiry follow-up"
elif stage == LeadIntentStage.HIGH_INTENT:
    action = "Offer counselling or course details"
elif stage == LeadIntentStage.ENGAGED:
    action = "Nurture with relevant training content"
elif stage == LeadIntentStage.INTERESTED:
    action = "Continue course education"
else:
    action = "Build awareness"

st.subheader("3. Intent Result")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Intent Score", f"{score}/100")
with m2:
    st.metric("Intent Stage", stage.value.replace("_", " ").title())
with m3:
    st.metric("Recommended Action", action)

weights = {
    "campaign_engaged": 5,
    "course_viewed": 10,
    "specific_course_selected": 15,
    "details_requested": 15,
    "session_registered": 20,
    "session_attended": 20,
    "course_question": 15,
    "counselling_requested": 25,
    "enquiry_submitted": 30,
}
rows = [
    {
        "Signal": name.replace("_", " ").title(),
        "Active": "Yes" if signals[name] else "No",
        "Weight": weight,
        "Contribution": weight if signals[name] else 0,
    }
    for name, weight in weights.items()
]
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
st.progress(score / 100, text=f"Training intent: {score}/100")

help_text = {
    LeadIntentStage.AWARENESS: "Early-stage awareness. Focus on useful educational content.",
    LeadIntentStage.INTERESTED: "Interest is emerging. Provide relevant course information.",
    LeadIntentStage.ENGAGED: "Meaningful engagement is present. Continue targeted nurture.",
    LeadIntentStage.HIGH_INTENT: "Strong intent is visible. Consider counselling or direct follow-up.",
    LeadIntentStage.ENQUIRY_READY: "The learner is enquiry-ready. Prioritize human follow-up.",
}
st.success(help_text[stage])

st.subheader("4. Structured Lead Record")
record = pd.DataFrame([{
    "Background": profile.background,
    "Career Goal": profile.career_goal,
    "Interest": profile.interest,
    "Experience": profile.experience_level,
    "Intent Score": score,
    "Intent Stage": stage.value,
    "Next Action": action,
}])
st.dataframe(record, width="stretch", hide_index=True)

st.caption(
    "Governance boundary: this page scores supplied engagement signals only. "
    "It does not send WhatsApp/email messages, alter CRM records, or execute campaigns."
)

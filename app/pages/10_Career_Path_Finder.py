from pathlib import Path
import sys
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from src.training.career_paths import build_career_path_result
from src.training.models import TrainingLeadProfile, TrainingProgram
st.set_page_config(page_title="Career Path Finder", page_icon="🧭", layout="wide")
st.title("Career Path Finder")
st.caption("M11.4 • translate learner context into an explainable career path and training sequence")
st.info("Portfolio demonstration only. Recommendations use synthetic learner inputs and the configured training catalogue. No application data or enrolment system is connected.")
catalog_path = ROOT / "data" / "training" / "hac_programs.csv"
if not catalog_path.exists(): st.error("Training catalogue not found."); st.stop()
catalog = pd.read_csv(catalog_path).fillna("")
background = st.selectbox("Background", ["career switcher", "student", "IT professional", "business professional"])
career_goal = st.selectbox("Career goal", ["data engineering","data analyst","AI / Gen AI","QA / testing","cybersecurity","Agile / product","digital marketing"])
interest = st.selectbox("Primary interest", ["Azure","Python","AI","Data","Cybersecurity","QA","Agile","Product","Digital Marketing"])
experience = st.selectbox("Experience level", ["beginner","intermediate","advanced"])
profile = TrainingLeadProfile(background=background, career_goal=career_goal, interest=interest, experience_level=experience)
programs = []
for row in catalog.to_dict(orient="records"):
    programs.append(TrainingProgram(program_id=str(row.get("program_id", row.get("id", row.get("program", row.get("name", ""))))), name=str(row.get("name", "")), category=str(row.get("category", "")), audience_tags=tuple(x.strip() for x in str(row.get("audience_tags", "")).split(",") if x.strip()), career_paths=tuple(x.strip() for x in str(row.get("career_paths", "")).split(",") if x.strip())))
if st.button("Find Career Path", type="primary", width="stretch"):
    st.session_state["m11_career_path_result"] = build_career_path_result(profile, programs)
result = st.session_state.get("m11_career_path_result")
if result:
    st.divider(); persona = result["persona"]; path = result["career_path"]
    left, right = st.columns(2)
    with left:
        st.subheader("Identified Career Persona")
        if persona: st.success(f"**{persona.name}**"); st.write(persona.description)
        else: st.warning("No strong persona identified from the supplied profile.")
    with right:
        st.subheader("Recommended Career Path")
        if path: st.success(f"**{path.name}**"); st.write(path.description)
        else: st.warning("No deterministic career path was identified.")
    if path:
        st.subheader("Career Path Progression")
        for i, stage in enumerate(path.stages, 1): st.markdown(f"**{i}. {stage}**")
        st.subheader("Recommended Training Sequence")
        for i, program in enumerate(result["recommendations"], 1): st.markdown(f"**{i}. {program.name}**  \n`{program.category}`")
        st.info(f"**Suggested next action:** {result['next_action']}")
        with st.expander("Why this path was selected"):
            st.write("The path is selected from explicit learner fields and the CampaignOS career-persona catalogue. It does not infer sensitive attributes or use an opaque model.")
else:
    st.caption("Enter the learner context and select **Find Career Path**.")

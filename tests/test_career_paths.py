from src.training.career_paths import build_career_path_result, career_paths, identify_career_path
from src.training.models import TrainingLeadProfile, TrainingProgram

def programs():
    data=[("P1","Hands-on Python Training","Development & Data",("career switcher","beginner"),("Python development","data")),("P2","Azure Data Engineer","Data",("career switcher","data"),("data engineering","Azure")),("P3","AI/ML with Gen AI","AI",("IT professional",),("AI / Gen AI",)),("P4","Generative AI + Agentic AI with Azure Cloud","AI",("IT professional",),("AI / Gen AI",)),("P5","Quality Assurance / Manual Testing","Quality Assurance",("career switcher",),("QA / testing",)),("P6","Automation Testing","Quality Assurance",("career switcher",),("QA / testing",)),("P7","Cybersecurity + Tools","Cybersecurity",("career switcher",),("cybersecurity",)),("P8","Dev-Sec-Ops","DevOps & Security",("IT professional",),("cybersecurity",)),("P9","Scrum Master Training","Agile & Product",("business professional",),("Agile / product",)),("P10","Product Owner Training","Agile & Product",("business professional",),("Agile / product",)),("P11","PSM I","Agile & Product",("business professional",),("Agile / product",)),("P12","PSPO I","Agile & Product",("business professional",),("Agile / product",)),("P13","Digital Marketing","Digital Marketing",("business professional",),("digital marketing",))]
    return [TrainingProgram(*x) for x in data]

def profile(**kw):
    v=dict(background="career switcher",career_goal="data engineering",interest="Azure",experience_level="beginner"); v.update(kw); return TrainingLeadProfile(**v)

def test_catalogue_has_multiple_paths(): assert len(career_paths()) >= 6
def test_data_path():
    r=build_career_path_result(profile(),programs()); assert r["persona"].persona_id=="DATA_SWITCHER"; assert r["career_path"].path_id=="DATA_SWITCHER_PATH"
def test_data_sequence():
    names=[p.name for p in build_career_path_result(profile(),programs())["recommendations"]]; assert "Hands-on Python Training" in names; assert "Azure Data Engineer" in names
def test_ai_path(): assert build_career_path_result(profile(background="IT professional",career_goal="AI / Gen AI",interest="AI",experience_level="intermediate"),programs())["career_path"].path_id=="AI_ENGINEERING_PATH"
def test_qa_path(): assert build_career_path_result(profile(career_goal="QA / testing",interest="QA"),programs())["career_path"].path_id=="QA_PATH"
def test_cyber_path(): assert build_career_path_result(profile(career_goal="cybersecurity",interest="Cybersecurity"),programs())["career_path"].path_id=="CYBERSECURITY_PATH"
def test_agile_path(): assert build_career_path_result(profile(background="business professional",career_goal="Agile / product",interest="Agile",experience_level="intermediate"),programs())["career_path"].path_id=="AGILE_PRODUCT_PATH"
def test_marketing_path(): assert build_career_path_result(profile(background="business professional",career_goal="digital marketing",interest="Digital Marketing"),programs())["career_path"].path_id=="DIGITAL_MARKETING_PATH"
def test_identify_path(): assert identify_career_path(profile()).persona_id=="DATA_SWITCHER"
def test_next_action(): assert build_career_path_result(profile(),programs())["next_action"]

"""M11.4 deterministic career-path recommendation engine for CampaignOS."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .models import TrainingLeadProfile, TrainingProgram
from .personas import CareerPersona, identify_persona
from .engine import recommend_programs

@dataclass(frozen=True)
class CareerPath:
    path_id: str
    name: str
    description: str
    persona_id: str
    stages: tuple[str, ...]
    recommended_programs: tuple[str, ...]
    next_action: str
    def validate(self) -> None:
        if not self.path_id.strip(): raise ValueError("path_id is required")
        if not self.name.strip(): raise ValueError("name is required")
        if not self.persona_id.strip(): raise ValueError("persona_id is required")
        if not self.stages: raise ValueError("at least one career-path stage is required")
        if not self.recommended_programs: raise ValueError("at least one recommended program is required")
        if not self.next_action.strip(): raise ValueError("next_action is required")

def career_paths() -> tuple[CareerPath, ...]:
    return (
        CareerPath("DATA_SWITCHER_PATH", "Career Switcher → Data Engineering", "A structured path for a career switcher targeting data engineering.", "DATA_SWITCHER", ("Build foundations", "Learn cloud/data engineering", "Apply skills through practical projects", "Prepare for role transition"), ("Hands-on Python Training", "Azure Data Engineer"), "Explore the recommended data-engineering training path."),
        CareerPath("AI_ENGINEERING_PATH", "Developer → AI / Gen AI", "A path for technical learners moving toward AI, ML and generative AI capabilities.", "AI_ENGINEER", ("Strengthen Python foundations", "Build AI/ML knowledge", "Explore Generative AI and Agentic AI", "Apply skills in practical scenarios"), ("Hands-on Python Training", "AI/ML with Gen AI", "Generative AI + Agentic AI with Azure Cloud"), "Review the AI learning sequence and identify the best starting program."),
        CareerPath("DATA_ANALYST_PATH", "Professional → Data Analyst", "A path for professionals building analytics and business-intelligence capability.", "DATA_ANALYST", ("Build data foundations", "Learn analytics and BI", "Practice business reporting", "Prepare for analyst opportunities"), ("Power BI Data Analyst (BI + MySQL)", "Hands-on Python Training"), "Start with the analytics program aligned to the learner's experience."),
        CareerPath("QA_PATH", "Career Switcher → QA / Testing", "A path for learners entering software quality assurance and testing.", "QA_TESTING", ("Understand software testing", "Practice manual QA techniques", "Build testing scenarios", "Prepare for QA opportunities"), ("Quality Assurance / Manual Testing", "Automation Testing"), "Start with QA foundations before progressing to automation."),
        CareerPath("CYBERSECURITY_PATH", "Career Switcher → Cybersecurity", "A path for learners targeting cybersecurity and related technology roles.", "CYBERSECURITY", ("Build security foundations", "Understand cloud/security tooling", "Practice security scenarios", "Prepare for security-focused roles"), ("Cybersecurity + Tools", "Dev-Sec-Ops"), "Review the security foundation and tooling sequence."),
        CareerPath("AGILE_PRODUCT_PATH", "Professional → Agile Product", "A path for professionals moving toward Scrum, product ownership and agile delivery.", "AGILE_PRODUCT", ("Build Agile foundations", "Develop Scrum capability", "Strengthen product ownership skills", "Prepare for Agile role opportunities"), ("Scrum Master Training", "Product Owner Training", "PSM I", "PSPO I"), "Choose the Scrum or Product Owner starting point based on the learner's goal."),
        CareerPath("DIGITAL_MARKETING_PATH", "Professional → Digital Marketing", "A path for learners building practical digital marketing capability.", "DIGITAL_MARKETING", ("Build digital marketing foundations", "Practice channel and campaign concepts", "Apply marketing scenarios", "Prepare for digital marketing opportunities"), ("Digital Marketing",), "Explore the digital marketing learning path."),
    )

def identify_career_path(
    profile: TrainingLeadProfile,
    *,
    persona: CareerPersona | None = None,
) -> CareerPath | None:
    """Resolve a learner profile to the canonical CampaignOS career path."""
    profile.validate()

    selected = persona or identify_persona(
        background=profile.background,
        career_goal=profile.career_goal,
        interest=profile.interest,
        experience_level=profile.experience_level,
    )

    if selected is None:
        return None

    # Persona IDs and career-path IDs are intentionally decoupled.
    # M11.4 owns the explicit business mapping between them.
    persona_to_path = {
        "DATA_SWITCHER": "DATA_SWITCHER_PATH",
        "AI_TRANSITIONER": "AI_ENGINEERING_PATH",
        "AI_ENGINEER": "AI_ENGINEERING_PATH",
        "DATA_ANALYST": "DATA_ANALYST_PATH",
        "QA_TESTING": "QA_PATH",
        "CYBERSECURITY": "CYBERSECURITY_PATH",
        "CLOUD_DEVOPS": "CYBERSECURITY_PATH",
        "AGILE_PRODUCT": "AGILE_PRODUCT_PATH",
        "DIGITAL_MARKETING": "DIGITAL_MARKETING_PATH",
    }

    path_id = persona_to_path.get(selected.persona_id)

    if path_id is None:
        return None

    return next(
        (p for p in career_paths() if p.path_id == path_id),
        None,
    )


def build_career_path_result(profile: TrainingLeadProfile, programs: Iterable[TrainingProgram]) -> dict:
    profile.validate()
    program_list = list(programs)
    for program in program_list: program.validate()
    persona = identify_persona(background=profile.background, career_goal=profile.career_goal, interest=profile.interest, experience_level=profile.experience_level)
    path = identify_career_path(profile, persona=persona)
    if persona is None or path is None:
        return {"persona": None, "career_path": None, "recommendations": recommend_programs(profile, program_list, limit=3), "next_action": "Refine the learner profile to identify a stronger career path."}
    by_name = {p.name.lower(): p for p in program_list}
    recommendations = [by_name[n.lower()] for n in path.recommended_programs if n.lower() in by_name]
    existing = {p.name.lower() for p in recommendations}
    for rec in recommend_programs(profile, program_list, limit=5):
        if rec.program_name.lower() not in existing and rec.program_name.lower() in by_name:
            recommendations.append(by_name[rec.program_name.lower()]); existing.add(rec.program_name.lower())
        if len(recommendations) >= 3: break
    return {"persona": persona, "career_path": path, "recommendations": tuple(recommendations[:3]), "next_action": path.next_action}

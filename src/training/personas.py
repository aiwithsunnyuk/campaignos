"""M11.3 career persona definitions for explainable training recommendations."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CareerPersona:
    persona_id: str
    name: str
    description: str
    backgrounds: tuple[str, ...]
    goals: tuple[str, ...]
    interests: tuple[str, ...]
    experience_levels: tuple[str, ...]
    priority_categories: tuple[str, ...]
    foundational_programs: tuple[str, ...] = ()


CAREER_PERSONAS: tuple[CareerPersona, ...] = (
    CareerPersona(
        "DATA_SWITCHER",
        "Data Career Switcher",
        "A beginner or career switcher targeting a data-oriented IT role.",
        ("career switcher", "student", "business professional"),
        ("data engineering", "data analytics", "data science"),
        ("Azure", "Python", "Power BI", "Data Science"),
        ("beginner", "intermediate"),
        ("Data & Cloud", "Development & Data", "Data & Analytics"),
        ("Hands-on Python Training",),
    ),
    CareerPersona(
        "AI_TRANSITIONER",
        "AI / GenAI Transitioner",
        "An IT or business professional moving toward AI and GenAI capabilities.",
        ("IT professional", "business professional", "student"),
        ("AI", "data science"),
        ("AI", "Azure", "Python"),
        ("beginner", "intermediate", "advanced"),
        ("AI & Machine Learning", "AI & Cloud", "Development & Data"),
        ("Hands-on Python Training",),
    ),
    CareerPersona(
        "CLOUD_DEVOPS",
        "Cloud & DevOps Builder",
        "A technology learner targeting cloud, DevOps or security-adjacent engineering work.",
        ("IT professional", "career switcher"),
        ("DevOps", "cybersecurity"),
        ("Azure", "DevOps", "Cybersecurity"),
        ("beginner", "intermediate", "advanced"),
        ("DevOps & Security", "Data & Cloud", "Cybersecurity"),
    ),
    CareerPersona(
        "AGILE_PRODUCT",
        "Agile / Product Practitioner",
        "A professional targeting Scrum, product ownership or Agile delivery roles.",
        ("IT professional", "business professional", "manager", "career switcher"),
        ("Scrum Master", "Product Owner"),
        ("Agile",),
        ("beginner", "intermediate", "advanced"),
        ("Agile & Product",),
    ),
    CareerPersona(
        "PROJECT_LEADER",
        "Project Management Aspirant",
        "A professional developing formal project-management capabilities.",
        ("business professional", "manager", "IT professional", "career switcher"),
        ("project management",),
        ("PMP", "Agile"),
        ("beginner", "intermediate", "advanced"),
        ("Project Management", "Agile & Product"),
    ),
    CareerPersona(
        "QA_TESTING",
        "QA & Testing Entrant",
        "A learner entering software quality assurance or testing.",
        ("career switcher", "student", "IT professional"),
        ("software testing",),
        ("Python",),
        ("beginner", "intermediate"),
        ("Quality Assurance", "Development & Data"),
    ),
    CareerPersona(
        "CYBERSECURITY",
        "Cybersecurity Aspirant",
        "A learner targeting cybersecurity capabilities and related technology roles.",
        ("career switcher", "student", "IT professional"),
        ("cybersecurity",),
        ("Cybersecurity", "Azure"),
        ("beginner", "intermediate", "advanced"),
        ("Cybersecurity", "DevOps & Security"),
    ),
    CareerPersona(
        "DIGITAL_MARKETING",
        "Digital Marketing Practitioner",
        "A professional building digital marketing capabilities.",
        ("career switcher", "student", "business professional", "IT professional"),
        ("digital marketing",),
        ("Digital Marketing",),
        ("beginner", "intermediate", "advanced"),
        ("Digital Marketing",),
    ),
)


def identify_persona(
    *,
    background: str,
    career_goal: str,
    interest: str,
    experience_level: str,
) -> CareerPersona | None:
    """Select the strongest matching persona using explicit profile fields only."""
    values = {
        "background": background.lower().strip(),
        "career_goal": career_goal.lower().strip(),
        "interest": interest.lower().strip(),
        "experience_level": experience_level.lower().strip(),
    }
    best: tuple[int, CareerPersona] | None = None
    for persona in CAREER_PERSONAS:
        score = 0
        if values["background"] in {v.lower() for v in persona.backgrounds}:
            score += 2
        if values["career_goal"] in {v.lower() for v in persona.goals}:
            score += 5
        if values["interest"] in {v.lower() for v in persona.interests}:
            score += 3
        if values["experience_level"] in {v.lower() for v in persona.experience_levels}:
            score += 1
        if best is None or score > best[0]:
            best = (score, persona)
    return best[1] if best and best[0] > 0 else None

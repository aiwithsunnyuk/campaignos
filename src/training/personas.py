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
    """Select the strongest persona using normalized career-intent signals."""

    def normalize(value: str) -> str:
        value = value.lower().strip()
        replacements = {
            "ai / gen ai": "ai",
            "gen ai": "ai",
            "qa / testing": "testing",
            "quality assurance": "testing",
            "software testing": "testing",
            "data engineering": "data engineering",
            "cybersecurity": "cybersecurity",
            "cyber security": "cybersecurity",
            "devops": "devops",
            "scrum master": "scrum master",
            "product owner": "product owner",
        }
        return replacements.get(value, value)

    values = {
        "background": normalize(background),
        "career_goal": normalize(career_goal),
        "interest": normalize(interest),
        "experience_level": normalize(experience_level),
    }

    best: tuple[int, CareerPersona] | None = None

    for persona in CAREER_PERSONAS:
        score = 0

        persona_backgrounds = {normalize(v) for v in persona.backgrounds}
        persona_goals = {normalize(v) for v in persona.goals}
        persona_interests = {normalize(v) for v in persona.interests}
        persona_experience = {normalize(v) for v in persona.experience_levels}

        if values["background"] in persona_backgrounds:
            score += 2

        if values["career_goal"] in persona_goals:
            score += 5
        elif any(
            values["career_goal"] in goal or goal in values["career_goal"]
            for goal in persona_goals
        ):
            score += 5

        if values["interest"] in persona_interests:
            score += 3
        elif any(
            values["interest"] in interest_value
            or interest_value in values["interest"]
            for interest_value in persona_interests
        ):
            score += 3

        if values["experience_level"] in persona_experience:
            score += 1

        if best is None or score > best[0]:
            best = (score, persona)

    return best[1] if best and best[0] > 0 else None

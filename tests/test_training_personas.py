from src.training.engine import recommend_programs
from src.training.models import TrainingLeadProfile, TrainingProgram
from src.training.personas import CAREER_PERSONAS, identify_persona


def programs():
    return [
        TrainingProgram(
            "P1",
            "Azure Data Engineer",
            "Data & Cloud",
            ("career switcher", "data aspirant"),
            ("data engineering", "cloud", "analytics"),
        ),
        TrainingProgram(
            "P2",
            "Hands-on Python Training",
            "Development & Data",
            ("career switcher", "beginner"),
            ("Python development", "automation", "data"),
        ),
        TrainingProgram(
            "P3",
            "Product Owner Training",
            "Agile & Product",
            ("business professional", "IT professional"),
            ("Product Owner", "Agile"),
        ),
    ]


def test_persona_catalogue_has_multiple_paths():
    assert len(CAREER_PERSONAS) >= 6


def test_data_switcher_persona_is_identified():
    persona = identify_persona(
        background="career switcher",
        career_goal="data engineering",
        interest="Azure",
        experience_level="beginner",
    )
    assert persona is not None
    assert persona.persona_id == "DATA_SWITCHER"


def test_data_switcher_prioritizes_data_engineering():
    profile = TrainingLeadProfile(
        background="career switcher",
        career_goal="data engineering",
        interest="Azure",
        experience_level="beginner",
    )
    results = recommend_programs(profile, programs(), limit=3)
    assert results[0].program_name == "Azure Data Engineer"
    assert results[0].score > results[-1].score


def test_reasons_explain_persona_scoring():
    profile = TrainingLeadProfile(
        background="career switcher",
        career_goal="data engineering",
        interest="Azure",
        experience_level="beginner",
    )
    results = recommend_programs(profile, programs(), limit=3)
    assert results
    assert any("career goal" in reason.lower() for reason in results[0].reasons)


def test_agile_profile_does_not_default_to_data():
    profile = TrainingLeadProfile(
        background="business professional",
        career_goal="Product Owner",
        interest="Agile",
        experience_level="intermediate",
    )
    results = recommend_programs(profile, programs(), limit=3)
    assert results[0].program_name == "Product Owner Training"

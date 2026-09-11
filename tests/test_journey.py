from src.journey.engine import JourneyEngine, summarize_journey_states
from src.journey.models import (
    Journey,
    JourneyStep,
    StepType,
    JourneyStatus,
)


def build_test_journey():
    journey = Journey(
        journey_id="JRN-001",
        journey_name="MQL Conversion Journey",
        description="Synthetic MQL nurture and sales journey.",
        status=JourneyStatus.ACTIVE,
        entry_segment="MQL_Audience",
    )

    journey.add_step(
        JourneyStep(
            step_id="entry",
            name="Journey Entry",
            step_type=StepType.ENTRY,
            next_step_id="welcome",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="welcome",
            name="Welcome Email",
            step_type=StepType.EMAIL,
            config={
                "template": "mql_welcome",
            },
            next_step_id="lifecycle_check",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="lifecycle_check",
            name="MQL Check",
            step_type=StepType.CONDITION,
            config={
                "field": "lifecycle_stage",
                "operator": "equals",
                "value": "MQL",
            },
            true_step_id="score_check",
            false_step_id="nurture",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="score_check",
            name="Lead Score Check",
            step_type=StepType.SCORE_CHECK,
            config={
                "field": "calculated_lead_score",
                "threshold": 70,
            },
            true_step_id="sales",
            false_step_id="nurture",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="nurture",
            name="Nurture Email",
            step_type=StepType.EMAIL,
            config={
                "template": "nurture_content",
            },
            next_step_id="exit",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="sales",
            name="Sales Handoff",
            step_type=StepType.SALES_HANDOFF,
            config={
                "priority": "High",
            },
            next_step_id="exit",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="exit",
            name="Journey Exit",
            step_type=StepType.EXIT,
        )
    )

    return journey


def test_journey_validation():
    journey = build_test_journey()

    assert journey.validate() == []


def test_high_score_mql_reaches_sales():
    journey = build_test_journey()
    engine = JourneyEngine(journey)

    contact = {
        "contact_id": "CON-001",
        "lifecycle_stage": "MQL",
        "calculated_lead_score": 85,
    }

    state = engine.execute_contact(contact)

    assert state.status == "Completed"
    assert "score_check" in state.history
    assert "sales" in state.history
    assert state.metadata["sales_handoff"] is True
    assert state.history[-1] == "exit"


def test_low_score_mql_goes_to_nurture():
    journey = build_test_journey()
    engine = JourneyEngine(journey)

    contact = {
        "contact_id": "CON-002",
        "lifecycle_stage": "MQL",
        "calculated_lead_score": 45,
    }

    state = engine.execute_contact(contact)

    assert state.status == "Completed"
    assert "score_check" in state.history
    assert "nurture" in state.history
    assert "sales" not in state.history
    assert state.history[-1] == "exit"


def test_non_mql_goes_to_nurture():
    journey = build_test_journey()
    engine = JourneyEngine(journey)

    contact = {
        "contact_id": "CON-003",
        "lifecycle_stage": "Engaged",
        "calculated_lead_score": 90,
    }

    state = engine.execute_contact(contact)

    assert state.status == "Completed"
    assert "lifecycle_check" in state.history
    assert "nurture" in state.history
    assert "score_check" not in state.history
    assert "sales" not in state.history


def test_sales_handoff_is_recorded():
    journey = build_test_journey()
    engine = JourneyEngine(journey)

    contact = {
        "contact_id": "CON-004",
        "lifecycle_stage": "MQL",
        "calculated_lead_score": 70,
    }

    state = engine.execute_contact(contact)

    assert state.metadata["sales_handoff"] is True


def test_journey_summary():
    journey = build_test_journey()
    engine = JourneyEngine(journey)

    contacts = [
        {
            "contact_id": "CON-001",
            "lifecycle_stage": "MQL",
            "calculated_lead_score": 85,
        },
        {
            "contact_id": "CON-002",
            "lifecycle_stage": "MQL",
            "calculated_lead_score": 40,
        },
        {
            "contact_id": "CON-003",
            "lifecycle_stage": "Engaged",
            "calculated_lead_score": 90,
        },
    ]

    states = [
        engine.execute_contact(contact)
        for contact in contacts
    ]

    summary = summarize_journey_states(states)

    assert summary["Completed"] == 3
    assert summary["Active"] == 0
    assert summary["Error"] == 0


def test_unknown_step_returns_error_state():
    journey = Journey(
        journey_id="JRN-002",
        journey_name="Broken Journey",
        entry_segment="Test",
    )

    journey.add_step(
        JourneyStep(
            step_id="entry",
            name="Entry",
            step_type=StepType.ENTRY,
            next_step_id="missing_step",
        )
    )

    engine = JourneyEngine(journey)

    contact = {
        "contact_id": "CON-005",
    }

    state = engine.execute_contact(contact)

    assert state.status == "Error"
    assert "Unknown step" in state.metadata["error"]

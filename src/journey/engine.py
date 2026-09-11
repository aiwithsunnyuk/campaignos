from typing import Any, Dict, List, Optional

from src.journey.models import (
    Journey,
    JourneyContactState,
    StepType,
)


class JourneyEngine:
    """
    Rule-based journey execution engine for synthetic contacts.

    The engine evaluates one journey step at a time and records
    the contact's journey history.
    """

    def __init__(self, journey: Journey):
        self.journey = journey
        self._steps = {
            step.step_id: step
            for step in journey.steps
        }

    def get_next_step(
        self,
        current_step_id: str,
        contact: Dict[str, Any],
    ) -> Optional[str]:
        step = self._steps.get(current_step_id)

        if step is None:
            raise ValueError(
                f"Unknown journey step: {current_step_id}"
            )

        if step.step_type == StepType.EXIT:
            return None

        if step.step_type == StepType.CONDITION:
            result = self._evaluate_condition(
                step.config,
                contact,
            )

            return (
                step.true_step_id
                if result
                else step.false_step_id
            )

        if step.step_type == StepType.SCORE_CHECK:
            result = self._evaluate_score(
                step.config,
                contact,
            )

            return (
                step.true_step_id
                if result
                else step.false_step_id
            )

        return step.next_step_id

    def execute_contact(
        self,
        contact: Dict[str, Any],
        max_steps: int = 25,
    ) -> JourneyContactState:

        state = JourneyContactState(
            contact_id=str(contact["contact_id"]),
            journey_id=self.journey.journey_id,
        )

        if not self.journey.steps:
            state.status = "Completed"
            return state

        current_step_id = self._entry_step_id()

        for _ in range(max_steps):
            if current_step_id is None:
                state.status = "Completed"
                break

            step = self._steps.get(current_step_id)

            if step is None:
                state.status = "Error"
                state.metadata["error"] = (
                    f"Unknown step: {current_step_id}"
                )
                break

            state.record_step(step.step_id)

            if step.step_type == StepType.EXIT:
                state.status = "Completed"
                break

            if step.step_type == StepType.SALES_HANDOFF:
                state.metadata["sales_handoff"] = True

            current_step_id = self.get_next_step(
                current_step_id,
                contact,
            )

        else:
            state.status = "Error"
            state.metadata["error"] = (
                "Maximum journey steps exceeded."
            )

        return state

    def _entry_step_id(self) -> Optional[str]:
        for step in self.journey.steps:
            if step.step_type == StepType.ENTRY:
                return step.step_id

        return self.journey.steps[0].step_id

    @staticmethod
    def _evaluate_condition(
        config: Dict[str, Any],
        contact: Dict[str, Any],
    ) -> bool:

        field = config.get("field")
        operator = config.get("operator", "equals")
        expected = config.get("value")

        if not field:
            return False

        actual = contact.get(field)

        if operator == "equals":
            return actual == expected

        if operator == "not_equals":
            return actual != expected

        if operator == "contains":
            return (
                expected is not None
                and expected in str(actual)
            )

        if operator == "greater_than":
            return actual is not None and actual > expected

        if operator == "greater_or_equal":
            return actual is not None and actual >= expected

        if operator == "less_than":
            return actual is not None and actual < expected

        if operator == "less_or_equal":
            return actual is not None and actual <= expected

        if operator == "in":
            return actual in expected

        return False

    @staticmethod
    def _evaluate_score(
        config: Dict[str, Any],
        contact: Dict[str, Any],
    ) -> bool:

        field = config.get(
            "field",
            "calculated_lead_score",
        )

        threshold = config.get(
            "threshold",
            70,
        )

        score = contact.get(field)

        if score is None:
            return False

        return float(score) >= float(threshold)


def summarize_journey_states(
    states: List[JourneyContactState],
) -> Dict[str, int]:

    summary = {
        "Active": 0,
        "Completed": 0,
        "Error": 0,
    }

    for state in states:
        summary[state.status] = (
            summary.get(state.status, 0) + 1
        )

    return summary
def prepare_contacts_for_journey(
    contacts,
    segment_engine=None,
):
    """
    Prepare contact records for journey execution.

    If a segmentation engine is supplied, it can be used to
    restrict the audience before journey execution.
    Lead scoring can then enrich each contact record before
    journey rules are evaluated.
    """

    if contacts is None:
        return []

    if hasattr(contacts, "to_dict"):
        records = contacts.to_dict("records")
    else:
        records = list(contacts)

    if segment_engine is not None:
        records = segment_engine(records)

    return records

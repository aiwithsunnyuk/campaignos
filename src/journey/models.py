from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class StepType(str, Enum):
    ENTRY = "entry"
    EMAIL = "email"
    WAIT = "wait"
    CONDITION = "condition"
    SCORE_CHECK = "score_check"
    SALES_HANDOFF = "sales_handoff"
    EXIT = "exit"


class JourneyStatus(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"


@dataclass
class JourneyStep:
    step_id: str
    name: str
    step_type: StepType
    config: Dict[str, Any] = field(default_factory=dict)

    # Used for linear steps
    next_step_id: Optional[str] = None

    # Used for branching steps
    true_step_id: Optional[str] = None
    false_step_id: Optional[str] = None


@dataclass
class Journey:
    journey_id: str
    journey_name: str
    description: str = ""
    status: JourneyStatus = JourneyStatus.DRAFT
    entry_segment: Optional[str] = None
    steps: List[JourneyStep] = field(default_factory=list)

    def add_step(self, step: JourneyStep) -> None:
        """Add a step to the journey."""
        self.steps.append(step)

    def get_step(self, step_id: str) -> Optional[JourneyStep]:
        """Return a journey step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step

        return None

    def validate(self) -> List[str]:
        """
        Validate the journey structure.

        Returns:
            A list of validation errors.
            An empty list means the journey is valid.
        """

        errors: List[str] = []

        if not self.journey_id:
            errors.append("Journey ID is required.")

        if not self.journey_name:
            errors.append("Journey name is required.")

        if not self.entry_segment:
            errors.append("Entry segment is required.")

        if not self.steps:
            errors.append("Journey must contain at least one step.")

        step_ids = [step.step_id for step in self.steps]

        if len(step_ids) != len(set(step_ids)):
            errors.append("Journey step IDs must be unique.")

        valid_step_ids = set(step_ids)

        for step in self.steps:

            # -----------------------------------------
            # Branching steps
            # -----------------------------------------
            if step.step_type in {
                StepType.CONDITION,
                StepType.SCORE_CHECK,
            }:

                if not step.true_step_id:
                    errors.append(
                        f"Branching step '{step.step_id}' "
                        "requires a true branch."
                    )

                if not step.false_step_id:
                    errors.append(
                        f"Branching step '{step.step_id}' "
                        "requires a false branch."
                    )

                if (
                    step.true_step_id
                    and step.true_step_id not in valid_step_ids
                ):
                    errors.append(
                        f"Branching step '{step.step_id}' "
                        f"references unknown true step "
                        f"'{step.true_step_id}'."
                    )

                if (
                    step.false_step_id
                    and step.false_step_id not in valid_step_ids
                ):
                    errors.append(
                        f"Branching step '{step.step_id}' "
                        f"references unknown false step "
                        f"'{step.false_step_id}'."
                    )

            # -----------------------------------------
            # Linear steps
            # -----------------------------------------
            elif step.step_type not in {
                StepType.ENTRY,
                StepType.EXIT,
            }:

                if not step.next_step_id:
                    errors.append(
                        f"Step '{step.step_id}' "
                        "requires a next step."
                    )

                elif step.next_step_id not in valid_step_ids:
                    errors.append(
                        f"Step '{step.step_id}' "
                        f"references unknown next step "
                        f"'{step.next_step_id}'."
                    )

        return errors


@dataclass
class JourneyContactState:
    contact_id: str
    journey_id: str
    current_step_id: Optional[str] = None
    status: str = "Active"
    history: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def record_step(self, step_id: str) -> None:
        """Record a journey step in the contact history."""
        self.current_step_id = step_id
        self.history.append(step_id)

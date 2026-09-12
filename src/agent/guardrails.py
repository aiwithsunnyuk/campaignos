"""Security and AI guardrails for CampaignOS agent operations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

ALLOWED_ACTION_TYPES = frozenset(
    {
        "OPTIMIZE_CONVERSION_PATH",
        "OPTIMIZE_EMAIL_ENGAGEMENT",
        "OPTIMIZE_CTA",
        "REFINE_AUDIENCE",
        "PRIORITIZE_LEADS",
        "REVIEW_JOURNEY",
    }
)

BLOCKED_PARAMETER_KEYS = frozenset(
    {
        "api_key",
        "access_token",
        "authorization",
        "password",
        "secret",
        "private_key",
        "credential",
    }
)

EXTERNAL_EXECUTION_KEYS = frozenset(
    {
        "url",
        "endpoint",
        "webhook",
        "recipient",
        "send",
        "execute",
        "tool",
    }
)


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str


def validate_action_type(action_type: str) -> GuardrailResult:
    """Allow only explicitly supported agent action types."""
    if not isinstance(action_type, str) or not action_type.strip():
        return GuardrailResult(False, "Action type must be a non-empty string.")
    if action_type not in ALLOWED_ACTION_TYPES:
        return GuardrailResult(False, f"Action type is not allowlisted: {action_type}")
    return GuardrailResult(True, "Action type is allowlisted.")


def validate_parameters(parameters: Mapping[str, Any] | None) -> GuardrailResult:
    """Reject parameters that could carry secrets or external execution intent."""
    if parameters is None:
        return GuardrailResult(True, "No parameters supplied.")
    if not isinstance(parameters, Mapping):
        return GuardrailResult(False, "Parameters must be a mapping.")

    lowered = {str(key).lower() for key in parameters}
    secret_keys = lowered & BLOCKED_PARAMETER_KEYS
    if secret_keys:
        return GuardrailResult(
            False,
            "Secret-bearing parameters are not permitted in agent actions.",
        )

    external_keys = lowered & EXTERNAL_EXECUTION_KEYS
    if external_keys:
        return GuardrailResult(
            False,
            "External execution parameters are not permitted in agent actions.",
        )

    return GuardrailResult(True, "Parameters pass the guardrail checks.")


def validate_action(
    action_type: str,
    parameters: Mapping[str, Any] | None = None,
) -> GuardrailResult:
    """Validate an agent action against the policy boundary."""
    action_check = validate_action_type(action_type)
    if not action_check.allowed:
        return action_check
    return validate_parameters(parameters)


def sanitize_llm_text(text: str, max_length: int = 12000) -> str:
    """Bound model-generated text before it is displayed or persisted."""
    if not isinstance(text, str):
        raise TypeError("LLM output must be text.")
    if max_length <= 0:
        raise ValueError("max_length must be positive.")
    return text[:max_length]


def external_execution_allowed() -> bool:
    """Explicitly document the current product boundary."""
    return False

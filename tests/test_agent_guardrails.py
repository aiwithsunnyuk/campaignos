from src.agent.guardrails import (
    ALLOWED_ACTION_TYPES,
    external_execution_allowed,
    sanitize_llm_text,
    validate_action,
    validate_action_type,
    validate_parameters,
)


def test_allowlisted_action_is_accepted():
    result = validate_action_type("REFINE_AUDIENCE")
    assert result.allowed is True


def test_unknown_action_is_rejected():
    result = validate_action_type("DELETE_CAMPAIGN")
    assert result.allowed is False


def test_empty_action_is_rejected():
    result = validate_action_type("")
    assert result.allowed is False


def test_secret_parameter_is_rejected():
    result = validate_parameters({"api_key": "do-not-store"})
    assert result.allowed is False


def test_external_execution_parameter_is_rejected():
    result = validate_parameters({"webhook": "https://example.invalid"})
    assert result.allowed is False


def test_normal_parameters_are_accepted():
    result = validate_action(
        "OPTIMIZE_CTA",
        {"channel": "email", "priority": 2},
    )
    assert result.allowed is True


def test_all_allowlisted_actions_are_strings():
    assert ALLOWED_ACTION_TYPES
    assert all(isinstance(action, str) for action in ALLOWED_ACTION_TYPES)


def test_llm_output_is_bounded():
    assert sanitize_llm_text("abcdef", max_length=3) == "abc"


def test_llm_output_rejects_non_text():
    try:
        sanitize_llm_text(123)  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError")


def test_external_execution_is_disabled():
    assert external_execution_allowed() is False

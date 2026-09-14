from src.training.engine import score_training_intent
from src.training.models import LeadIntentStage


def test_no_signals_is_awareness():
    score, stage = score_training_intent({})
    assert score == 0
    assert stage == LeadIntentStage.AWARENESS


def test_basic_interest_stage():
    score, stage = score_training_intent({"campaign_engaged": True, "course_viewed": True})
    assert score == 15
    assert stage == LeadIntentStage.INTERESTED


def test_high_intent_threshold():
    score, stage = score_training_intent({
        "campaign_engaged": True,
        "course_viewed": True,
        "specific_course_selected": True,
        "details_requested": True,
        "session_registered": True,
        "session_attended": True,
    })
    assert score == 85
    assert stage == LeadIntentStage.ENQUIRY_READY


def test_enquiry_score_is_capped():
    score, stage = score_training_intent({
        "campaign_engaged": True,
        "course_viewed": True,
        "specific_course_selected": True,
        "details_requested": True,
        "session_registered": True,
        "session_attended": True,
        "course_question": True,
        "counselling_requested": True,
        "enquiry_submitted": True,
    })
    assert score == 100
    assert stage == LeadIntentStage.ENQUIRY_READY


def test_numeric_signals_are_supported():
    score, stage = score_training_intent({"campaign_engaged": 1, "course_viewed": 1})
    assert score == 15
    assert stage == LeadIntentStage.INTERESTED

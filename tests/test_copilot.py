from src.copilot.engine import CampaignCopilot
from src.copilot.models import CopilotRequest, TASK_PROMPTS

class OfflineProvider:
    model = "offline-test"
    def health(self):
        return False

def sample_request(task="Campaign Brief"):
    return CopilotRequest(task=task, campaign_name="Test Campaign", business_type="Training & Education", region="APAC", objective="Increase qualified registrations", audience="APAC opted-in MQL contacts", tone="Professional", context={"Campaign status": "Planning", "Average contact lead score": 72.5})

def test_task_prompts_exist():
    assert len(TASK_PROMPTS) == 4
    assert "Campaign Brief" in TASK_PROMPTS
    assert "Email Copy" in TASK_PROMPTS

def test_prompt_contains_campaign_context():
    prompt = CampaignCopilot(provider=OfflineProvider()).build_prompt(sample_request())
    assert "Test Campaign" in prompt
    assert "APAC" in prompt
    assert "Increase qualified registrations" in prompt

def test_offline_fallback_returns_response():
    response = CampaignCopilot(provider=OfflineProvider()).run(sample_request())
    assert response.used_fallback is True
    assert response.provider == "CampaignOS Rule Engine"
    assert "Campaign Objective" in response.content

def test_each_task_has_fallback_output():
    copilot = CampaignCopilot(provider=OfflineProvider())
    for task in TASK_PROMPTS:
        response = copilot.run(sample_request(task))
        assert response.content
        assert response.task == task
        assert response.used_fallback is True

def test_fallback_can_be_disabled():
    copilot = CampaignCopilot(provider=OfflineProvider())
    try:
        copilot.run(sample_request(), allow_fallback=False)
    except RuntimeError as exc:
        assert "Local LLM is unavailable" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")

def test_provider_health_is_not_required_for_prompt_building():
    prompt = CampaignCopilot(provider=OfflineProvider()).build_prompt(sample_request("Email Copy"))
    assert "Email Copy" in prompt
    assert "Professional" in prompt

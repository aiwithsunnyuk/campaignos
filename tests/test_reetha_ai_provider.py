import json
from urllib.error import URLError
import pytest
from src.reetha_ai_provider import OpenAICompatibleProvider, ProviderConfig, ProviderRequestError, load_provider_config

def test_no_key_means_no_provider():
    assert load_provider_config(environ={}, secrets_reader=lambda _name: "") is None

def test_environment_config_and_timeout_clamp():
    config = load_provider_config(environ={"CAMPAIGNOS_AI_API_KEY":"secret", "CAMPAIGNOS_AI_MODEL":"test-model",
        "CAMPAIGNOS_AI_BASE_URL":"https://example.test/v1/", "CAMPAIGNOS_AI_TIMEOUT_SECONDS":"120"},
        secrets_reader=lambda _name: "")
    assert config.api_key == "secret" and config.model == "test-model"
    assert config.base_url == "https://example.test/v1" and config.timeout_seconds == 90

def test_streamlit_secret_fallback():
    config = load_provider_config(environ={}, secrets_reader=lambda name: {
        "CAMPAIGNOS_AI_API_KEY":"secret-store", "CAMPAIGNOS_AI_MODEL":"secret-model"}.get(name, ""))
    assert config.api_key == "secret-store" and config.model == "secret-model"

def test_successful_provider_response(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def read(self): return json.dumps({"choices":[{"message":{"content":" improved copy "}}]}).encode()
    seen = {}
    def fake_urlopen(request, timeout):
        seen["url"], seen["auth"] = request.full_url, request.get_header("Authorization")
        seen["body"] = json.loads(request.data.decode())
        return Response()
    monkeypatch.setattr("src.reetha_ai_provider.urlopen", fake_urlopen)
    provider = OpenAICompatibleProvider(ProviderConfig("test-secret", "test-model", "https://example.test/v1"))
    assert provider.generate_text("Improve this") == "improved copy"
    assert seen["url"] == "https://example.test/v1/chat/completions"
    assert seen["auth"] == "Bearer test-secret" and seen["body"]["model"] == "test-model"

def test_network_failure_is_sanitized_and_empty_prompt_rejected(monkeypatch):
    monkeypatch.setattr("src.reetha_ai_provider.urlopen", lambda *_a, **_k: (_ for _ in ()).throw(URLError("offline")))
    provider = OpenAICompatibleProvider(ProviderConfig("private-key"))
    with pytest.raises(ProviderRequestError, match="could not be reached"): provider.generate_text("draft")
    with pytest.raises(ValueError): provider.generate_text(" ")

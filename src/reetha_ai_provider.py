"""Configurable OpenAI-compatible provider adapter for CampaignOS."""
from __future__ import annotations
import json, os
from dataclasses import dataclass
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class ProviderRequestError(RuntimeError):
    """Sanitized provider/network/response error."""

@dataclass(frozen=True)
class ProviderConfig:
    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 30.0

def _secret(name: str) -> str:
    try:
        import streamlit as st
        return str(st.secrets.get(name, "") or "").strip()
    except Exception:
        return ""

def load_provider_config(environ: Mapping[str, str] | None = None, secrets_reader=None):
    env = os.environ if environ is None else environ
    secret = secrets_reader or _secret
    key = str(env.get("CAMPAIGNOS_AI_API_KEY", "") or "").strip() or str(secret("CAMPAIGNOS_AI_API_KEY") or "").strip()
    if not key:
        return None
    model = str(env.get("CAMPAIGNOS_AI_MODEL", "") or "").strip() or str(secret("CAMPAIGNOS_AI_MODEL") or "gpt-4o-mini").strip()
    base = str(env.get("CAMPAIGNOS_AI_BASE_URL", "") or "").strip() or str(secret("CAMPAIGNOS_AI_BASE_URL") or "https://api.openai.com/v1").strip()
    raw_timeout = str(env.get("CAMPAIGNOS_AI_TIMEOUT_SECONDS", "") or "").strip()
    try:
        timeout = float(raw_timeout) if raw_timeout else 30.0
    except ValueError:
        timeout = 30.0
    timeout = min(max(timeout, 1.0), 90.0)
    return ProviderConfig(key, model, base.rstrip("/"), timeout)

class OpenAICompatibleProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config
    def generate_text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        payload = {"model": self.config.model, "temperature": 0.4, "messages": [
            {"role": "system", "content": "You edit B2B campaign copy. Preserve facts. Never invent prices, results, certifications, guarantees, or customer claims. Return only revised copy."},
            {"role": "user", "content": prompt}]}
        request = Request(f"{self.config.base_url}/chat/completions", data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                data = json.loads(response.read().decode())
        except HTTPError as exc:
            raise ProviderRequestError(f"AI provider returned HTTP {exc.code}.") from None
        except (URLError, TimeoutError, OSError):
            raise ProviderRequestError("AI provider could not be reached or timed out.") from None
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ProviderRequestError("AI provider returned an unreadable response.") from None
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise ProviderRequestError("AI provider response did not contain draft text.") from None
        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestError("AI provider returned empty draft text.")
        return content.strip()

def configured_provider():
    config = load_provider_config()
    return OpenAICompatibleProvider(config) if config else None

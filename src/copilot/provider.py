import json
import os
from typing import Optional
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

class LocalLLMProvider:
    """Small Ollama-compatible local provider with no cloud/API dependency."""
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 60):
        self.base_url = (base_url or os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            request = Request(f"{self.base_url}/api/tags", method="GET")
            with urlopen(request, timeout=3) as response:
                return response.status == 200
        except (URLError, HTTPError, OSError):
            return False

    def generate(self, prompt: str, system: str = "", temperature: float = 0.3) -> str:
        payload = {"model": self.model, "prompt": prompt, "system": system, "stream": False, "options": {"temperature": temperature}}
        request = Request(f"{self.base_url}/api/generate", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return str(data.get("response", "")).strip()

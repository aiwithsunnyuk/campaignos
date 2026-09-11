# CampaignOS M9: Local LLM Campaign Copilot

M9 adds an optional local LLM layer without a cloud API dependency.

```text
CampaignOS synthetic data -> Context Builder -> CopilotRequest
                                      |
                                      v
                              LocalLLMProvider
                               /            \
                         Ollama/local     fallback
                               \            /
                                CopilotResponse
                                      |
                                  Streamlit UI
```

## Local model

CampaignOS uses an Ollama-compatible local HTTP interface.

```bash
ollama pull llama3.2:3b
ollama serve
streamlit run app/Home.py
```

Defaults:
- `LOCAL_LLM_BASE_URL=http://localhost:11434`
- `LOCAL_LLM_MODEL=llama3.2:3b`

M9 uses synthetic CampaignOS context only. It does not connect to Eloqua,
Salesforce, Outlook, CRM records, or other proprietary systems. Generated
text is advisory and does not send email, update CRM records, or execute
external actions.

If Ollama is unavailable, the deterministic fallback keeps the workflow
fully demonstrable offline.

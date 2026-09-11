from typing import Any, Dict
from src.copilot.models import CopilotRequest, CopilotResponse, TASK_PROMPTS
from src.copilot.provider import LocalLLMProvider

SYSTEM_PROMPT = """You are CampaignOS Copilot, a marketing-operations assistant.
Work only with the campaign context supplied by the application.
Do not claim access to Eloqua, Salesforce, Outlook, CRM records, customer data, external APIs, or proprietary systems.
Use practical B2B marketing-automation language.
Prefer structured, concise recommendations.
Never invent performance results that are not present in the context.""".strip()

class CampaignCopilot:
    def __init__(self, provider: LocalLLMProvider | None = None):
        self.provider = provider or LocalLLMProvider()

    def build_prompt(self, request: CopilotRequest) -> str:
        context_lines = [f"Campaign: {request.campaign_name}", f"Business type: {request.business_type}", f"Region: {request.region}", f"Objective: {request.objective}", f"Audience: {request.audience}", f"Tone: {request.tone}"]
        for key, value in request.context.items():
            context_lines.append(f"{key}: {value}")
        task_instruction = TASK_PROMPTS.get(request.task, "Provide useful campaign guidance for the selected task.")
        return f"Task: {request.task}\nInstruction: {task_instruction}\n\nCampaign context:\n" + "\n".join(context_lines) + "\n\nReturn the answer with clear headings and actionable bullets."

    def run(self, request: CopilotRequest, allow_fallback: bool = True) -> CopilotResponse:
        prompt = self.build_prompt(request)
        if self.provider.health():
            try:
                content = self.provider.generate(prompt=prompt, system=SYSTEM_PROMPT)
                if content:
                    return CopilotResponse(request.task, content, "Ollama", self.provider.model, False)
            except Exception:
                pass
        if not allow_fallback:
            raise RuntimeError("Local LLM is unavailable and fallback is disabled.")
        return CopilotResponse(request.task, self._fallback(request), "CampaignOS Rule Engine", "deterministic-fallback", True, {"reason": "Local Ollama endpoint unavailable."})

    @staticmethod
    def _fallback(request: CopilotRequest) -> str:
        objective = request.objective or "improve campaign performance"
        audience = request.audience or "the selected campaign audience"
        if request.task == "Campaign Brief":
            return f"""### Campaign Objective\n{objective}\n\n### Audience\n{audience}\n\n### Messaging Pillars\n- Lead with the audience's business problem.\n- Connect the offer to a measurable business outcome.\n- Use proof, relevance, and a clear next step.\n\n### Recommended Channels\n- Email nurture\n- Landing page\n- Webinar or event touchpoint\n- Sales follow-up for qualified leads\n\n### Primary CTA\nRequest more information or start the next agreed campaign action.\n\n### Measurement\nTrack reach, engagement, clicks, conversions, lifecycle progression, and regional performance."""
        if request.task == "Audience Strategy":
            return f"""### Audience Strategy\nPrioritize {audience} for the objective: {objective}.\n\n### Segmentation\n- Lifecycle stage\n- Region\n- Industry\n- Engagement level\n- Consent / marketability status\n\n### Exclusions\n- Not Subscribed contacts\n- Invalid or incomplete contact records\n- Contacts already converted for the campaign objective\n\n### Next Best Action\nUse engagement and lead-score signals to separate nurture audiences from sales-ready audiences."""
        if request.task == "Optimization Recommendations":
            return f"""### Priority 1: Tighten Audience Relevance\nAlign {audience} more closely to the objective.\n\n**Why:** Better relevance should improve engagement quality.\n\n**Next action:** Compare lifecycle, region, industry, and engagement segments.\n\n### Priority 2: Strengthen Message-to-CTA Alignment\nMake the CTA directly reinforce the promised outcome.\n\n**Next action:** Test one focused CTA against a broader CTA.\n\n### Priority 3: Use Lifecycle-Aware Follow-up\nRoute higher-intent contacts toward sales while keeping lower-intent contacts in nurture.\n\n**Next action:** Apply the existing CampaignOS lead-score and journey rules."""
        return f"""### Subject\nA focused next step for {audience}\n\n### Preheader\nTurn campaign interest into a measurable next action.\n\n### Email\nYour audience has a specific business objective: {objective}.\n\nCampaignOS recommends keeping the message focused on the problem, the business outcome, and one clear next step.\n\n### CTA\nExplore the next step\n\n### Footer\nCampaign communication should follow the applicable consent and contact-preference rules."""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class CopilotRequest:
    task: str
    campaign_name: str
    business_type: str
    region: str
    objective: str
    audience: str
    tone: str = "Professional"
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CopilotResponse:
    task: str
    content: str
    provider: str
    model: str
    used_fallback: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

TASK_PROMPTS = {
    "Campaign Brief": "Create a concise campaign brief covering objective, audience, value proposition, messaging pillars, channels, CTA, and measurement.",
    "Audience Strategy": "Recommend audience strategy, segmentation logic, lifecycle focus, message angle, exclusions, and next-best marketing action.",
    "Optimization Recommendations": "Review the supplied campaign context and provide prioritized optimization recommendations. Include the reason, expected impact, and a practical next action.",
    "Email Copy": "Draft a concise B2B marketing email with subject line, preheader, opening, value proposition, CTA, and a short compliance-conscious footer.",
}

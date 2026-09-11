from typing import Any, Dict, Iterable, List, Tuple

from src.agent.models import AgentObservation, ObservationSeverity


def _number(context: Dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in context:
            value = context[key]
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def _rate(context: Dict[str, Any], *keys: str) -> float | None:
    value = _number(context, *keys)
    if value is None:
        return None
    return value / 100 if value > 1 else value


class CampaignIntelligenceAnalyzer:
    """Deterministic campaign analyzer that produces evidence-backed observations.

    The analyzer deliberately uses only supplied CampaignOS context. It does not
    call external systems and does not invent missing performance data.
    """

    def analyze(
        self,
        campaign_id: str,
        context: Dict[str, Any],
    ) -> List[AgentObservation]:
        observations: List[AgentObservation] = []

        conversion_rate = _rate(
            context,
            "conversion_rate",
            "Conversion rate",
            "Conversion Rate",
        )
        benchmark = _rate(
            context,
            "conversion_benchmark",
            "Conversion benchmark",
            "Conversion Benchmark",
        )

        if conversion_rate is not None and benchmark is not None:
            if conversion_rate < benchmark * 0.75:
                observations.append(
                    self._observation(
                        campaign_id,
                        "Conversion",
                        "Conversion performance requires review",
                        "Campaign conversion is materially below the supplied benchmark.",
                        ObservationSeverity.HIGH,
                        {
                            "conversion_rate": conversion_rate,
                            "benchmark": benchmark,
                            "gap": benchmark - conversion_rate,
                        },
                    )
                )
            elif conversion_rate < benchmark:
                observations.append(
                    self._observation(
                        campaign_id,
                        "Conversion",
                        "Conversion performance is below benchmark",
                        "Campaign conversion is below the supplied benchmark.",
                        ObservationSeverity.MEDIUM,
                        {
                            "conversion_rate": conversion_rate,
                            "benchmark": benchmark,
                            "gap": benchmark - conversion_rate,
                        },
                    )
                )
            else:
                observations.append(
                    self._observation(
                        campaign_id,
                        "Conversion",
                        "Conversion is at or above benchmark",
                        "Campaign conversion meets or exceeds the supplied benchmark.",
                        ObservationSeverity.INFO,
                        {
                            "conversion_rate": conversion_rate,
                            "benchmark": benchmark,
                            "gap": conversion_rate - benchmark,
                        },
                    )
                )

        open_rate = _rate(context, "open_rate", "Open rate", "Open Rate")
        click_rate = _rate(context, "click_rate", "Click rate", "Click Rate")

        if open_rate is not None and open_rate < 0.25:
            observations.append(
                self._observation(
                    campaign_id,
                    "Engagement",
                    "Email engagement is low",
                    "The supplied open rate indicates that message reach or subject-line relevance should be reviewed.",
                    ObservationSeverity.MEDIUM,
                    {"open_rate": open_rate},
                )
            )

        if click_rate is not None and click_rate < 0.05:
            observations.append(
                self._observation(
                    campaign_id,
                    "Engagement",
                    "Click engagement is low",
                    "The supplied click rate indicates that message-to-CTA alignment should be reviewed.",
                    ObservationSeverity.MEDIUM,
                    {"click_rate": click_rate},
                )
            )

        marketable = _number(
            context,
            "marketable_contacts",
            "Marketable contacts",
            "Marketable Contacts",
        )
        mql_count = _number(
            context,
            "mql_count",
            "MQL count",
            "MQL Count",
        )

        if marketable is not None and mql_count is not None and marketable > 0:
            mql_ratio = mql_count / marketable
            if mql_ratio < 0.10:
                observations.append(
                    self._observation(
                        campaign_id,
                        "Audience",
                        "Qualified audience share is low",
                        "MQLs represent a small share of the supplied marketable audience.",
                        ObservationSeverity.MEDIUM,
                        {
                            "mql_count": mql_count,
                            "marketable_contacts": marketable,
                            "mql_ratio": mql_ratio,
                        },
                    )
                )

        lead_score = _number(
            context,
            "average_lead_score",
            "Average contact lead score",
            "Average lead score",
            "Average Contact Lead Score",
        )

        if lead_score is not None:
            if lead_score < 50:
                observations.append(
                    self._observation(
                        campaign_id,
                        "Lifecycle",
                        "Average lead score is low",
                        "The supplied average lead score suggests the campaign audience may need additional nurturing.",
                        ObservationSeverity.MEDIUM,
                        {"average_lead_score": lead_score},
                    )
                )
            elif lead_score >= 80:
                observations.append(
                    self._observation(
                        campaign_id,
                        "Lifecycle",
                        "Audience shows strong lead intent",
                        "The supplied average lead score indicates a high-intent audience.",
                        ObservationSeverity.LOW,
                        {"average_lead_score": lead_score},
                    )
                )

        if not observations:
            observations.append(
                self._observation(
                    campaign_id,
                    "Portfolio Health",
                    "No material issue detected from supplied signals",
                    "The available campaign context does not contain a rule trigger requiring intervention.",
                    ObservationSeverity.INFO,
                    {},
                )
            )

        return observations

    @staticmethod
    def _observation(
        campaign_id: str,
        category: str,
        title: str,
        description: str,
        severity: ObservationSeverity,
        evidence: Dict[str, Any],
    ) -> AgentObservation:
        safe_id = "".join(ch if ch.isalnum() else "-" for ch in title.lower()).strip("-")
        return AgentObservation(
            observation_id=f"{campaign_id}-{safe_id}",
            category=category,
            title=title,
            description=description,
            severity=severity,
            evidence=evidence,
        )

    @staticmethod
    def summarize(observations: Iterable[AgentObservation]) -> Dict[str, Any]:
        items = list(observations)
        severity_rank = {
            ObservationSeverity.INFO: 0,
            ObservationSeverity.LOW: 1,
            ObservationSeverity.MEDIUM: 2,
            ObservationSeverity.HIGH: 3,
            ObservationSeverity.CRITICAL: 4,
        }
        highest = max(
            items,
            key=lambda item: severity_rank[item.severity],
            default=None,
        )

        return {
            "observation_count": len(items),
            "highest_severity": highest.severity.value if highest else None,
            "highest_priority_observation": highest.title if highest else None,
        }

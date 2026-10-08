from src.lead_360.models import Lead360

from .models import NextBestAction


class LeadNextBestActionEngine:
    """Deterministic, explainable lead-level NBA engine."""

    def recommend(self, lead: Lead360) -> NextBestAction:
        if lead.registration_count > 0 and lead.enrollment_count == 0:
            return NextBestAction(
                lead_id=lead.lead_id,
                tenant_id=lead.tenant_id,
                action_type="enrollment_follow_up",
                priority="high",
                recommendation="Prioritize enrollment conversion",
                reason=(
                    "The lead has registered but has not enrolled. "
                    "Enrollment is the next conversion opportunity."
                ),
                evidence=(
                    f"{lead.registration_count} registration(s)",
                    "no enrollment recorded",
                ),
            )

        if lead.total_engagements == 0:
            return NextBestAction(
                lead_id=lead.lead_id,
                tenant_id=lead.tenant_id,
                action_type="re_engagement",
                priority="medium",
                recommendation="Start a re-engagement sequence",
                reason=(
                    "No engagement activity is currently associated "
                    "with this lead."
                ),
                evidence=("no engagement activity recorded",),
            )

        if lead.registration_count == 0 and lead.total_engagements < 3:
            return NextBestAction(
                lead_id=lead.lead_id,
                tenant_id=lead.tenant_id,
                action_type="nurture",
                priority="medium",
                recommendation="Continue targeted nurture",
                reason=(
                    "The lead shows early engagement but does not yet "
                    "have a strong enough conversion signal."
                ),
                evidence=(
                    f"{lead.total_engagements} engagement(s)",
                    "no registration recorded",
                ),
            )

        if lead.registration_count == 0 and lead.total_engagements >= 3:
            return NextBestAction(
                lead_id=lead.lead_id,
                tenant_id=lead.tenant_id,
                action_type="registration_follow_up",
                priority="high",
                recommendation="Prioritize registration conversion",
                reason=(
                    "The lead has strong engagement but has not registered. "
                    "Registration is the next conversion opportunity."
                ),
                evidence=(
                    f"{lead.total_engagements} engagement(s)",
                    "no registration recorded",
                ),
            )

        return NextBestAction(
            lead_id=lead.lead_id,
            tenant_id=lead.tenant_id,
            action_type="monitor",
            priority="low",
            recommendation="Monitor lead activity",
            reason=(
                "The lead does not currently require an immediate "
                "conversion intervention."
            ),
            evidence=(
                f"{lead.total_engagements} engagement(s)",
                "no immediate intervention required",
            ),
        )

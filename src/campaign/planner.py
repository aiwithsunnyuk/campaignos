from datetime import date
from typing import List

from src.campaign.models import Campaign


def create_campaign(
    campaign_id: str,
    campaign_name: str,
    business_type: str,
    product_name: str,
    region: str,
    objective: str,
    status: str,
    start_date: date,
    end_date: date,
    target_mqls: int,
    budget: float,
    channels: List[str],
    owner: str,
) -> Campaign:
    """Create and validate a CampaignOS campaign."""

    if not campaign_name.strip():
        raise ValueError("Campaign name is required.")

    if end_date < start_date:
        raise ValueError("End date cannot be before start date.")

    if target_mqls < 0:
        raise ValueError("Target MQLs cannot be negative.")

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    if not channels:
        raise ValueError("At least one campaign channel is required.")

    return Campaign(
        campaign_id=campaign_id,
        campaign_name=campaign_name.strip(),
        business_type=business_type,
        product_name=product_name,
        region=region,
        objective=objective,
        status=status,
        start_date=start_date,
        end_date=end_date,
        target_mqls=target_mqls,
        budget=budget,
        channels=channels,
        owner=owner.strip(),
    )

import pandas as pd

from src.analytics.campaign_performance import (
    campaign_performance,
    campaign_summary,
    channel_performance,
    executive_insights,
    regional_performance,
    top_campaigns,
)


def sample_campaigns():
    return pd.DataFrame(
        [
            {
                "campaign_id": "CMP-001",
                "campaign_name": "Campaign A",
                "business_type": "Training",
                "region": "APAC",
                "objective": "Lead Generation",
                "status": "Active",
                "budget": 10000,
            },
            {
                "campaign_id": "CMP-002",
                "campaign_name": "Campaign B",
                "business_type": "Technology",
                "region": "Europe",
                "objective": "Conversion",
                "status": "Completed",
                "budget": 15000,
            },
        ]
    )


def sample_contacts():
    return pd.DataFrame(
        [
            {
                "contact_id": "C001",
                "region": "APAC",
            },
            {
                "contact_id": "C002",
                "region": "APAC",
            },
            {
                "contact_id": "C003",
                "region": "Europe",
            },
        ]
    )


def sample_activities():
    return pd.DataFrame(
        [
            {
                "campaign_id": "CMP-001",
                "contact_id": "C001",
                "activity_type": "Email Sent",
                "channel": "Email",
            },
            {
                "campaign_id": "CMP-001",
                "contact_id": "C001",
                "activity_type": "Email Opened",
                "channel": "Email",
            },
            {
                "campaign_id": "CMP-001",
                "contact_id": "C001",
                "activity_type": "Email Clicked",
                "channel": "Email",
            },
            {
                "campaign_id": "CMP-001",
                "contact_id": "C001",
                "activity_type": "Form Submitted",
                "channel": "Email",
            },
            {
                "campaign_id": "CMP-001",
                "contact_id": "C002",
                "activity_type": "Email Sent",
                "channel": "Email",
            },
            {
                "campaign_id": "CMP-001",
                "contact_id": "C002",
                "activity_type": "Email Opened",
                "channel": "Email",
            },
            {
                "campaign_id": "CMP-002",
                "contact_id": "C003",
                "activity_type": "Email Sent",
                "channel": "Email",
            },
        ]
    )


def test_campaign_performance():

    result = campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    assert len(result) == 2

    campaign_a = result[
        result["campaign_id"] == "CMP-001"
    ].iloc[0]

    assert campaign_a["sent"] == 2
    assert campaign_a["opened"] == 2
    assert campaign_a["clicked"] == 1
    assert campaign_a["converted"] == 1
    assert campaign_a["conversion_rate"] == 50.0


def test_campaign_summary():

    performance = campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    summary = campaign_summary(
        performance
    )

    assert summary["campaigns"] == 2
    assert summary["budget"] == 25000
    assert summary["sent"] == 3
    assert summary["converted"] == 1


def test_campaign_rates_are_safe():

    campaigns = sample_campaigns().iloc[:1]

    activities = pd.DataFrame(
        columns=[
            "campaign_id",
            "contact_id",
            "activity_type",
            "channel",
        ]
    )

    result = campaign_performance(
        campaigns,
        activities,
    )

    assert result.iloc[0]["open_rate"] == 0.0
    assert result.iloc[0]["click_rate"] == 0.0
    assert result.iloc[0]["conversion_rate"] == 0.0


def test_regional_performance():

    result = regional_performance(
        sample_contacts(),
        sample_activities(),
    )

    assert set(
        result["region"]
    ) == {"APAC", "Europe"}

    apac = result[
        result["region"] == "APAC"
    ].iloc[0]

    assert apac["sent"] == 2
    assert apac["converted"] == 1


def test_channel_performance():

    result = channel_performance(
        sample_activities()
    )

    assert len(result) == 1
    assert result.iloc[0]["channel"] == "Email"
    assert result.iloc[0]["converted"] == 1


def test_top_campaigns():

    performance = campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    result = top_campaigns(
        performance,
        metric="conversion_rate",
        limit=1,
    )

    assert len(result) == 1
    assert result.iloc[0]["campaign_id"] == "CMP-001"


def test_top_campaigns_invalid_metric():

    performance = campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    try:
        top_campaigns(
            performance,
            metric="invalid_metric",
        )

        assert False

    except ValueError:
        assert True


def test_executive_insights():

    performance = campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    regional = regional_performance(
        sample_contacts(),
        sample_activities(),
    )

    insights = executive_insights(
        performance,
        regional,
    )

    assert len(insights) >= 3

    assert any(
        "Campaign A" in insight
        for insight in insights
    )


def test_empty_summary():

    result = campaign_summary(
        pd.DataFrame()
    )

    assert result["campaigns"] == 0
    assert result["sent"] == 0
    assert result["conversion_rate"] == 0.0


def test_empty_top_campaigns():

    result = top_campaigns(
        pd.DataFrame(),
        metric="conversion_rate",
    )

    assert result.empty

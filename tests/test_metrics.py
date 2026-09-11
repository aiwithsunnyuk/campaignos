import pandas as pd
from src.analytics.metrics import campaign_metrics

def test_campaign_metrics():
    df = pd.DataFrame({"activity_type": [
        "Email Sent", "Email Sent", "Email Opened", "Email Clicked", "Form Submitted"
    ]})
    result = campaign_metrics(df)
    assert result["sent"] == 2
    assert result["opened"] == 1
    assert result["clicked"] == 1
    assert result["converted"] == 1
    assert result["open_rate"] == 0.5
    assert result["ctr"] == 0.5

import pandas as pd

def campaign_metrics(activities: pd.DataFrame) -> dict:
    if activities.empty:
        return {"sent": 0, "opened": 0, "clicked": 0, "converted": 0,
                "open_rate": 0.0, "ctr": 0.0, "conversion_rate": 0.0}

    sent = int((activities["activity_type"] == "Email Sent").sum())
    opened = int((activities["activity_type"] == "Email Opened").sum())
    clicked = int((activities["activity_type"] == "Email Clicked").sum())
    converted = int((activities["activity_type"] == "Form Submitted").sum())

    return {
        "sent": sent, "opened": opened, "clicked": clicked, "converted": converted,
        "open_rate": opened / sent if sent else 0,
        "ctr": clicked / sent if sent else 0,
        "conversion_rate": converted / sent if sent else 0,
    }

def regional_activity(activities: pd.DataFrame, contacts: pd.DataFrame) -> pd.DataFrame:
    if activities.empty or contacts.empty:
        return pd.DataFrame(columns=["region", "activities"])
    merged = activities.merge(contacts[["contact_id", "region"]], on="contact_id", how="left")
    return merged.groupby("region").size().reset_index(name="activities").sort_values("activities", ascending=False)

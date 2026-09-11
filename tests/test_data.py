from src.data.generator import generate_all

def test_generate_all():
    counts = generate_all()
    assert counts["contacts"] == 10000
    assert counts["accounts"] == 1000
    assert counts["campaigns"] == 25
    assert counts["activities"] == 25000
    assert counts["products"] == 10

def test_generated_email_funnel_is_monotonic():
    import pandas as pd

    activities = pd.read_csv("data/synthetic/activities.csv")

    sent = int((activities["activity_type"] == "Email Sent").sum())
    opened = int((activities["activity_type"] == "Email Opened").sum())
    clicked = int((activities["activity_type"] == "Email Clicked").sum())
    submitted = int((activities["activity_type"] == "Form Submitted").sum())

    assert sent >= opened
    assert opened >= clicked
    assert clicked >= submitted
    assert submitted / sent <= 1

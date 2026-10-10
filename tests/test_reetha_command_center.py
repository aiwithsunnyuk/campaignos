import pandas as pd

from src.reetha_command_center import offering_summary


def test_offering_summary_matches_reetha_pricing_catalogue():
    df = pd.DataFrame(
        [
            {"offering_type": "Standalone", "pricing": "₹500 / Month"},
            {"offering_type": "Standalone", "pricing": "Contact Us"},
            {"offering_type": "Integrated", "pricing": "Contact Us"},
            {"offering_type": "Integrated", "pricing": "₹20,000 / Month"},
        ]
    )

    assert offering_summary(df) == {
        "total": 4,
        "standalone": 2,
        "integrated": 2,
        "contact_us": 2,
    }

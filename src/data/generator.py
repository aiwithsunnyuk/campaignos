from pathlib import Path
import random
import pandas as pd
from faker import Faker

RANDOM_SEED = 42
fake = Faker()
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

DATA_DIR = Path("data/synthetic")
REGIONS = ["WW", "APAC", "AMEA", "Europe"]

COUNTRIES = {
    "WW": ["United States", "United Kingdom", "India", "Australia", "Germany"],
    "APAC": ["India", "Australia", "Singapore", "Japan"],
    "AMEA": ["United Arab Emirates", "South Africa", "Kenya", "Saudi Arabia"],
    "Europe": ["Germany", "France", "Netherlands", "Spain", "Italy"],
}

BUSINESSES = [
    "Professional Information Services",
    "Training & Education",
    "Farming Machinery",
    "Event Decoration",
    "Legal Services",
    "SAP Training",
]

PRODUCTS = [
    ("PROD-001", "Professional Information Subscription", "Professional Information Services"),
    ("PROD-002", "DevOps Leadership Program", "Training & Education"),
    ("PROD-003", "Agentic AI Practitioner", "Training & Education"),
    ("PROD-004", "Gen AI Accelerator", "Training & Education"),
    ("PROD-005", "Azure DevOps Bootcamp", "Training & Education"),
    ("PROD-006", "PMP Certification Program", "Training & Education"),
    ("PROD-007", "AI Scrum Master & Product Owner", "Training & Education"),
    ("PROD-008", "Smart Farm Equipment Demo", "Farming Machinery"),
    ("PROD-009", "Event Decoration Package", "Event Decoration"),
    ("PROD-010", "SAP S/4HANA Training", "SAP Training"),
]

CAMPAIGN_NAMES = [
    "DevOps Leadership 2026", "Agentic AI Awareness", "Gen AI Transformation",
    "Azure DevOps Skills", "PMP Career Accelerator", "AI Scrum Master Program",
    "SAP S/4HANA Skills", "Professional Information Subscription",
    "Smart Farming Equipment Demo", "Event Decoration Season",
    "Legal Consultation Awareness", "Product Owner AI Readiness",
    "APAC Technology Leaders", "Europe Digital Transformation",
    "AMEA Business Growth", "WW Customer Engagement",
    "IT Decision Maker Nurture", "High Intent Re-engagement",
    "Webinar Conversion Program", "Customer Expansion",
    "Lead Generation Sprint", "Product Education Series",
    "Regional Demand Generation", "Partner Enablement", "Lifecycle Nurture",
]

def _write(df: pd.DataFrame, filename: str) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_DIR / filename, index=False)
    return len(df)

def generate_products():
    rows = [{"product_id": pid, "product_name": name, "business_type": business}
            for pid, name, business in PRODUCTS]
    return _write(pd.DataFrame(rows), "products.csv")

def generate_accounts(n=1000):
    rows = []
    industries = ["Technology", "Financial Services", "Manufacturing", "Education", "Professional Services", "Agriculture"]
    for i in range(1, n + 1):
        region = random.choice(REGIONS)
        rows.append({
            "account_id": f"ACC-{i:05d}",
            "company_name": fake.company(),
            "industry": random.choice(industries),
            "country": random.choice(COUNTRIES[region]),
            "region": region,
            "employees": random.choice([25, 50, 100, 250, 500, 1000, 5000, 10000]),
            "revenue_band": random.choice(["<$10M", "$10M-$50M", "$50M-$250M", "$250M-$1B", "$1B+"]),
            "account_tier": random.choice(["Tier 1", "Tier 2", "Tier 3"]),
        })
    return _write(pd.DataFrame(rows), "accounts.csv")

def generate_contacts(n=10000):
    rows = []
    titles = ["IT Manager", "Director of Technology", "Software Engineer", "Product Owner",
              "Scrum Master", "Project Manager", "Marketing Manager", "Operations Manager",
              "CIO", "Training Manager"]
    stages = ["Known", "Engaged", "MQL", "SQL", "Opportunity", "Customer"]
    industries = ["Technology", "Financial Services", "Manufacturing", "Education", "Professional Services", "Agriculture"]
    for i in range(1, n + 1):
        region = random.choice(REGIONS)
        rows.append({
            "contact_id": f"CON-{i:06d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": f"contact{i}@example.test",
            "account_id": f"ACC-{random.randint(1, 1000):05d}",
            "job_title": random.choice(titles),
            "country": random.choice(COUNTRIES[region]),
            "region": region,
            "industry": random.choice(industries),
            "lifecycle_stage": random.choice(stages),
            "lead_score": random.randint(0, 100),
            "engagement_score": random.randint(0, 100),
            "consent_status": random.choice(["Opted In", "Opted In", "Opted In", "Not Subscribed"]),
        })
    return _write(pd.DataFrame(rows), "contacts.csv")

def generate_campaigns():
    rows = []
    objectives = ["Lead Generation", "Engagement", "Customer Expansion", "Awareness", "Event Registration", "Nurture"]
    statuses = ["Draft", "Planning", "Running", "Completed"]
    for i, name in enumerate(CAMPAIGN_NAMES, 1):
        region = random.choice(REGIONS)
        business = random.choice(BUSINESSES)
        product = random.choice(PRODUCTS)
        rows.append({
            "campaign_id": f"CMP-{i:04d}",
            "campaign_name": name,
            "business_type": business,
            "product_id": product[0],
            "region": region,
            "objective": random.choice(objectives),
            "status": random.choice(statuses),
            "budget": random.randint(5000, 75000),
            "start_date": f"2026-{random.randint(1, 8):02d}-{random.randint(1, 25):02d}",
        })
    return _write(pd.DataFrame(rows), "campaigns.csv")

def generate_activities(n=25000):
    """Generate synthetic activities with a realistic email funnel hierarchy.

    Email events are generated from the same contact/campaign journey so the
    aggregate funnel always follows:
    Email Sent >= Email Opened >= Email Clicked >= Form Submitted.
    """
    rows = []
    next_id = 1

    # Realistic synthetic email funnel.
    sent_count = min(8000, n)
    opened_count = int(sent_count * 0.55)
    clicked_count = int(opened_count * 0.30)
    submitted_count = int(clicked_count * 0.20)

    send_records = []

    # 1. Email Sent
    for _ in range(sent_count):
        record = {
            "activity_id": f"ACT-{next_id:07d}",
            "contact_id": f"CON-{random.randint(1, 10000):06d}",
            "campaign_id": f"CMP-{random.randint(1, len(CAMPAIGN_NAMES)):04d}",
            "activity_type": "Email Sent",
            "channel": "Email",
            "timestamp": fake.date_time_between(
                start_date="-180d", end_date="now"
            ).isoformat(),
        }

        rows.append(record)
        send_records.append(record)
        next_id += 1

    # 2. Email Opened: subset of sent emails
    opened_records = random.sample(send_records, opened_count)

    for source in opened_records:
        rows.append({
            **source,
            "activity_id": f"ACT-{next_id:07d}",
            "activity_type": "Email Opened",
        })
        next_id += 1

    # 3. Email Clicked: subset of opened emails
    clicked_records = random.sample(opened_records, clicked_count)

    for source in clicked_records:
        rows.append({
            **source,
            "activity_id": f"ACT-{next_id:07d}",
            "activity_type": "Email Clicked",
        })
        next_id += 1

    # 4. Form Submitted: subset of clicked emails
    submitted_records = random.sample(clicked_records, submitted_count)

    for source in submitted_records:
        rows.append({
            **source,
            "activity_id": f"ACT-{next_id:07d}",
            "activity_type": "Form Submitted",
        })
        next_id += 1

    # Remaining activities represent other marketing/sales touchpoints.
    other_types = [
        ("Landing Page View", "Web"),
        ("Webinar Registered", "Webinar"),
        ("Webinar Attended", "Webinar"),
        ("Sales Accepted", "Sales"),
    ]

    remaining = n - len(rows)

    for _ in range(remaining):
        activity_type, channel = random.choice(other_types)

        rows.append({
            "activity_id": f"ACT-{next_id:07d}",
            "contact_id": f"CON-{random.randint(1, 10000):06d}",
            "campaign_id": f"CMP-{random.randint(1, len(CAMPAIGN_NAMES)):04d}",
            "activity_type": activity_type,
            "channel": channel,
            "timestamp": fake.date_time_between(
                start_date="-180d", end_date="now"
            ).isoformat(),
        })

        next_id += 1

    random.shuffle(rows)

    return _write(pd.DataFrame(rows), "activities.csv")

def generate_all():
    return {
        "products": generate_products(),
        "accounts": generate_accounts(),
        "contacts": generate_contacts(),
        "campaigns": generate_campaigns(),
        "activities": generate_activities(),
    }

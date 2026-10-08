import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


TENANT_ID = "reetha"

FIRST_NAMES = [
    "Aarav", "Ananya", "Rahul", "Priya", "Vikram",
    "Sneha", "Arjun", "Kavya", "Rohan", "Divya",
    "Kiran", "Meera", "Aditya", "Pooja", "Nikhil",
]

LAST_NAMES = [
    "Reddy", "Kumar", "Sharma", "Rao", "Patel",
    "Singh", "Naidu", "Verma", "Iyer", "Gupta",
]

COURSES = [
    ("CRS-001", "Generative AI", "AI"),
    ("CRS-002", "Data Science", "Data"),
    ("CRS-003", "Python Programming", "Programming"),
    ("CRS-004", "Cloud Computing", "Cloud"),
    ("CRS-005", "AWS Certification", "Cloud"),
    ("CRS-006", "Azure Certification", "Cloud"),
    ("CRS-007", "DevOps Engineering", "DevOps"),
    ("CRS-008", "Cybersecurity", "Security"),
    ("CRS-009", "Power BI Analytics", "Analytics"),
    ("CRS-010", "Machine Learning", "AI"),
    ("CRS-011", "Full Stack Development", "Development"),
    ("CRS-012", "Digital Marketing", "Marketing"),
]

CHANNELS = [
    "Google Ads",
    "Meta",
    "LinkedIn",
    "Instagram",
    "WhatsApp",
    "Email",
    "Organic Search",
]

EVENT_TYPES = [
    "ad_click",
    "landing_page_view",
    "course_page_view",
    "form_started",
    "form_submitted",
    "email_opened",
    "email_clicked",
    "whatsapp_message",
    "webinar_registered",
    "demo_requested",
]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_reetha_dataset(
    output_dir: str | Path,
    seed: int = 42,
    lead_count: int = 250,
    campaign_count: int = 20,
    engagement_count: int = 1500,
    registration_count: int = 100,
    enrollment_count: int = 50,
) -> None:
    """
    Generate deterministic synthetic GTM data for the Reetha tenant.
    """

    random.seed(seed)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_date = datetime(2026, 1, 1)

    # ---------------------------------------------------------
    # Courses
    # ---------------------------------------------------------

    courses = []

    for course_id, name, category in COURSES:
        courses.append(
            {
                "course_id": course_id,
                "tenant_id": TENANT_ID,
                "name": name,
                "category": category,
                "delivery_mode": random.choice(
                    ["online", "classroom", "hybrid"]
                ),
                "duration": random.choice(
                    ["4 weeks", "6 weeks", "8 weeks", "12 weeks"]
                ),
                "price": random.choice(
                    [12000, 18000, 25000, 30000, 45000]
                ),
                "status": "active",
                "created_at": base_date.isoformat(),
                "updated_at": base_date.isoformat(),
            }
        )

    _write_csv(
        output_dir / "courses.csv",
        list(courses[0].keys()),
        courses,
    )

    course_ids = [course["course_id"] for course in courses]

    # ---------------------------------------------------------
    # Campaigns
    # ---------------------------------------------------------

    campaigns = []

    for index in range(1, campaign_count + 1):
        start = base_date + timedelta(days=random.randint(0, 240))
        end = start + timedelta(days=random.randint(7, 30))

        campaigns.append(
            {
                "campaign_id": f"CMP-{index:03d}",
                "tenant_id": TENANT_ID,
                "name": f"Reetha Campaign {index:03d}",
                "channel": random.choice(CHANNELS),
                "campaign_type": random.choice(
                    ["lead_generation", "webinar", "course_promotion"]
                ),
                "status": random.choice(
                    ["active", "completed", "draft"]
                ),
                "start_date": start.date().isoformat(),
                "end_date": end.date().isoformat(),
                "budget": random.choice(
                    [10000, 25000, 50000, 75000, 100000]
                ),
            }
        )

    _write_csv(
        output_dir / "campaigns.csv",
        list(campaigns[0].keys()),
        campaigns,
    )

    campaign_ids = [
        campaign["campaign_id"]
        for campaign in campaigns
    ]

    # ---------------------------------------------------------
    # Leads
    # ---------------------------------------------------------

    lifecycle_stages = [
        "new",
        "contacted",
        "engaged",
        "qualified",
        "demo",
        "enrolled",
    ]

    leads = []

    for index in range(1, lead_count + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        created = base_date + timedelta(
            days=random.randint(0, 270)
        )

        leads.append(
            {
                "lead_id": f"LEAD-{index:04d}",
                "tenant_id": TENANT_ID,
                "first_name": first,
                "last_name": last,
                "email": (
                    f"{first.lower()}.{last.lower()}"
                    f"{index}@example.com"
                ),
                "phone": f"9{random.randint(100000000, 999999999)}",
                "source": random.choice(CHANNELS),
                "lifecycle_stage": random.choice(
                    lifecycle_stages
                ),
                "interest": random.choice(course_ids),
                "course_id": random.choice(course_ids),
                "lead_score": round(
                    random.uniform(20, 95), 2
                ),
                "created_at": created.isoformat(),
                "updated_at": (
                    created + timedelta(
                        days=random.randint(0, 30)
                    )
                ).isoformat(),
            }
        )

    _write_csv(
        output_dir / "leads.csv",
        list(leads[0].keys()),
        leads,
    )

    lead_ids = [lead["lead_id"] for lead in leads]

    # ---------------------------------------------------------
    # Engagements
    # ---------------------------------------------------------

    engagements = []

    for index in range(1, engagement_count + 1):
        occurred = base_date + timedelta(
            days=random.randint(0, 270),
            hours=random.randint(0, 23),
        )

        engagements.append(
            {
                "engagement_id": f"ENG-{index:05d}",
                "tenant_id": TENANT_ID,
                "lead_id": random.choice(lead_ids),
                "channel": random.choice(CHANNELS),
                "event_type": random.choice(EVENT_TYPES),
                "campaign_id": random.choice(campaign_ids),
                "course_id": random.choice(course_ids),
                "occurred_at": occurred.isoformat(),
                "metadata": "{}",
            }
        )

    _write_csv(
        output_dir / "engagements.csv",
        list(engagements[0].keys()),
        engagements,
    )

    # ---------------------------------------------------------
    # Registrations
    # ---------------------------------------------------------

    registrations = []

    for index in range(1, registration_count + 1):
        registered = base_date + timedelta(
            days=random.randint(10, 280)
        )

        registrations.append(
            {
                "registration_id": f"REG-{index:04d}",
                "tenant_id": TENANT_ID,
                "lead_id": random.choice(lead_ids),
                "course_id": random.choice(course_ids),
                "registration_type": random.choice(
                    ["demo", "webinar", "counselling"]
                ),
                "status": random.choice(
                    ["registered", "attended", "cancelled"]
                ),
                "registered_at": registered.isoformat(),
                "converted_at": "",
            }
        )

    _write_csv(
        output_dir / "registrations.csv",
        list(registrations[0].keys()),
        registrations,
    )

    # ---------------------------------------------------------
    # Enrollments
    # ---------------------------------------------------------

    enrollments = []

    for index in range(1, enrollment_count + 1):
        enrollment_date = base_date + timedelta(
            days=random.randint(20, 290)
        )

        enrollments.append(
            {
                "enrollment_id": f"ENR-{index:04d}",
                "tenant_id": TENANT_ID,
                "lead_id": random.choice(lead_ids),
                "course_id": random.choice(course_ids),
                "enrollment_status": random.choice(
                    ["active", "completed", "in_progress"]
                ),
                "enrollment_date": enrollment_date.isoformat(),
                "amount": random.choice(
                    [12000, 18000, 25000, 30000, 45000]
                ),
                "payment_status": random.choice(
                    ["paid", "partial"]
                ),
            }
        )

    _write_csv(
        output_dir / "enrollments.csv",
        list(enrollments[0].keys()),
        enrollments,
    )

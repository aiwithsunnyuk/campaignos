from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/synthetic")


def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def load_all():
    return {
        name: load_csv(name)
        for name in [
            "products",
            "accounts",
            "contacts",
            "campaigns",
            "activities",
        ]
    }


def load_contacts() -> pd.DataFrame:
    return load_csv("contacts")


def load_campaigns() -> pd.DataFrame:
    return load_csv("campaigns")


def load_activities() -> pd.DataFrame:
    return load_csv("activities")


def load_accounts() -> pd.DataFrame:
    return load_csv("accounts")


def load_products() -> pd.DataFrame:
    return load_csv("products")
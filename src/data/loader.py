from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/synthetic")

def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def load_all():
    return {name: load_csv(name) for name in
            ["products", "accounts", "contacts", "campaigns", "activities"]}

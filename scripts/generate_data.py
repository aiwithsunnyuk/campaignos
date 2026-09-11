from src.data.generator import generate_all

if __name__ == "__main__":
    counts = generate_all()
    print("CampaignOS synthetic data generated:")
    for name, count in counts.items():
        print(f"  {name}: {count}")

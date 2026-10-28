
import pandas as pd
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"


def generate_data(number_of_records=100_000):
    DATA_FOLDER.mkdir(exist_ok=True)

    # Create reference codes
    reference = pd.DataFrame({
        "code": [f"C{i:05d}" for i in range(1, 1001)],
        "valid_from": ["2026-01-01"] * 1000,
        "valid_to": ["2026-12-31"] * 1000,
        "status": ["ACTIVE"] * 1000,
        "reference_version": ["v1"] * 1000
    })

    # Create incoming records
    codes = [f"C{i:05d}" for i in range(1, 1201)]

    incoming = pd.DataFrame({
        "record_id": range(1, number_of_records + 1),
        "code": [
            codes[i % len(codes)]
            for i in range(number_of_records)
        ],
        "check_date": ["2026-10-28"] * number_of_records
    })

    # Save generated files separately from the sample data
    incoming.to_csv(DATA_FOLDER / "large_incoming.csv", index=False)
    reference.to_csv(DATA_FOLDER / "large_reference.csv", index=False)

    print(f"Generated {len(incoming):,} incoming records.")
    print(f"Generated {len(reference):,} reference records.")
    print("Files saved in the data folder.")


if __name__ == "__main__":
    generate_data()

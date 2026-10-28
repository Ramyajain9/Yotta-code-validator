
import logging
import pandas as pd
from pathlib import Path
from validator import validate_codes

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"

logging.basicConfig(
    filename=DATA_FOLDER / "validation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

try:
    incoming = pd.read_csv(DATA_FOLDER / "incoming.csv")
    reference = pd.read_csv(DATA_FOLDER / "reference.csv")

    logging.info("Validation started")
    logging.info("Incoming records: %s", len(incoming))

    result = validate_codes(incoming, reference)

    # Save validation output
    output_file = DATA_FOLDER / "output.csv"
    result.to_csv(output_file, index=False)

    # Count records by status
    summary = result["status"].value_counts()

    # Create reconciliation report
    report = summary.rename_axis("status").reset_index(name="record_count")

    # Add total number of processed records
    total_row = pd.DataFrame({
        "status": ["TOTAL"],
        "record_count": [len(result)]
    })

    report = pd.concat([report, total_row], ignore_index=True)

    # Save reconciliation report
    report_file = DATA_FOLDER / "reconciliation.csv"
    report.to_csv(report_file, index=False)

    print("Validation completed!")
    print("\nReconciliation report:")
    print(report.to_string(index=False))
    print(f"\nOutput saved to: {output_file}")
    print(f"Report saved to: {report_file}")

    logging.info("Validation completed successfully")

except Exception:
    logging.exception("Validation failed")
    raise



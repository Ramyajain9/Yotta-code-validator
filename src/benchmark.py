
import time
import pandas as pd
from pathlib import Path
from validator import validate_codes


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"


def run_benchmark():
    incoming_file = DATA_FOLDER / "large_incoming.csv"
    reference_file = DATA_FOLDER / "large_reference.csv"

    print("Loading large datasets...")

    incoming = pd.read_csv(incoming_file)
    reference = pd.read_csv(reference_file)

    print(f"Incoming records: {len(incoming):,}")
    print(f"Reference records: {len(reference):,}")

    print("\nStarting validation...")
    start_time = time.perf_counter()

    result = validate_codes(incoming, reference)

    end_time = time.perf_counter()
    elapsed_seconds = end_time - start_time

    # Count validation results
    summary = result["status"].value_counts()

    print("\nValidation completed!")
    print(f"Processing time: {elapsed_seconds:.2f} seconds")
    print(f"Records processed: {len(result):,}")

    if elapsed_seconds > 0:
        records_per_second = len(result) / elapsed_seconds
        print(f"Processing speed: {records_per_second:,.0f} records/second")

    print("\nStatus summary:")
    print(summary.to_string())

    # Save benchmark output separately
    output_file = DATA_FOLDER / "large_output.csv"
    result.to_csv(output_file, index=False)

    # Save benchmark metrics
    metrics = pd.DataFrame([{
        "incoming_records": len(incoming),
        "reference_records": len(reference),
        "output_records": len(result),
        "processing_seconds": round(elapsed_seconds, 2),
        "records_per_second": round(
            len(result) / elapsed_seconds, 2
        ) if elapsed_seconds > 0 else None
    }])

    metrics_file = DATA_FOLDER / "benchmark_metrics.csv"
    metrics.to_csv(metrics_file, index=False)

    print(f"\nLarge output saved to: {output_file}")
    print(f"Benchmark metrics saved to: {metrics_file}")


if __name__ == "__main__":
    run_benchmark()

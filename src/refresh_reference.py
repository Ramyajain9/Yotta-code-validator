
import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from .validator import validate_codes
except ImportError:
    from validator import validate_codes


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"
ARCHIVE_FOLDER = DATA_FOLDER / "reference_archive"
CURRENT_REFERENCE = DATA_FOLDER / "reference.csv"


def refresh_reference(new_reference_file):
    new_reference_file = Path(new_reference_file)

    if not new_reference_file.is_absolute():
        new_reference_file = PROJECT_FOLDER / new_reference_file

    if not new_reference_file.exists():
        raise FileNotFoundError(
            f"New reference file not found: {new_reference_file}"
        )

    # Load the new reference data
    new_reference = pd.read_csv(new_reference_file)

    # Validate the new data before replacing the current reference
    empty_incoming = pd.DataFrame({
        "record_id": [],
        "code": [],
        "check_date": []
    })

    validate_codes(empty_incoming, new_reference)

    # Assign a version if the file does not contain one
    if "reference_version" not in new_reference.columns:
        version = datetime.now(timezone.utc).strftime(
            "v%Y%m%d%H%M%S"
        )
        new_reference["reference_version"] = version

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=DATA_FOLDER / "reference_refresh.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True
    )

    temporary_path = None

    try:
        # Write the new reference to a temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            prefix="reference_",
            dir=DATA_FOLDER,
            delete=False,
            newline="",
            encoding="utf-8"
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            new_reference.to_csv(temporary_file, index=False)

        # Archive the current reference before replacing it
        if CURRENT_REFERENCE.exists():
            timestamp = datetime.now(timezone.utc).strftime(
                "%Y%m%d%H%M%S%f"
            )

            archive_file = ARCHIVE_FOLDER / (
                f"reference_{timestamp}.csv"
            )

            shutil.copy2(CURRENT_REFERENCE, archive_file)

        # Replace the current reference with the prepared file
        os.replace(temporary_path, CURRENT_REFERENCE)
        temporary_path = None

        logging.info(
            "Reference refresh completed. Records: %s",
            len(new_reference)
        )

        print("Reference refresh completed successfully.")
        print(f"Records loaded: {len(new_reference)}")
        print(f"Current reference: {CURRENT_REFERENCE}")
        print(f"Archived references: {ARCHIVE_FOLDER}")

    except Exception:
        logging.exception("Reference refresh failed")
        raise

    finally:
        # Remove any temporary file left behind
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


if __name__ == "__main__":
    refresh_reference("data/new_reference.csv")


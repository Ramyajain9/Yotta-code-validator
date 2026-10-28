# Data Dictionary

## 1. Incoming Data: incoming.csv

| Column | Description | Example |
|---|---|---|
| record_id | Identifier for an incoming record | 1 |
| code | Code that needs validation | A101 |
| check_date | Date on which the code is checked | 2026-10-28 |

## 2. Reference Data: reference.csv

| Column | Description | Example |
|---|---|---|
| code | Code stored in the reference dataset | A101 |
| valid_from | First date the code is valid | 2026-01-01 |
| valid_to | Last date the code is valid; may be empty | 2026-12-31 |
| status | Reference status: ACTIVE or DEPRECATED | ACTIVE |
| reference_version | Version identifier for the reference dataset | v2 |

The `valid_from` and `valid_to` dates define the effective period. An empty `valid_to` means there is no specified end date.

## 3. Validation Output: output.csv

The output preserves incoming record information, matching reference information, and the final validation result.

| Column | Description |
|---|---|
| record_id | Incoming record identifier |
| code | Incoming code |
| check_date | Date used for validation |
| valid_from | Reference start date, when matched |
| valid_to | Reference end date, when matched |
| reference_status | Status stored in the reference data |
| reference_version | Reference version, when available |
| status | Final validation result |

Additional reference columns may also appear in the output.

## 4. Validation Statuses

| Status | Meaning |
|---|---|
| VALID | The code is active on the check date |
| EXPIRED | The check date is after the validity end date |
| DEPRECATED | The reference code is marked as deprecated |
| UNKNOWN | The code does not match a reference code |
| NOT_YET_VALID | The check date is before the validity start date |
| DATA_QUALITY_ERROR | The incoming code or check date is missing or invalid |

Invalid reference statuses, duplicate reference codes, missing or invalid start dates, and invalid date ranges cause validation errors.

## 5. Reconciliation Report

The reconciliation report contains the number of records in each validation category and a `TOTAL` row showing the number of processed records.

## 6. Reference Refresh

The reference refresh workflow validates a new reference dataset before replacing the current reference file. When a current file exists, it saves an archive copy before replacement.

- Current reference: `data/reference.csv`
- New reference input: `data/new_reference.csv`
- Archive folder: `data/reference_archive/`

Reference snapshots are archived locally. The current implementation does not provide a separate command to select any historical snapshot for validation.


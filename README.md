# Versioned Reference Code Validator

## 1. Project Overview

This project is a local Python data engineering solution that validates incoming codes against a reference dataset.

It checks reference status and effective dates to classify records as VALID, EXPIRED, DEPRECATED, UNKNOWN, NOT_YET_VALID, or DATA_QUALITY_ERROR.

The application produces validation output, reconciliation reports, execution logs, and performance metrics. It also supports refreshing reference data after validation and archiving the previous version.

## 2. Technologies Used

- Python
- pandas
- pytest
- CSV
- Git and GitHub

## 3. Project Structure

```text
Yotta-code-validator/
├── data/
│   ├── incoming.csv
│   ├── reference.csv
│   └── reference_archive/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── ai_prompt_history.md
├── src/
│   ├── validator.py
│   ├── main.py
│   ├── generate_data.py
│   ├── benchmark.py
│   └── refresh_reference.py
├── tests/
│   ├── test_validator.py
│   └── test_refresh_reference.py
├── .gitignore
├── README.md
└── requirements.txt
```

## 4. Installation

Install Python and open the project folder in VS Code.

Install the required packages:

```bash
pip install -r requirements.txt
```

## 5. How to Run

### Run automated tests

```bash
python -m pytest -v
```

### Validate the sample data

```bash
python src/main.py
```

### Generate a large synthetic dataset

```bash
python src/generate_data.py
```

### Run the performance benchmark

```bash
python src/benchmark.py
```

### Refresh the reference dataset

Prepare a valid new reference CSV at `data/new_reference.csv`, then run:

```bash
python src/refresh_reference.py
```

The refresh workflow validates the incoming reference data, archives the current reference, and replaces it with the new dataset.

## 6. Input Data

### Incoming data

`data/incoming.csv` contains:

- `record_id`: record identifier
- `code`: code to validate
- `check_date`: date on which the code is checked

### Reference data

`data/reference.csv` contains:

- `code`: reference code
- `valid_from`: start date of validity
- `valid_to`: end date of validity; may be empty
- `status`: ACTIVE or DEPRECATED
- `reference_version`: reference dataset version

## 7. Validation Statuses

| Status | Meaning |
|---|---|
| VALID | Active code within its effective dates |
| EXPIRED | Active code checked after its end date |
| DEPRECATED | Code marked as deprecated |
| UNKNOWN | Code not found in the reference data |
| NOT_YET_VALID | Check date is before the start date |
| DATA_QUALITY_ERROR | Incoming code or check date is missing or invalid |

Invalid reference statuses, duplicate reference codes, and invalid reference date ranges cause validation errors.

## 8. Outputs

- `data/output.csv`: record-level validation results
- `data/reconciliation.csv`: counts by status and total records
- `data/validation.log`: validation execution logs
- `data/reference_archive/`: archived reference snapshots
- `data/large_output.csv`: benchmark validation results
- `data/benchmark_metrics.csv`: benchmark timing and throughput

Generated files may be excluded from Git using `.gitignore`.

## 9. Testing

The automated test suite contains 10 tests covering validation rules, missing values, duplicate reference codes, reference versions, invalid statuses, invalid date ranges, not-yet-valid codes, reference refresh, archiving, and rejection of invalid reference data.

Run the tests with:

```bash
python -m pytest -v
```

## 10. Performance

A local benchmark was run using 100,000 incoming records and 1,000 reference records.

| Metric | Measured result |
|---|---:|
| Incoming records | 100,000 |
| Reference records | 1,000 |
| Validation time | 0.10 seconds |
| Validation throughput | 1,025,385 records/second |

These measurements reflect one local run and may vary by machine and dataset. The reported timing measures validation processing, excluding CSV loading and output writing.

## 11. Limitations and Future Improvements

- Reference data is stored in CSV files rather than a database.
- Historical reference snapshots are archived, but selecting and validating against an arbitrary historical version is not yet implemented.
- Additional checks are needed for malformed reference dates and overlapping effective periods.
- The application currently runs locally as a single process.
- Further tests and benchmarks can improve confidence in larger production workloads.

## 12. AI Assistance

AI assistance was used for code explanations, debugging, test design, and documentation. The prompt-history document summarizes this assistance. The developer reviewed and ran the project locally and should be able to explain its implementation and limitations.


# Architecture and Design

## 1. Overview

The Versioned Reference Code Validator is a local data engineering application built using Python and pandas.

It validates incoming codes against reference data, checks effective dates, identifies data-quality issues, generates reconciliation reports, and supports reference-data refreshes.

## 2. System Architecture

```text
 Incoming CSV
      |
      v
 Load Incoming and Reference Data
      |
      v
 Check Required Columns and Reference Quality
      |
      v
 Match Incoming Codes with Reference Codes
      |
      v
 Apply Effective-Date and Status Rules
      |
      v
 Assign Validation Results
      |
      v
 Save Output CSV
      |
      v
 Generate Reconciliation Report
      |
      v
 Record Execution Logs
```

The reference-refresh workflow is separate:

```text
 New Reference CSV
       |
       v
 Validate New Reference Data
       |
       v
 Save Current Reference Archive
       |
       v
 Replace Current Reference CSV
```

## 3. Main Components

### Validator — `src/validator.py`

Matches incoming codes with reference codes and assigns validation statuses. It also checks required columns, duplicate reference codes, reference statuses, and effective-date ranges.

### Main Application — `src/main.py`

Loads the sample input files, runs validation, saves record-level results, generates a reconciliation report, and records execution logs.

### Data Generator — `src/generate_data.py`

Creates synthetic reference data and at least 100,000 incoming records for scalability testing.

### Benchmark — `src/benchmark.py`

Measures validation execution time and processing throughput for the generated dataset. Its timing excludes CSV loading and output writing.

### Reference Refresh — `src/refresh_reference.py`

Validates a new reference dataset, archives the current reference file, and replaces it with the new version. Invalid reference data is rejected before replacement.

### Automated Tests — `tests/`

The test suite checks validation behavior and reference-refresh operations, including archiving and rejection of invalid reference data.

## 4. Validation Rules

1. Required input columns must be present.
2. Missing reference codes and duplicate reference codes cause errors.
3. Reference statuses must be `ACTIVE` or `DEPRECATED`.
4. Reference start dates must be valid.
5. A reference end date cannot be earlier than its start date.
6. An unmatched incoming code is classified as `UNKNOWN`.
7. A deprecated reference code is classified as `DEPRECATED`.
8. An active code checked before its start date is classified as `NOT_YET_VALID`.
9. An active code checked after its end date is classified as `EXPIRED`.
10. An active code checked within its effective dates is classified as `VALID`.
11. Missing or invalid incoming codes or check dates are classified as `DATA_QUALITY_ERROR`.

## 5. Outputs and Observability

| Output | Purpose |
|---|---|
| `data/output.csv` | Validation result for each incoming record |
| `data/reconciliation.csv` | Counts by status and total records |
| `data/validation.log` | Validation execution logs |
| `data/reference_archive/` | Archived reference snapshots |
| `data/large_output.csv` | Results for the generated dataset |
| `data/benchmark_metrics.csv` | Processing time and throughput measurements |

## 6. Testing and Performance

Automated tests are run with:

```bash
python -m pytest -v
```

The benchmark uses 100,000 incoming records and 1,000 reference records. One local run processed 100,000 records in 0.10 seconds, at approximately 1,025,385 records per second.

Results vary by computer and dataset. This measures the validation function rather than the complete file-processing workflow.

## 7. Limitations

- The application uses local CSV files rather than a database.
- Reference snapshots are archived, but the application does not yet offer a dedicated workflow for selecting and validating against any historical version.
- Malformed non-empty end dates and overlapping effective periods need additional validation checks.
- The application runs locally as a single process.
- More tests and benchmarks are needed before production use.

## 8. Future Improvements

- Add stricter validation for malformed reference dates.
- Detect overlapping effective periods and support multiple effective-dated entries per code.
- Add a way to select historical reference versions.
- Improve metrics and structured logging.
- Test larger datasets and document end-to-end performance.


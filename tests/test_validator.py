
import pandas as pd
import pytest

from src.validator import validate_codes


def test_validate_codes():
    incoming = pd.DataFrame({
        "record_id": [1, 2, 3, 4],
        "code": ["A101", "B202", "X999", "C303"],
        "check_date": [
            "2026-10-28",
            "2026-10-28",
            "2026-10-28",
            "2026-10-28"
        ]
    })

    reference = pd.DataFrame({
        "code": ["A101", "B202", "C303", "D404"],
        "valid_from": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-01",
            "2026-01-01"
        ],
        "valid_to": [
            "2026-12-31",
            "2026-06-30",
            None,
            None
        ],
        "status": [
            "ACTIVE",
            "ACTIVE",
            "DEPRECATED",
            "ACTIVE"
        ],
        "reference_version": ["v1", "v1", "v1", "v1"]
    })

    result = validate_codes(incoming, reference)

    assert result["status"].tolist() == [
        "VALID",
        "EXPIRED",
        "UNKNOWN",
        "DEPRECATED"
    ]


def test_missing_code():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": [None],
        "check_date": ["2026-10-28"]
    })

    reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-12-31"],
        "status": ["ACTIVE"]
    })

    result = validate_codes(incoming, reference)

    assert result.loc[0, "status"] == "DATA_QUALITY_ERROR"


def test_missing_date():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": ["A101"],
        "check_date": [None]
    })

    reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-12-31"],
        "status": ["ACTIVE"]
    })

    result = validate_codes(incoming, reference)

    assert result.loc[0, "status"] == "DATA_QUALITY_ERROR"


def test_duplicate_reference_codes():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": ["A101"],
        "check_date": ["2026-10-28"]
    })

    reference = pd.DataFrame({
        "code": ["A101", "A101"],
        "valid_from": ["2026-01-01", "2026-01-01"],
        "valid_to": ["2026-12-31", "2026-12-31"],
        "status": ["ACTIVE", "ACTIVE"]
    })

    with pytest.raises(
        ValueError,
        match="Duplicate codes found in reference data"
    ):
        validate_codes(incoming, reference)


def test_reference_version_is_preserved():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": ["A101"],
        "check_date": ["2026-10-28"]
    })

    reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-12-31"],
        "status": ["ACTIVE"],
        "reference_version": ["v1"]
    })

    result = validate_codes(incoming, reference)

    assert result.loc[0, "status"] == "VALID"
    assert result.loc[0, "reference_version"] == "v1"


def test_invalid_reference_status():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": ["A101"],
        "check_date": ["2026-10-28"]
    })

    reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-12-31"],
        "status": ["WRONG_STATUS"]
    })

    with pytest.raises(
        ValueError,
        match="Invalid statuses found in reference data"
    ):
        validate_codes(incoming, reference)


def test_invalid_reference_date_range():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": ["A101"],
        "check_date": ["2026-10-28"]
    })

    reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-12-31"],
        "valid_to": ["2026-01-01"],
        "status": ["ACTIVE"]
    })

    with pytest.raises(
        ValueError,
        match="Invalid reference date ranges found"
    ):
        validate_codes(incoming, reference)


def test_not_yet_valid_code():
    incoming = pd.DataFrame({
        "record_id": [1],
        "code": ["A101"],
        "check_date": ["2025-12-31"]
    })

    reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-12-31"],
        "status": ["ACTIVE"]
    })

    result = validate_codes(incoming, reference)

    assert result.loc[0, "status"] == "NOT_YET_VALID"


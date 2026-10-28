
import pandas as pd


def validate_codes(incoming, reference):
    incoming = incoming.copy()
    reference = reference.copy()

    # Check required incoming columns
    required_incoming = {"record_id", "code", "check_date"}
    missing_columns = required_incoming - set(incoming.columns)

    if missing_columns:
        raise ValueError(
            f"Missing incoming columns: {sorted(missing_columns)}"
        )

    # Check required reference columns
    required_reference = {
        "code", "valid_from", "valid_to", "status"
    }
    missing_columns = required_reference - set(reference.columns)

    if missing_columns:
        raise ValueError(
            f"Missing reference columns: {sorted(missing_columns)}"
        )

    # Clean codes and statuses
    incoming["code"] = incoming["code"].replace(
        r"^\s*$", pd.NA, regex=True
    )

    reference["code"] = reference["code"].replace(
        r"^\s*$", pd.NA, regex=True
    )

    incoming["code"] = incoming["code"].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

    reference["code"] = reference["code"].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

    reference["status"] = (
        reference["status"].astype("string").str.strip().str.upper()
    )

    # Reject missing reference codes
    if reference["code"].isna().any():
        raise ValueError("Missing codes found in reference data")

    # Reject duplicate reference codes
    if reference["code"].duplicated().any():
        raise ValueError("Duplicate codes found in reference data")

    # Check reference statuses
    allowed_statuses = {"ACTIVE", "DEPRECATED"}

    invalid_status = (
        reference["status"].isna()
        | ~reference["status"].isin(allowed_statuses)
    )

    if invalid_status.any():
        raise ValueError("Invalid statuses found in reference data")

    # Parse reference dates
    reference["valid_from"] = pd.to_datetime(
        reference["valid_from"], errors="coerce"
    )

    reference["valid_to"] = pd.to_datetime(
        reference["valid_to"], errors="coerce"
    )

    # Start date is required
    if reference["valid_from"].isna().any():
        raise ValueError("Missing or invalid valid_from dates")

    # End date cannot be earlier than start date
    invalid_range = (
        reference["valid_to"].notna()
        & (reference["valid_to"] < reference["valid_from"])
    )

    if invalid_range.any():
        raise ValueError("Invalid reference date ranges found")

    # Preserve the reference status separately
    reference = reference.rename(
        columns={"status": "reference_status"}
    )

    # Match incoming records with reference data
    result = incoming.merge(
        reference,
        on="code",
        how="left",
        indicator=True,
        validate="many_to_one"
    )

    # Parse incoming check dates
    result["check_date"] = pd.to_datetime(
        result["check_date"], errors="coerce"
    )

    # Set the default result
    result["status"] = "UNKNOWN"

    # Identify data-quality problems
    missing_code = result["code"].isna()

    missing_date = result["check_date"].isna()

    # Identify matched reference records
    found = result["_merge"] == "both"

    # Deprecated codes
    deprecated = (
        found
        & (result["reference_status"] == "DEPRECATED")
    )

    result.loc[deprecated, "status"] = "DEPRECATED"

    # Active codes checked before their start date
    not_yet_valid = (
        found
        & (result["reference_status"] == "ACTIVE")
        & result["valid_from"].notna()
        & (result["check_date"] < result["valid_from"])
    )

    result.loc[not_yet_valid, "status"] = "NOT_YET_VALID"

    # Active codes checked after their end date
    expired = (
        found
        & (result["reference_status"] == "ACTIVE")
        & result["valid_to"].notna()
        & (result["check_date"] > result["valid_to"])
    )

    result.loc[expired, "status"] = "EXPIRED"

    # Active codes within their effective dates
    active = (
        found
        & (result["reference_status"] == "ACTIVE")
        & result["valid_from"].notna()
        & (result["check_date"] >= result["valid_from"])
        & (
            result["valid_to"].isna()
            | (result["check_date"] <= result["valid_to"])
        )
    )

    result.loc[active, "status"] = "VALID"

    # Data-quality errors take priority
    data_quality_error = missing_code | missing_date

    result.loc[
        data_quality_error, "status"
    ] = "DATA_QUALITY_ERROR"

    # Remove the temporary merge indicator
    result = result.drop(columns=["_merge"])

    return result


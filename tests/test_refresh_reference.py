
import pandas as pd
import pytest

from src.refresh_reference import refresh_reference


def test_refresh_reference_archives_old_version(tmp_path, monkeypatch):
    # Create temporary project folders for this test
    data_folder = tmp_path / "data"
    archive_folder = data_folder / "reference_archive"
    data_folder.mkdir()

    current_reference = data_folder / "reference.csv"

    # Create the old reference dataset
    old_reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-06-30"],
        "status": ["ACTIVE"],
        "reference_version": ["v1"]
    })

    old_reference.to_csv(current_reference, index=False)

    # Create the new reference dataset
    new_reference_file = tmp_path / "new_reference.csv"

    new_reference = pd.DataFrame({
        "code": ["A101", "B202"],
        "valid_from": ["2026-01-01", "2026-01-01"],
        "valid_to": ["2026-12-31", "2026-12-31"],
        "status": ["ACTIVE", "ACTIVE"],
        "reference_version": ["v2", "v2"]
    })

    new_reference.to_csv(new_reference_file, index=False)

    # Redirect refresh paths to the temporary test folders
    monkeypatch.setattr(
        "src.refresh_reference.DATA_FOLDER", data_folder
    )
    monkeypatch.setattr(
        "src.refresh_reference.ARCHIVE_FOLDER", archive_folder
    )
    monkeypatch.setattr(
        "src.refresh_reference.CURRENT_REFERENCE",
        current_reference
    )

    # Run the refresh
    refresh_reference(new_reference_file)

    # Confirm the new version is current
    current_data = pd.read_csv(current_reference)

    assert len(current_data) == 2
    assert set(current_data["reference_version"]) == {"v2"}

    # Confirm the old version was archived
    archived_files = list(archive_folder.glob("reference_*.csv"))

    assert len(archived_files) == 1

    archived_data = pd.read_csv(archived_files[0])

    assert archived_data.loc[0, "reference_version"] == "v1"
    assert archived_data.loc[0, "valid_to"] == "2026-06-30"


def test_refresh_rejects_invalid_reference(tmp_path, monkeypatch):
    data_folder = tmp_path / "data"
    archive_folder = data_folder / "reference_archive"
    data_folder.mkdir()

    current_reference = data_folder / "reference.csv"

    old_reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-01-01"],
        "valid_to": ["2026-12-31"],
        "status": ["ACTIVE"],
        "reference_version": ["v1"]
    })

    old_reference.to_csv(current_reference, index=False)

    invalid_reference_file = tmp_path / "invalid_reference.csv"

    invalid_reference = pd.DataFrame({
        "code": ["A101"],
        "valid_from": ["2026-12-31"],
        "valid_to": ["2026-01-01"],
        "status": ["ACTIVE"],
        "reference_version": ["v2"]
    })

    invalid_reference.to_csv(invalid_reference_file, index=False)

    monkeypatch.setattr(
        "src.refresh_reference.DATA_FOLDER", data_folder
    )
    monkeypatch.setattr(
        "src.refresh_reference.ARCHIVE_FOLDER", archive_folder
    )
    monkeypatch.setattr(
        "src.refresh_reference.CURRENT_REFERENCE",
        current_reference
    )

    # An invalid reference must be rejected
    with pytest.raises(
        ValueError,
        match="Invalid reference date ranges found"
    ):
        refresh_reference(invalid_reference_file)

    # The original current reference must remain unchanged
    current_data = pd.read_csv(current_reference)

    assert current_data.loc[0, "reference_version"] == "v1"
    assert current_data.loc[0, "valid_to"] == "2026-12-31"

    # No archive should be created for a rejected refresh
    assert not archive_folder.exists()

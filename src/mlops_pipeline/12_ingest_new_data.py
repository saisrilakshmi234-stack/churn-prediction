
import argparse
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

CURRENT_FILE = ROOT / "data/raw/churn.csv"
INCOMING_FILE = ROOT / "data/raw/new_churn.csv"
BACKUP_DIR = ROOT / "backups"
ARCHIVE_DIR = ROOT / "data/archive"
REPORT_FILE = ROOT / "outputs/monitoring/ingestion_report.json"

EXPECTED_COLUMNS = [
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
    "tenure", "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
    "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"
]

ALLOWED_VALUES = {
    "gender": {"Female", "Male"},
    "Partner": {"Yes", "No"},
    "Dependents": {"Yes", "No"},
    "PhoneService": {"Yes", "No"},
    "MultipleLines": {"Yes", "No", "No phone service"},
    "InternetService": {"DSL", "Fiber optic", "No"},
    "OnlineSecurity": {"Yes", "No", "No internet service"},
    "OnlineBackup": {"Yes", "No", "No internet service"},
    "DeviceProtection": {"Yes", "No", "No internet service"},
    "TechSupport": {"Yes", "No", "No internet service"},
    "StreamingTV": {"Yes", "No", "No internet service"},
    "StreamingMovies": {"Yes", "No", "No internet service"},
    "Contract": {"Month-to-month", "One year", "Two year"},
    "PaperlessBilling": {"Yes", "No"},
    "PaymentMethod": {
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)"
    },
    "Churn": {"Yes", "No"},
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_incoming(incoming, current):
    if list(incoming.columns) != EXPECTED_COLUMNS:
        raise ValueError("Incoming columns do not match expected schema.")

    if list(current.columns) != EXPECTED_COLUMNS:
        raise ValueError("Current columns do not match expected schema.")

    if incoming.empty:
        raise ValueError("Incoming dataset is empty.")

    if incoming.isna().any().any():
        raise ValueError("Incoming dataset contains missing values.")

    if incoming.astype(str).apply(
        lambda col: col.str.strip().eq("").any()
    ).any():
        raise ValueError("Incoming dataset contains blank values.")

    for column, allowed in ALLOWED_VALUES.items():
        invalid = set(incoming[column].astype(str)) - allowed
        if invalid:
            raise ValueError(
                f"Invalid values in {column}: {sorted(invalid)}"
            )

    for column in [
        "SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"
    ]:
        incoming[column] = pd.to_numeric(
            incoming[column], errors="raise"
        )

    if not incoming["SeniorCitizen"].isin([0, 1]).all():
        raise ValueError("SeniorCitizen must be 0 or 1.")

    if not incoming["tenure"].between(0, 72).all():
        raise ValueError("tenure must be between 0 and 72.")

    if not incoming["tenure"].mod(1).eq(0).all():
        raise ValueError("tenure must contain whole numbers.")

    if not incoming["MonthlyCharges"].between(0, 120).all():
        raise ValueError("MonthlyCharges must be between 0 and 120.")

    if (incoming["TotalCharges"] < 0).any():
        raise ValueError("TotalCharges cannot be negative.")

    if incoming["customerID"].duplicated().any():
        raise ValueError("Duplicate IDs in incoming data.")

    if current["customerID"].duplicated().any():
        raise ValueError("Duplicate IDs in current data.")

    existing_ids = set(current["customerID"].astype(str))
    incoming_ids = set(incoming["customerID"].astype(str))

    if existing_ids.intersection(incoming_ids):
        raise ValueError("Incoming data contains existing customer IDs.")

    return incoming


def make_temp_file(directory, suffix):
    fd, name = tempfile.mkstemp(suffix=suffix, dir=directory)
    os.close(fd)
    return Path(name)


def ingest(commit=False):
    if not CURRENT_FILE.exists() or not INCOMING_FILE.exists():
        raise FileNotFoundError("Current or incoming dataset is missing.")

    incoming_hash = sha256(INCOMING_FILE)
    archive_file = ARCHIVE_DIR / f"new_churn_{incoming_hash}.csv"

    if archive_file.exists():
        raise ValueError("This incoming batch has already been archived.")

    current = pd.read_csv(CURRENT_FILE, dtype={"customerID": str})
    incoming = pd.read_csv(INCOMING_FILE, dtype={"customerID": str})

    incoming = validate_incoming(incoming, current)

    original_rows = len(current)
    incoming_rows = len(incoming)
    combined = pd.concat([current, incoming], ignore_index=True)

    if len(combined) != original_rows + incoming_rows:
        raise RuntimeError("Combined row count verification failed.")

    if combined["customerID"].duplicated().any():
        raise RuntimeError("Duplicate IDs found in combined dataset.")

    print("[VALIDATION PASSED]")
    print(f"Original rows: {original_rows}")
    print(f"Incoming rows: {incoming_rows}")
    print(f"Expected total rows: {len(combined)}")
    print(f"Incoming SHA256: {incoming_hash}")

    if not commit:
        print("\n[DRY RUN] No files were modified.")
        print("Run with --commit only after reviewing these results.")
        return

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    backup_file = BACKUP_DIR / f"churn_before_ingestion_{timestamp}.csv"

    # Create and verify backup before preparing the commit.
    shutil.copy2(CURRENT_FILE, backup_file)

    if sha256(CURRENT_FILE) != sha256(backup_file):
        raise RuntimeError("Backup verification failed.")

    archive_temp = make_temp_file(ARCHIVE_DIR, ".tmp")
    data_temp = make_temp_file(CURRENT_FILE.parent, ".csv")
    report_temp = make_temp_file(REPORT_FILE.parent, ".tmp")

    dataset_replaced = False

    try:
        # Prepare and verify archive.
        shutil.copy2(INCOMING_FILE, archive_temp)

        if sha256(archive_temp) != incoming_hash:
            raise RuntimeError("Archive staging verification failed.")

        # Prepare and verify combined dataset.
        combined.to_csv(data_temp, index=False)

        verification = pd.read_csv(
            data_temp, dtype={"customerID": str}
        )

        if len(verification) != len(combined):
            raise RuntimeError("Temporary dataset row count mismatch.")

        if verification["customerID"].duplicated().any():
            raise RuntimeError("Temporary dataset has duplicate IDs.")

        # Prepare report before replacing the original dataset.
        report = {
            "stage": "Lab 13 - Safe Data Ingestion",
            "status": "ingested",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_file": "data/raw/new_churn.csv",
            "archive_file": str(archive_file.relative_to(ROOT)),
            "backup_file": str(backup_file.relative_to(ROOT)),
            "incoming_sha256": incoming_hash,
            "original_rows": original_rows,
            "input_rows": incoming_rows,
            "rows_added": incoming_rows,
            "total_rows": len(combined),
            "duplicate_ids": 0,
            "schema_validation": "passed",
            "data_validation": "passed",
            "backup_validation": "passed",
            "archive_validation": "passed",
            "production_model_changed": False,
            "model_retraining_executed": False,
            "model_promotion_executed": False
        }

        with report_temp.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        # Final safety check immediately before replacing the dataset.
        if sha256(CURRENT_FILE) != sha256(backup_file):
            raise RuntimeError(
                "Current dataset changed after backup. Commit cancelled."
            )

        if archive_file.exists():
            raise RuntimeError("Archive appeared during ingestion.")

        # Commit the prepared files.
        os.replace(data_temp, CURRENT_FILE)
        dataset_replaced = True

        os.replace(archive_temp, archive_file)
        os.replace(report_temp, REPORT_FILE)

    except Exception as error:
        if dataset_replaced:
            raise RuntimeError(
                "Dataset was updated, but a later commit step failed. "
                "Do not rerun ingestion. Check the backup, archive, "
                "and report before proceeding."
            ) from error
        raise

    finally:
        for path in (archive_temp, data_temp, report_temp):
            if path.exists():
                path.unlink()

    print("\n[SUCCESS] Data ingestion completed.")
    print(f"Original rows: {original_rows}")
    print(f"Rows added: {incoming_rows}")
    print(f"Total rows: {len(combined)}")
    print(f"Backup: {backup_file}")
    print(f"Archive: {archive_file}")
    print(f"Report: {REPORT_FILE}")
    print("Incoming source file preserved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually append incoming data. Default is dry-run."
    )
    args = parser.parse_args()

    ingest(commit=args.commit)

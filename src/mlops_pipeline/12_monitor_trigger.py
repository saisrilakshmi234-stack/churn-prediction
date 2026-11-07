import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DRIFT_REPORT = Path("outputs/drift/drift_analysis_report.csv")
NEW_DATA_PATH = Path("data/raw/new_churn.csv")
TRIGGER_REPORT = Path("outputs/monitoring/monitor_trigger_report.json")


def detect_drift():
    if not DRIFT_REPORT.exists():
        raise FileNotFoundError(f"Drift report not found: {DRIFT_REPORT}")

    df = pd.read_csv(DRIFT_REPORT)

    if "status" not in df.columns:
        raise ValueError("Drift report must contain a 'status' column.")

    statuses = df["status"].astype(str).str.strip().str.upper()
    drift_rows = df.loc[statuses == "DRIFT"]

    return len(drift_rows) > 0, drift_rows


def save_trigger_report(report):
    TRIGGER_REPORT.parent.mkdir(parents=True, exist_ok=True)

    with TRIGGER_REPORT.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)


def run_monitor_trigger():
    print("=" * 70)
    print("LAB 12 - READ-ONLY MONITORING TRIGGER")
    print("=" * 70)

    drift_detected, drift_rows = detect_drift()
    new_data_present = NEW_DATA_PATH.exists()

    report = {
        "status": "drift_alert" if drift_detected else "no_drift",
        "monitoring_mode": "read_only",
        "drift_report": str(DRIFT_REPORT),
        "drift_detected": drift_detected,
        "drift_categories": (
            drift_rows["category"].astype(str).tolist()
            if "category" in drift_rows.columns else []
        ),
        "new_data_present": new_data_present,
        "new_data_ingested": False,
        "pipeline_called": False,
        "retraining_executed": False,
        "registry_modified": False,
        "deployment_changed": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    save_trigger_report(report)

    print(f"Drift detected       : {drift_detected}")
    print(f"New data present     : {new_data_present}")
    print("Pipeline called      : False")
    print("Retraining executed  : False")
    print("Registry modified    : False")
    print("Deployment changed   : False")
    print(f"Report saved         : {TRIGGER_REPORT}")

    return True


if __name__ == "__main__":
    run_monitor_trigger()


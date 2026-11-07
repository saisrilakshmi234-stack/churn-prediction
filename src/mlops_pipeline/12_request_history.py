import json
from pathlib import Path

import pandas as pd


LOG_PATH = Path("logs/inference/inference_log.jsonl")
PRODUCTION_MODEL = "Telco_Churn_Production_Model"
CI_MODEL = "CI_Test_Model"


def load_history():
    if not LOG_PATH.exists():
        raise FileNotFoundError(f"Log file not found: {LOG_PATH}")

    with LOG_PATH.open("r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    if not records:
        raise ValueError("Inference history is empty")

    df = pd.DataFrame(records)

    required = {"request_id", "timestamp", "status", "model_name"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required log columns: {sorted(missing)}")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True, errors="coerce"
    )

    return df


def mask_request_id(value):
    if pd.isna(value):
        return "N/A"

    value = str(value)
    return value[:4] + "..." if len(value) > 4 else "****"


def show_group(df, title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    if df.empty:
        print("No requests found.")
        return

    print(f"Total requests: {len(df)}")
    print(f"Successful: {(df['status'] == 'success').sum()}")
    print(f"Failed: {(df['status'] == 'failure').sum()}")

    columns = [
        "request_id",
        "timestamp",
        "prediction",
        "churn_probability",
        "latency_ms",
        "status",
        "model_version",
    ]

    available = [col for col in columns if col in df.columns]
    recent = df.sort_values("timestamp", na_position="last").tail(10).copy()

    recent["request_id"] = recent["request_id"].apply(mask_request_id)

    print("\nLatest requests (maximum 10):")
    print(recent[available].to_string(index=False))


def show_production_failures(df):
    failures = df[df["status"] == "failure"]

    print("\n" + "=" * 65)
    print("PRODUCTION FAILED REQUESTS")
    print("=" * 65)

    if failures.empty:
        print("No failed Production requests.")
        return

    print(f"Failed Production requests: {len(failures)}")

    columns = ["request_id", "timestamp", "status", "model_version"]
    available = [col for col in columns if col in failures.columns]

    failures = failures.copy()
    failures["request_id"] = failures["request_id"].apply(mask_request_id)

    print(failures[available].to_string(index=False))
    print("Raw error messages and customer inputs are hidden.")


def main():
    df = load_history()

    production = df[df["model_name"] == PRODUCTION_MODEL].copy()
    ci = df[df["model_name"] == CI_MODEL].copy()

    other = df[
        ~df["model_name"].isin([PRODUCTION_MODEL, CI_MODEL])
    ].copy()

    print("\nREQUEST HISTORY - PRODUCTION AND CI SEPARATED")
    print(f"Total log records: {len(df)}")

    show_group(production, "PRODUCTION REQUEST HISTORY")
    show_production_failures(production)

    show_group(ci, "CI TEST REQUEST HISTORY")

    if not other.empty:
        print(f"\nOther model records excluded: {len(other)}")


if __name__ == "__main__":
    main()

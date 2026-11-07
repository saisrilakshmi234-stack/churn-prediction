import json
from pathlib import Path

import pandas as pd


LOG_PATH = Path("logs/inference/inference_log.jsonl")
PRODUCTION_MODEL = "Telco_Churn_Production_Model"
CI_MODEL = "CI_Test_Model"


def load_logs():
    if not LOG_PATH.exists():
        raise FileNotFoundError(f"Log file not found: {LOG_PATH}")

    with LOG_PATH.open("r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    if not records:
        raise ValueError("Inference log is empty")

    return pd.DataFrame(records)


def analyze_group(df, title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    if df.empty:
        print("No requests found for this group.")
        return

    total = len(df)
    success = (df["status"] == "success").sum()
    failure = (df["status"] == "failure").sum()

    print(f"Total requests : {total}")
    print(f"Successful     : {success}")
    print(f"Failed         : {failure}")
    print(f"Success rate   : {success / total * 100:.2f}%")
    print(f"Failure rate   : {failure / total * 100:.2f}%")

    latency = pd.to_numeric(df["latency_ms"], errors="coerce").dropna()

    if not latency.empty:
        print("\nLatency:")
        print(f"Average        : {latency.mean():.3f} ms")
        print(f"Median         : {latency.median():.3f} ms")
        print(f"P95            : {latency.quantile(0.95):.3f} ms")
        print(f"Minimum        : {latency.min():.3f} ms")
        print(f"Maximum        : {latency.max():.3f} ms")

    timestamps = pd.to_datetime(df["timestamp"], utc=True, errors="coerce").dropna()

    if len(timestamps) >= 2:
        elapsed = (timestamps.max() - timestamps.min()).total_seconds()

        if elapsed > 0:
            print(f"\nThroughput     : {total / elapsed:.3f} requests/sec")
        else:
            print("\nThroughput     : Cannot calculate from identical timestamps")
    else:
        print("\nThroughput     : Insufficient timestamps")

    print("\nStatus distribution:")
    print(df["status"].value_counts().to_string())


def main():
    df = load_logs()

    if "model_name" not in df.columns:
        raise ValueError("Inference logs must contain model_name.")

    print("\nAPI PERFORMANCE MONITORING - SEPARATED REPORTS")

    production = df[df["model_name"] == PRODUCTION_MODEL].copy()
    ci = df[df["model_name"] == CI_MODEL].copy()
    other = df[~df["model_name"].isin([PRODUCTION_MODEL, CI_MODEL])].copy()

    analyze_group(production, "PRODUCTION API")
    analyze_group(ci, "CI TEST REQUESTS")

    if not other.empty:
        print(f"\nOther model requests excluded from these groups: {len(other)}")


if __name__ == "__main__":
    main()

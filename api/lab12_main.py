import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent

DRIFT_REPORT = BASE_DIR / "outputs" / "drift" / "drift_analysis_report.csv"
COMPARISON_REPORT = BASE_DIR / "outputs" / "retraining" / "model_comparison_report.json"

app = FastAPI(
    title="Churn Prediction - Lab 12 Monitoring API",
    description="Read-only API for drift monitoring and model comparison.",
    version="1.0.0",
)


def load_drift_report():
    if not DRIFT_REPORT.exists():
        raise HTTPException(status_code=503, detail="Drift report is unavailable.")

    try:
        df = pd.read_csv(DRIFT_REPORT)
        return df.where(pd.notna(df), None).to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not read drift report: {exc}")


def load_comparison_report():
    if not COMPARISON_REPORT.exists():
        raise HTTPException(status_code=503, detail="Model comparison report is unavailable.")

    try:
        with COMPARISON_REPORT.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not read comparison report: {exc}")


@app.get("/")
def root():
    return {
        "project": "Churn Prediction MLOps",
        "lab": "Lab 12",
        "service": "Monitoring API",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    drift_available = DRIFT_REPORT.exists()
    comparison_available = COMPARISON_REPORT.exists()

    return {
        "status": "healthy" if drift_available and comparison_available else "degraded",
        "lab": "Lab 12",
        "reports": {
            "drift_report_available": drift_available,
            "model_comparison_report_available": comparison_available,
        },
    }


@app.get("/monitoring/drift")
def get_drift():
    records = load_drift_report()
    return {
        "lab": "Lab 12",
        "report": "Drift Analysis",
        "total_checks": len(records),
        "drift_results": records,
    }


@app.get("/monitoring/model-comparison")
def get_model_comparison():
    return load_comparison_report()


@app.get("/monitoring/summary")
def get_monitoring_summary():
    drift_records = load_drift_report()
    comparison = load_comparison_report()

    drift_count = sum(
        1 for record in drift_records
        if str(record.get("status", "")).upper() == "DRIFT"
    )

    return {
        "lab": "Lab 12",
        "drift_summary": {
            "total_checks": len(drift_records),
            "drift_detected": drift_count,
            "results": drift_records,
        },
        "model_comparison": {
            "production_model": comparison.get("production_model"),
            "retrained_candidate": comparison.get("retrained_candidate"),
            "quality_gate": comparison.get("quality_gate"),
        },
    }

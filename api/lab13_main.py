import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent

INGESTION_REPORT = (
    BASE_DIR / "outputs" / "monitoring" / "ingestion_report.json"
)
PIPELINE_LOG = (
    BASE_DIR / "logs" / "churn_prediction_pipeline_run_log.json"
)

app = FastAPI(
    title="Churn Prediction - Lab 13 Operations API",
    description="Read-only API for safe data ingestion and pipeline execution status.",
    version="1.0.0",
)


def read_json_report(path: Path, report_name: str):
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"{report_name} is unavailable.",
        )

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read {report_name}: {exc}",
        )


@app.get("/")
def root():
    return {
        "project": "Churn Prediction MLOps",
        "lab": "Lab 13",
        "service": "Ingestion and Pipeline Status API",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    ingestion_available = INGESTION_REPORT.exists()
    pipeline_available = PIPELINE_LOG.exists()

    return {
        "status": (
            "healthy"
            if ingestion_available and pipeline_available
            else "degraded"
        ),
        "lab": "Lab 13",
        "reports": {
            "ingestion_report_available": ingestion_available,
            "pipeline_log_available": pipeline_available,
        },
    }


@app.get("/ingestion/status")
def ingestion_status():
    report = read_json_report(INGESTION_REPORT, "Ingestion report")

    return {
        "lab": "Lab 13",
        "report": "Safe Data Ingestion",
        "ingestion": report,
    }


@app.get("/pipeline/status")
def pipeline_status():
    report = read_json_report(PIPELINE_LOG, "Pipeline execution log")

    stages = report.get("stages", [])
    passed = sum(
        1 for stage in stages
        if str(stage.get("status", "")).upper() == "PASSED"
    )
    failed = sum(
        1 for stage in stages
        if str(stage.get("status", "")).upper() == "FAILED"
    )

    return {
        "lab": "Lab 13",
        "report": "Pipeline Execution Status",
        "pipeline": report.get("pipeline"),
        "overall_status": report.get("overall_status"),
        "total_stages": len(stages),
        "passed_stages": passed,
        "failed_stages": failed,
        "stages": stages,
    }


@app.get("/summary")
def summary():
    ingestion = read_json_report(
        INGESTION_REPORT,
        "Ingestion report",
    )
    pipeline = read_json_report(
        PIPELINE_LOG,
        "Pipeline execution log",
    )

    stages = pipeline.get("stages", [])

    return {
        "lab": "Lab 13",
        "ingestion_summary": {
            "status": ingestion.get("status"),
            "original_rows": ingestion.get("original_rows"),
            "input_rows": ingestion.get("input_rows"),
            "rows_added": ingestion.get("rows_added"),
            "total_rows": ingestion.get("total_rows"),
            "duplicate_ids": ingestion.get("duplicate_ids"),
            "schema_validation": ingestion.get("schema_validation"),
            "data_validation": ingestion.get("data_validation"),
            "production_model_changed": ingestion.get(
                "production_model_changed"
            ),
            "model_retraining_executed": ingestion.get(
                "model_retraining_executed"
            ),
            "model_promotion_executed": ingestion.get(
                "model_promotion_executed"
            ),
        },
        "pipeline_summary": {
            "overall_status": pipeline.get("overall_status"),
            "total_stages": len(stages),
            "passed_stages": sum(
                1 for stage in stages
                if str(stage.get("status", "")).upper() == "PASSED"
            ),
            "failed_stages": sum(
                1 for stage in stages
                if str(stage.get("status", "")).upper() == "FAILED"
            ),
        },
        "note": (
            "Ingestion and pipeline records are reported separately. "
            "Their timestamps are not assumed to represent one execution."
        ),
    }

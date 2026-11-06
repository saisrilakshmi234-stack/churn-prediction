# MLOps Churn Prediction - Architecture

## 1. Purpose

This project implements a Telco Customer Churn Prediction system using MLOps practices.

The project covers data validation, preprocessing, model training, MLflow tracking, model lifecycle management, drift monitoring, safe data ingestion, Docker, Kubernetes and GitHub Actions.

## 2. System Architecture

```text
GitHub Repository
       |
       v
GitHub Actions
       |
       v
Self-hosted Windows Runner
       |
       +--------------------------+
       |                          |
       v                          v
Runner Test Workflow       Monitoring Workflow
       |                          |
       v                          v
Python, Git, Docker        Project and Python
Kubernetes checks          Ingestion report check
                           Kubernetes checks
```

## 3. Main Project Components

| Component | Responsibility |
|---|---|
| Data validation | Checks incoming dataset structure and values |
| Data ingestion | Safely validates and adds new records |
| Data drift | Evaluates feature distribution changes |
| Prediction drift | Monitors prediction distribution changes |
| Concept drift | Compares model performance |
| Performance monitoring | Evaluates model metrics |
| API monitoring | Summarizes latency and throughput |
| Request history | Displays inference request information |
| MLflow | Tracks experiments and model versions |
| Docker | Packages the application |
| Kubernetes | Runs and manages application deployments |

## 4. Data Ingestion

The original dataset contained 7,044 records. A simulated batch of 100 records was validated and ingested.

- Original records: 7,044
- Incoming records: 100
- Records added: 100
- Final records: 7,144
- Duplicate customer IDs: 0
- Schema validation: Passed
- Production model changed: No
- Model retraining executed: No
- Model promotion executed: No

Ingestion report: `outputs/monitoring/ingestion_report.json`

Batch archive: `data/archive/`

Backups: `backups/`

The ingestion script uses dry-run mode by default. The `--commit` argument is required for actual ingestion.

## 5. MLflow Model Registry

Latest verified registry state after Lab 13 ingestion:

| Model Version | Registry Stage |
|---|---|
| Version 2 | Production |
| Version 7 | Staging |

Data ingestion did not change either model version.

Model retraining, registration and promotion are separate operations.

## 6. GitHub Actions Execution

The project uses a self-hosted Windows runner.

Runner labels:
- `self-hosted`
- `Windows`
- `X64`

Project directory:

`C:\Users\KALYANI\OneDrive\Desktop\churn_prediction`

Python environment:

`.venv\Scripts\python.exe`

Verified Python version: 3.13.3.

### Workflow 1: Lab 13 Monitoring

File: `.github/workflows/lab13_monitoring.yml`

Trigger: Manual execution using `workflow_dispatch`.

Checks:
1. Project directory.
2. Python virtual environment.
3. Ingestion report.
4. Kubernetes deployment and pods.

This workflow performs verification checks. It does not automatically retrain, register or promote models.

### Workflow 2: Self-hosted Runner Test

File: `.github/workflows/lab13_runner_test.yml`

Triggers:
- Push to the `main` branch.
- Manual execution.

Checks:
1. Project directory.
2. Python environment.
3. Git installation.
4. Docker availability.
5. Kubernetes node availability.
6. Runner and workspace information.

The runner is started interactively using `run.cmd`. Its terminal must remain open, and the computer must stay awake and connected to the internet while jobs execute.

## 7. Historical MLOps Experiments

Earlier experiments covered:
- Model training and evaluation.
- MLflow experiment tracking.
- Model registration and lifecycle management.
- Recall-based quality gates.
- Candidate-versus-Production comparisons.
- Docker image creation.
- Kubernetes deployment and rollout verification.
- Drift simulation and monitoring.

Historical reports may refer to earlier model versions and dataset counts. They do not represent the current registry state.

Synthetic drift datasets are demonstration data, not actual live customer data.

## 8. Runtime Dependencies

- Python
- Pandas and NumPy
- Scikit-learn
- Pandera
- MLflow
- Docker Desktop
- Kubernetes
- kubectl
- GitHub Actions
- Self-hosted Windows runner

## 9. Current Limitations

- The incoming 100-row dataset is simulated.
- The current monitoring workflow performs verification checks rather than automatic retraining.
- Drift experiments use generated datasets.
- The self-hosted runner requires the local computer to remain online.
- Production model promotion requires a separate, verified lifecycle process.
- Deployment scripts can modify Kubernetes resources and must be reviewed before execution.

## 10. Conclusion

The project demonstrates an MLOps workflow covering dataset validation, safe data ingestion, model tracking, monitoring, containerization, Kubernetes deployment and GitHub Actions integration.

Lab 13 successfully demonstrated safe ingestion of a new dataset batch while preserving the existing Production and Staging model versions.
# Runbook - Churn Prediction MLOps

## 1. Project Environment

Project directory:

`C:\Users\KALYANI\OneDrive\Desktop\churn_prediction`

Python virtual environment:

`.venv\Scripts\python.exe`

Verified Python version: 3.13.3.

Git branch: `main`

## 2. Before Running

1. Open PowerShell in the project directory.
2. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Confirm Python:

   ```powershell
   python --version
   ```

4. Start Docker Desktop when Docker or Kubernetes operations are required.
5. Verify Docker:

   ```powershell
   docker info
   ```

6. Verify Kubernetes:

   ```powershell
   kubectl get nodes
   kubectl get deployment churn-api
   kubectl get pods
   ```

Do not execute model retraining, registry updates or production deployment scripts without reviewing their effects first.

## 3. Self-hosted GitHub Actions Runner

Runner directory:

`C:\actions-runner`

Runner name:

`DESKTOP-HM5AKSG`

Runner labels:

- `self-hosted`
- `Windows`
- `X64`

Start the runner in a separate PowerShell window:

```powershell
cd C:\actions-runner
.\run.cmd
```

Keep this terminal open while GitHub Actions jobs are running.

The computer must remain awake, connected to the internet and available for the runner to receive jobs.

Check runner status in GitHub:

**Repository → Settings → Actions → Runners**

## 4. GitHub Actions Workflows

### Lab 13 Monitoring Workflow

File:

`.github/workflows/lab13_monitoring.yml`

Trigger: Manual execution using `workflow_dispatch`.

To run:

1. Open the repository on GitHub.
2. Select **Actions**.
3. Select **Lab 13 - End-to-End MLOps**.
4. Choose **Run workflow** on branch `main`.
5. Open the workflow run and inspect its steps.

The workflow verifies:

- Project directory.
- Python virtual environment.
- Ingestion report.
- Kubernetes deployment and pods.

It does not automatically execute drift analysis, retraining, model registration, promotion or deployment.

### Self-hosted Runner Test Workflow

File:

`.github/workflows/lab13_runner_test.yml`

Triggers:

- Push to `main`.
- Manual execution.

It checks Python, Git, Docker, Kubernetes and runner information.

## 5. Data Ingestion

Incoming dataset:

`data/raw/new_churn.csv`

Main dataset:

`data/raw/churn.csv`

Ingestion script:

`src/mlops_pipeline/12_ingest_new_data.py`

### Dry-run validation

Run:

```powershell
python .\src\mlops_pipeline\12_ingest_new_data.py
```

The default execution validates the batch without committing it.

### Actual ingestion

Only after reviewing the dry-run report and explicitly deciding to ingest:

```powershell
python .\src\mlops_pipeline\12_ingest_new_data.py --commit
```

The `--commit` option modifies the main dataset.

### Latest verified ingestion

- Original records: 7,044
- Incoming records: 100
- Records added: 100
- Final records: 7,144
- Duplicate customer IDs: 0
- Schema and data validation: Passed

Report:

`outputs/monitoring/ingestion_report.json`

Batch archive:

`data/archive/`

Backups:

`backups/`

The incoming dataset is preserved after ingestion.

Do not rerun the commit operation for the same batch without first checking its status and the current dataset.

## 6. MLflow Model Registry

Latest verified registry state after Lab 13 ingestion:

| Model Version | Stage |
|---|---|
| Version 2 | Production |
| Version 7 | Staging |

Data ingestion did not change these versions.

To inspect the registry, use the read-only utility:

```powershell
python .\src\mlops_pipeline\check_mlflow_registry.py
```

Do not run registry update or promotion scripts unless their quality gates, model versions and effects have been reviewed.

## 7. Important Reports and Directories

| Location | Purpose |
|---|---|
| `outputs/monitoring/ingestion_report.json` | Latest ingestion result |
| `data/archive/` | Archived incoming batches |
| `backups/` | Dataset backups |
| `outputs/drift/` | Drift experiment reports |
| `artifacts/` | Generated pipeline artifacts |
| `logs/` | Application and inference logs |
| `deployment/` | Deployment files and model metadata |
| `k8s/` | Kubernetes manifests |

Generated reports and customer datasets should not be committed to a public repository unless they have been reviewed and sanitized.

## 8. Troubleshooting

### Workflow stays queued

- Confirm the self-hosted runner is online.
- Keep the `run.cmd` terminal open.
- Check that workflow labels match `self-hosted`, `Windows` and `X64`.
- Ensure the computer is awake and connected to the internet.

### Kubernetes commands fail

1. Start Docker Desktop.
2. Wait for Kubernetes to become ready.
3. Run:

   ```powershell
   kubectl get nodes
   ```

4. Check the deployment:

   ```powershell
   kubectl get deployment churn-api
   ```

A Kubernetes check can fail because the cluster is unavailable, not necessarily because the application code is incorrect.

### Ingestion report is missing

Check whether the ingestion script has been executed and whether this file exists:

`outputs/monitoring/ingestion_report.json`

Do not assume the monitoring workflow performs ingestion automatically.

### Model version or stage differs

Inspect the MLflow Model Registry before performing any model lifecycle operation.

Do not promote a candidate based only on a successful training run.

### Docker access fails

Check Docker Desktop status and run `docker info` directly from PowerShell.

Do not change Docker permissions without understanding the cause of the access error.

## 9. Production Safety

- Review scripts before running them.
- Keep production model artifacts and registry state protected.
- Do not overwrite the Production model without a verified promotion decision.
- Review Kubernetes deployment changes before applying them.
- Keep backups before modifying important datasets.
- Never commit passwords, access tokens, customer data or private model artifacts.

## 10. Operational Summary

This runbook describes the verified project environment, self-hosted runner, GitHub Actions checks, safe dataset ingestion, MLflow registry inspection and operational troubleshooting.

The current Lab 13 workflow performs environment and deployment verification. Automatic retraining and production promotion are separate operations and are not performed by this workflow.
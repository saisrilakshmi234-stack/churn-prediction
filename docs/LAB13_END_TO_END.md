# Lab 13 — End-to-End MLOps Integration Report

## 1. Objective

This lab documents the integration of data ingestion and validation, model monitoring, MLflow model registry management, deployment infrastructure, and GitHub Actions verification for the Telco Customer Churn Prediction MLOps project.

The report distinguishes verified current execution from historical experiments and synthetic demonstrations.

## 2. Current Project Architecture

The project contains the following components:

1. Data loading and validation.
2. Data preprocessing and model training.
3. MLflow experiment tracking and model registry.
4. Model evaluation and quality checks.
5. Data drift, prediction drift, and concept drift analysis.
6. API inference and performance monitoring.
7. Safe incoming dataset ingestion.
8. Docker containerization and Kubernetes deployment.
9. GitHub Actions workflows using a self-hosted Windows runner.

Not every component is executed automatically by the current GitHub Actions workflows.

## 3. Incoming Dataset Ingestion

The incoming dataset was processed using:

`src/mlops_pipeline/12_ingest_new_data.py`

The script supports two execution modes:

- Dry-run mode: validates the incoming batch without changing the main dataset.
- Commit mode: performs ingestion after explicit use of the `--commit` argument.

### Verified ingestion result

| Item | Result |
|---|---:|
| Original dataset rows | 7,044 |
| Incoming batch rows | 100 |
| Rows added | 100 |
| Final dataset rows | 7,144 |
| Duplicate incoming customer IDs | 0 |
| Incoming customer ID range | NEW000201–NEW000300 |

The ingestion completed successfully.

### Data protection and lineage

The ingestion process created:

- A backup of the previous dataset under `backups/`.
- An archived copy of the incoming batch under `data/archive/`.
- An ingestion report at `outputs/monitoring/ingestion_report.json`.

The original incoming file `data/raw/new_churn.csv` was preserved.

The report confirmed successful schema, data, backup, and archive validation.

The ingestion did not retrain a model, change the MLflow registry, promote a model, or deploy a new model.

## 4. MLflow Model Registry Status

The current verified registry state is:

| Model version | Stage |
|---|---|
| Version 2 | Production |
| Version 7 | Staging |

Production version 2 remains unchanged following the ingestion operation.

Version 7 remains in Staging. No promotion to Production was performed as part of the verified Lab 13 ingestion.

Registry verification was performed without changing model stages.

## 5. GitHub Actions Workflows

The project contains two Lab 13 workflows.

### 5.1 Lab 13 — End-to-End MLOps

File:

`.github/workflows/lab13_monitoring.yml`

Trigger:

- Manual execution using `workflow_dispatch`.

Checks performed:

1. Verify the project directory.
2. Verify the Python virtual environment.
3. Check the ingestion report.
4. Check Kubernetes deployment and pod availability.

This workflow is a verification workflow. It does not automatically execute drift analysis, dataset ingestion, model training, MLflow registration, model promotion, or production deployment.

### 5.2 Lab 13 — Self-hosted Runner Test

File:

`.github/workflows/lab13_runner_test.yml`

Triggers:

- Push to the `main` branch.
- Manual execution using `workflow_dispatch`.

Checks performed:

- Project directory.
- Python environment.
- Git.
- Docker.
- Kubernetes.
- Runner and workspace information.

### 5.3 Runner configuration

The self-hosted runner was configured with:

- Runner name: `DESKTOP-HM5AKSG`
- Operating system: Windows
- Architecture: X64
- Labels: `self-hosted`, `Windows`, `X64`

The runner was started interactively using `C:\actions-runner\run.cmd`.

The runner terminal must remain open, and the computer must remain awake and connected for jobs to execute.

## 6. Docker and Kubernetes Verification

The local environment checks confirmed:

- Docker Desktop was accessible.
- `kubectl` was available.
- The Kubernetes node reported Ready.
- The `churn-api` Deployment showed 3/3 replicas ready during verification.

These checks establish that the local container and Kubernetes environment was available at the time of testing.

They do not establish that the current Lab 13 workflow automatically performs a production deployment.

## 7. Historical MLOps Experiments

Earlier project experiments included:

- Synthetic data drift generation.
- Prediction drift analysis.
- Concept drift simulation.
- Candidate model training and evaluation.
- MLflow model lifecycle experiments.
- Deployment and Kubernetes rollout testing.

Some older reports refer to different dataset sizes, model versions, archive locations, and workflow configurations.

Those results are historical experiment records. They must not be interpreted as the current dataset state, current MLflow registry state, or current GitHub Actions behavior.

Synthetic drift datasets are demonstration data and are not evidence of real-world customer behavior.

## 8. Important Current Paths

| File or directory | Purpose |
|---|---|
| `data/raw/churn.csv` | Main local dataset |
| `data/raw/new_churn.csv` | Incoming dataset |
| `data/archive/` | Archived incoming batches |
| `backups/` | Dataset backups |
| `outputs/monitoring/ingestion_report.json` | Ingestion result |
| `outputs/drift/` | Drift analysis outputs |
| `logs/inference/` | API inference logs |
| `deployment/model_metadata.json` | Packaged model metadata |
| `k8s/` | Kubernetes configuration |
| `.github/workflows/` | GitHub Actions workflow definitions |

Generated datasets, customer data, local logs, model binaries, and runtime reports should not be committed to the public repository.

## 9. Limitations and Safety Considerations

1. The 100-row incoming batch was a simulated dataset, not a live external customer-data feed.
2. Drift experiments use generated or prepared datasets and should be interpreted as demonstrations.
3. The current Lab 13 monitoring workflow verifies existing artifacts and infrastructure; it is not an automated retraining pipeline.
4. The self-hosted runner depends on the local computer being online and available.
5. Production model promotion and deployment require separate review and explicit execution.
6. Scripts that register models, change registry stages, or update Kubernetes deployments must be reviewed before execution.
7. Historical experiment results should not be presented as current production metrics.

## 10. Conclusion

Lab 13 established a verified incoming-data ingestion process, preserved dataset backups and batch archives, confirmed the current MLflow registry state, and checked the local Docker and Kubernetes environment.

The GitHub Actions workflows provide manual MLOps environment verification and self-hosted runner diagnostics.

The project includes additional monitoring, retraining, registry, and deployment components, but these are separate operations and are not automatically executed by the current Lab 13 monitoring workflow.

This report records the verified project state without claiming unverified automated retraining, model promotion, or deployment.
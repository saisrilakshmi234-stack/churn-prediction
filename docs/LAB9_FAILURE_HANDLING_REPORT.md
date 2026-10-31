# Lab 9 - Pipeline Failure Handling and Recovery

## Goal

Intentionally introduce failures into the MLOps pipeline and verify that validation halts unsafe processing or that the system recovers the Production model through MLflow Model Registry.

## Run locally

```bash
python src/mlops_pipeline/10_failure_injection.py
```

## Failure scenarios

| Scenario | Expected behavior | Result |
|---|---|---|
| Missing raw dataset | HALT | PASSED |
| Invalid datatype | HALT | PASSED |
| Schema mismatch | HALT | PASSED |
| Corrupted processed output | HALT | PASSED |
| Missing local model artifact | Detect failure, recover Production model from MLflow, and rerun evaluation | PASSED |

## Repeated execution

The `lab9.repetitions` setting in `config.yaml` is configured to `3`.

The failure-injection script completed three repetitions of all five scenarios.

- Total scenario executions: 15
- Successful scenario executions: 15
- Failed scenario executions: 0
- Overall status: PASSED

## Recovery behavior

During the missing-model scenario, the pipeline detected that `models/churn_model.pkl` was missing. The Production model was loaded from MLflow, the local model artifact was restored, and evaluation ran successfully.

Evaluation metrics after recovery:

| Metric | Result |
|---|---:|
| Accuracy | 0.7615 |
| Precision | 0.5374 |
| Recall | 0.7299 |
| F1 score | 0.6190 |
| ROC-AUC | 0.8406 |

## Evidence

The generated report is saved at:

`reports/failure_report.json`

The report records the results of all three repetitions and confirms:

`"overall_status": "PASSED"`

## Safety verification

After the failure tests completed, these checks returned `True`:

- `data/raw/churn.csv` exists.
- `models/churn_model.pkl` exists.

The failure-injection script uses cleanup logic to restore temporarily modified files. The existence checks confirm that the original dataset and local model are present after the run.

## Conclusion

Lab 9 completed successfully in the local environment. All five failure-handling scenarios passed in each of three repetitions, including recovery of the Production model from MLflow.

The GitHub Actions workflow is configured to run the normal pipeline before the failure-injection tests. A successful local run does not, by itself, confirm that the GitHub Actions workflow has passed.

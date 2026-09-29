# Customer Churn Prediction - MLOps Project

This project implements an end-to-end Machine Learning Operations (MLOps) workflow for customer churn prediction.

The project covers data preprocessing, model training, evaluation, experiment tracking, validation, reproducibility, model registry, and lifecycle automation.

---

## Project Objectives

- Build a customer churn prediction model
- Perform data preprocessing and feature engineering
- Train and evaluate machine learning models
- Track experiments using MLflow
- Validate data and model outputs
- Ensure reproducibility
- Register and manage trained models
- Automate model lifecycle activities
- Organize the complete workflow using pipeline scripts

---

## Project Structure

```text
churn_prediction/
│
├── data/
│   ├── raw/
│   │   └── churn.csv
│   │
│   └── processed/
│       ├── dataset_metadata.json
│       ├── X_test_final.npy
│       ├── X_train_final.npy
│       ├── y_test.npy
│       └── y_train.npy
│
├── notebooks/
│   └── project_implementation.ipynb
│
├── src/
│   ├── preprocess.py
│   ├── train.py
│   ├── evaluate.py
│   ├── train_mlflow.py
│   ├── preprocess_pipeline.py
│   ├── validate_data.py
│   ├── validate_reproducibility.py
│   ├── validate_outputs.py
│   ├── train_registry.py
│   ├── automate_lifecycle.py
│   └── generate_registry_report.py
│
├── pipelines/
│   ├── run_lab3_baseline.py
│   ├── run_lab4_tracking.py
│   ├── run_lab5_pipeline.py
│   └── run_lab6_registry.py
│
├── models/
├── outputs/
├── logs/
├── artifacts/
│
├── requirements.txt
└── .gitignore
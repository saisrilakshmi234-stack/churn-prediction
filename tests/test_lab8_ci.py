from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_config_has_required_pipeline_settings():
    config_path = ROOT / "config.yaml"
    assert config_path.exists()

    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    assert config["data"]["raw_path"] == "data/raw/churn.csv"
    assert config["data"]["target_column"] == "Churn"
    assert config["registry"]["model_name"]
    assert config["quality_gate"]["metric"] == "recall"
    assert 0 <= config["quality_gate"]["minimum_value"] <= 1


def test_churn_dataset_has_required_columns():
    data_path = ROOT / "data" / "raw" / "churn.csv"
    assert data_path.exists()

    df = pd.read_csv(data_path)

    assert len(df) > 0
    assert "customerID" in df.columns
    assert "Churn" in df.columns
    assert set(df["Churn"].dropna().unique()).issubset({"Yes", "No"})


def test_churn_dataset_has_no_missing_target_values():
    df = pd.read_csv(ROOT / "data" / "raw" / "churn.csv")

    assert df["Churn"].notna().all()

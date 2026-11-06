import numpy as np
import pytest

from api.main import model_loader


class DummyPreprocessor:
    def transform(self, data):
        return np.zeros((len(data), 1))


class DummyModel:
    def predict(self, data):
        return np.zeros(len(data), dtype=int)

    def predict_proba(self, data):
        return np.tile([0.75, 0.25], (len(data), 1))


@pytest.fixture(autouse=True)
def mock_model_loader(monkeypatch):
    def fake_load():
        model_loader.model = DummyModel()
        model_loader.preprocessor = DummyPreprocessor()
        model_loader.model_name = "CI_Test_Model"
        model_loader.model_version = "test"
        model_loader.run_id = "ci-test-run"
        model_loader.model_uri = "test://ci-model"

    monkeypatch.setattr(model_loader, "load", fake_load)

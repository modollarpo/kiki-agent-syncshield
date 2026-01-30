import torch
import pytest
from services.syncvalue.internal.usecases import ltv_inference

def test_predict_ltv_mock(monkeypatch):
    monkeypatch.setattr(ltv_inference, "predict_ltv", lambda features: 42.0)
    features = {"f1": 1.0, "f2": 2.0}
    result = ltv_inference.predict_ltv(features)
    assert result == 42.0

def test_predict_ltv_real():
    features = {"f1": 1.0, "f2": 2.0}
    result = ltv_inference.predict_ltv(features)
    assert isinstance(result, float)

# tests/test_predict_ltv.py
import pytest
from app.entities.drnn import DRNN
from app.usecases.predict_ltv import predict_ltv

class DummyModel(DRNN):
    def forward(self, x):
        return x.sum(dim=2)

def test_predict_ltv():
    model = DummyModel(10, 20, 1)
    features = [1.0] * 10
    result = predict_ltv(model, features)
    assert isinstance(result, float)

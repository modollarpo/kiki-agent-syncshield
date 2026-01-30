"""
Unit tests for Acquisition Agent budget optimisation
- All external calls are mocked
"""
import pytest
from domain.optimisation import optimise_budget

def test_ltv_based_optimisation():
    campaigns = ["A", "B", "C"]
    budget = 300.0
    constraints = {}
    pacing = {}
    ltv_predictions = {"A": 120.0, "B": 100.0, "C": 80.0}
    allocation, events = optimise_budget(campaigns, budget, constraints, pacing, ltv_predictions)
    assert sum(allocation.values()) == pytest.approx(budget)
    assert all(isinstance(e, str) for e in events)
    assert allocation["A"] > allocation["B"] > allocation["C"]

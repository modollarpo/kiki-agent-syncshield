"""
Domain logic for budget optimisation and scenario simulation
- Pluggable strategy pattern for optimisation
- Strong typing and docstrings
"""
from typing import List, Dict, Tuple

class SimulationRequest:
    def __init__(self, campaigns: List[str], budget: float, constraints: Dict, pacing: Dict, ltv_predictions: Dict):
        self.campaigns = campaigns
        self.budget = budget
        self.constraints = constraints
        self.pacing = pacing
        self.ltv_predictions = ltv_predictions

class SimulationResult:
    def __init__(self, allocation: Dict, predicted_ltv: Dict, events: List[str]):
        self.allocation = allocation
        self.predicted_ltv = predicted_ltv
        self.events = events

    @staticmethod
    def simulate(request: 'SimulationRequest') -> 'SimulationResult':
        # What-if analysis logic (abstracted)
        allocation = {c: request.budget / len(request.campaigns) for c in request.campaigns}
        events = [f"Simulated allocation for {c}" for c in request.campaigns]
        return SimulationResult(allocation, request.ltv_predictions, events)

# Strategy pattern for budget optimisation
class BudgetOptimisationStrategy:
    def optimise(self, campaigns: List[str], budget: float, constraints: Dict, pacing: Dict, ltv_predictions: Dict) -> Tuple[Dict, List[str]]:
        raise NotImplementedError

class LTVBasedOptimisation(BudgetOptimisationStrategy):
    def optimise(self, campaigns, budget, constraints, pacing, ltv_predictions):
        # Replace ROAS logic with predicted LTV
        total_ltv = sum(ltv_predictions.values())
        allocation = {}
        for c in campaigns:
            allocation[c] = budget * (ltv_predictions[c] / total_ltv) if total_ltv > 0 else budget / len(campaigns)
        events = [f"Allocated {allocation[c]:.2f} to {c} based on LTV {ltv_predictions[c]:.2f}" for c in campaigns]
        return allocation, events

# Entry point for optimisation

def optimise_budget(campaigns: List[str], budget: float, constraints: Dict, pacing: Dict, ltv_predictions: Dict) -> Tuple[Dict, List[str]]:
    # Pluggable strategy (can be extended)
    strategy = LTVBasedOptimisation()
    return strategy.optimise(campaigns, budget, constraints, pacing, ltv_predictions)

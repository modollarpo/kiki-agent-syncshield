from abc import ABC, abstractmethod

class LtvService(ABC):
    @abstractmethod
    def predict_ltv(self, user_id: str, features: dict) -> float:
        pass

from abc import ABC, abstractmethod

class CRMTrigger(ABC):
    @abstractmethod
    def trigger(self, event: str, user_id: str, data: dict) -> dict:
        pass

from abc import ABC, abstractmethod

class CreativeGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str, variant: str, user_id: str, creative_type: str) -> dict:
        pass

from pydantic import BaseModel
from typing import Dict, Any

class LTVPredictionRequest(BaseModel):
    user_id: str
    features: Dict[str, Any]

class LTVPredictionResponse(BaseModel):
    ltv: float
    user_id: str

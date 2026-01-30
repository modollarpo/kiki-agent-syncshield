from pydantic import BaseModel

class BidRequest(BaseModel):
    user_id: str
    ad_slot: str
    bid_amount: float

class BidResponse(BaseModel):
    bid_id: str
    accepted: bool
    reason: str = None

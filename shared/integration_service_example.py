import requests
from schemas.bid import BidRequest, BidResponse
from schemas.ltv_prediction import LTVPredictionRequest, LTVPredictionResponse

# Example: Service-to-service call (Python)
def call_syncflow_bid():
    req = BidRequest(user_id="u1", ad_slot="banner_top", bid_amount=1.23)
    resp = requests.post("http://syncflow:8000/execute-bid", json=req.dict())
    if resp.status_code == 200:
        bid_resp = BidResponse(**resp.json())
        print("BidResponse:", bid_resp)
    else:
        print("Bid failed:", resp.text)

def call_syncvalue_ltv():
    req = LTVPredictionRequest(user_id="u1", features={"f1": 1.0})
    resp = requests.post("http://syncvalue:8000/predict-ltv", json=req.dict())
    if resp.status_code == 200:
        ltv_resp = LTVPredictionResponse(**resp.json())
        print("LTVPredictionResponse:", ltv_resp)
    else:
        print("LTV failed:", resp.text)

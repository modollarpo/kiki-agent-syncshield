from schemas.ltv_prediction import LTVPredictionRequest, LTVPredictionResponse
from schemas.creative import Creative
from shared.audit_event import AuditEvent

# Example: Validate and use LTVPredictionRequest
req = LTVPredictionRequest(user_id="u1", features={"f1": 1.0, "f2": 2.0})
print("LTVPredictionRequest valid:", req)

# Example: Create and use Creative
creative = Creative(creative_id="c1", prompt="banner", variant="default", user_id="u1", image_url=None, brand_safety="safe", ratings=[5,4,5])
print("Creative:", creative)

# Example: AuditEvent for creative generation
event = AuditEvent(event="creative_generated", user_id="u1", data={"creative_id": creative.creative_id})
print("AuditEvent:", event.__dict__)

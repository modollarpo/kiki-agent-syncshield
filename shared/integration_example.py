from shared.audit_event import AuditEvent
from schemas.user import User
from utils.validation import validate_model

def example_usage():
    user_data = {"id": "u1", "email": "test@example.com", "name": "Test User"}
    user, errors = validate_model(User, user_data)
    if errors:
        print("Validation failed:", errors)
    else:
        print("User valid:", user)
    event = AuditEvent(event="login", user_id=user.id, data={"ip": "127.0.0.1"})
    print("Audit event:", event.__dict__)

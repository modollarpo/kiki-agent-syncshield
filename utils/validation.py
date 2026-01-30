from pydantic import ValidationError

def validate_model(model_class, data):
    try:
        return model_class(**data), None
    except ValidationError as e:
        return None, e.errors()

# Inference API (FastAPI stub)
from fastapi import FastAPI
from app.adapters.model_loader import load_model
from app.usecases.predict_ltv import predict_ltv

app = FastAPI()
model = load_model("model.pth")

@app.post("/predict_ltv")
def predict(features: list[float]):
    ltv = predict_ltv(model, features)
    return {"ltv": ltv}

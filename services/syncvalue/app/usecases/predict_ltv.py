# Usecase: LTV Prediction
from app.entities.drnn import DRNN
import torch

def predict_ltv(model: DRNN, features):
    model.eval()
    with torch.no_grad():
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        return model(x).item()

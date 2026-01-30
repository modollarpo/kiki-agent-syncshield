"""
Inference for LTV dRNN model.
"""
import torch
from ltv_dRNN import LTVdRNN

def predict(model, features):
    model.eval()
    with torch.no_grad():
        return model(features)

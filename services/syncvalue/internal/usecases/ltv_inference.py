# Clean Architecture UseCase: LTV Inference (dRNN placeholder)
import torch
import torch.nn as nn
from typing import Dict

class dRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    def forward(self, x):
        out, _ = self.rnn(x)
        out = self.fc(out[:, -1, :])
        return out

def load_model():
    # In real use, load weights from disk
    return dRNN(input_size=2, hidden_size=8, output_size=1)

_model = load_model()

def predict_ltv(features: Dict[str, float]) -> float:
    # Preprocess features to tensor
    x = torch.tensor([[features.get('f1', 0.0), features.get('f2', 0.0)]], dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        out = _model(x)
    return float(out.item())

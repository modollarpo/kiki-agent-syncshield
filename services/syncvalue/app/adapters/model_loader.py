# Adapter: Model Loader
from app.entities.drnn import DRNN
import torch

def load_model(path: str) -> DRNN:
    model = DRNN(input_size=10, hidden_size=20, output_size=1)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model

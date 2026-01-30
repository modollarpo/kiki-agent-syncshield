import torch
import torch.nn as nn

class LTV_dRNN(nn.Module):
    def __init__(self, input_dim=10, hidden_dim=64, output_dim=1):
        super(LTV_dRNN, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        # x shape: (batch, seq_len, features)
        _, (hn, _) = self.lstm(x)
        return self.fc(hn[-1]) # Predict margin recovery

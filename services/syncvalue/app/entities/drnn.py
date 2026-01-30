# PyTorch dRNN structure (entities)
import torch
import torch.nn as nn

class DRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DRNN, self).__init__()
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.rnn(x)
        out = self.fc(out[:, -1, :])
        return out

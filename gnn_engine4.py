import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import numpy as np

class StockGNN(nn.Module):
    def __init__(self, num_features):
        super(StockGNN, self).__init__()
        self.conv1 = GCNConv(num_features, 32)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = GCNConv(32, 16)
        self.out = nn.Linear(16, 1)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        return self.out(x)
def get_gnn_predictions(corr_matrix, features_matrix):
   
    adj = (np.abs(corr_matrix) > 0.7).astype(int)
    np.fill_diagonal(adj, 0)
    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    
    x = torch.tensor(features_matrix, dtype=torch.float)
    y = x[:, 0].view(-1, 1) 

    
    target_mean = y.mean()
    target_std = y.std() + 1e-6
    y_norm = (y - target_mean) / target_std

    model = StockGNN(num_features=x.shape[1])
   
    optimizer = optim.Adam(model.parameters(), lr=0.001) 
    criterion = nn.MSELoss()

    model.train()
    for _ in range(100): 
        optimizer.zero_grad()
        out = model(x, edge_index)
        loss = criterion(out, y_norm) 
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        
        preds_norm = model(x, edge_index)
        preds = (preds_norm * target_std) + target_mean
    
    return preds.numpy().flatten()
def get_gnn_predictions2(corr_matrix, features_matrix):
    """
    Принимает матрицы, обучает GNN и возвращает предсказания.
    """
   
    adj = (np.abs(corr_matrix) > 0.5).astype(int)
    np.fill_diagonal(adj, 0)
    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    
    
    x = torch.tensor(features_matrix, dtype=torch.float)
    
    
    y = x[:, 0].view(-1, 1)

   
    x_norm = (x - x.mean(dim=0)) / (x.std(dim=0) + 1e-6)

   
    model = StockGNN(num_features=x.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    model.train()
    for _ in range(50):
        optimizer.zero_grad()
        out = model(x_norm, edge_index)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()

  
    model.eval()
    with torch.no_grad():
        preds = model(x_norm, edge_index).numpy().flatten()
    
    return preds
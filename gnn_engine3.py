import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GATConv 
import numpy as np

class StockGAT(nn.Module):
    def __init__(self, num_features):
        super(StockGAT, self).__init__()
        
        self.gat1 = GATConv(num_features, 16, heads=8, dropout=0.2)
        self.bn1 = nn.BatchNorm1d(16 * 8)
        
      
        self.gat2 = GATConv(16 * 8, 1, heads=1, concat=False, dropout=0.2)
        
    def forward(self, x, edge_index):
       
        x = self.gat1(x, edge_index)
        x = self.bn1(x)
        x = F.elu(x) 
        
      
        x = self.gat2(x, edge_index)
        return x

def get_gnn_predictions(corr_matrix, features_matrix):
    
    adj = (np.abs(corr_matrix) > 0.6).astype(int)
    np.fill_diagonal(adj, 0)
    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    
    x = torch.tensor(features_matrix, dtype=torch.float)
    y = x[:, 0].view(-1, 1) 

    
    target_mean = y.mean()
    target_std = y.std() + 1e-6
    y_norm = (y - target_mean) / target_std

    
    model = StockGAT(num_features=x.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    criterion = nn.MSELoss()

    model.train()
    for _ in range(150): 
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























































































import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from torch_geometric.nn import GATv2Conv


class StockGATv2(nn.Module):
    def __init__(self, num_features, hidden_dim=32, heads=4, dropout=0.2):
        super(StockGATv2, self).__init__()
       
        self.conv1 = GATv2Conv(num_features, hidden_dim, heads=heads, concat=True, dropout=dropout)
        self.conv2 = GATv2Conv(hidden_dim * heads, hidden_dim, heads=1, concat=False, dropout=dropout)
        
       
        self.ln1 = nn.LayerNorm(hidden_dim * heads)
        self.ln2 = nn.LayerNorm(hidden_dim)
        
      
        self.shortcut = nn.Linear(num_features, hidden_dim * heads)
        
        self.out = nn.Linear(hidden_dim, 1)

    def forward(self, x, edge_index, edge_attr=None):
       
        res = self.shortcut(x)
        h = self.conv1(x, edge_index, edge_attr=edge_attr)
        h = F.elu(self.ln1(h + res))
        
       
        h = self.conv2(h, edge_index, edge_attr=edge_attr)
        h = F.elu(self.ln2(h))
        
        return self.out(h)


def get_gnn_predictions_pro(corr_matrix, features_matrix, formula="abs(corr) > 0.5"):
    
    corr = np.array(corr_matrix)
    n = len(corr)
    
   
    allowed_names = {"abs": np.abs, "corr": corr, "np": np}
    try:
        adj_mask = eval(formula, {"__builtins__": None}, allowed_names)
        adj = adj_mask.astype(int)
    except Exception as e:
        print(f"Formula Error: {e}. Fallback to k-NN.")
        adj = np.zeros_like(corr)

    
    k = min(3, n - 1)
    for i in range(n):
        top_k_idx = np.argpartition(np.abs(corr[i]), -k)[-k:]
        adj[i, top_k_idx] = 1
    
    np.fill_diagonal(adj, 0)
    
    
    rows, cols = np.nonzero(adj)
    edge_index = torch.tensor(np.array([rows, cols]), dtype=torch.long)
    edge_attr = torch.tensor(corr[rows, cols], dtype=torch.float)

    
    x = torch.tensor(features_matrix, dtype=torch.float)
    y = x[:, 0].view(-1, 1) 
    
   
    x_mean, x_std = x.mean(dim=0), x.std(dim=0) + 1e-6
    x_norm = (x - x_mean) / x_std
    y_mean, y_std = y.mean(), y.std() + 1e-6
    y_norm = (y - y_mean) / y_std

    
    model = StockGATv2(num_features=x.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-3)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.5)
    criterion = nn.HuberLoss(delta=1.0)

    model.train()
    for epoch in range(100):
        optimizer.zero_grad()
        out = model(x_norm, edge_index, edge_attr=edge_attr)
        loss = criterion(out, y_norm)
        loss.backward()
        optimizer.step()
        scheduler.step(loss)

   
    model.eval()
    with torch.no_grad():
        preds_norm = model(x_norm, edge_index, edge_attr=edge_attr)
        preds = (preds_norm * y_std) + y_mean
    
    return preds.numpy().flatten()
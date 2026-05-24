import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import numpy as np
import numpy as np
import torch
import torch.nn as nn
from torch_geometric.nn import GATConv, global_mean_pool
import torch.nn as nn
import torch.nn.functional as F

class StockGAT4(nn.Module):
    def __init__(self, num_features):
        super(StockGAT, self).__init__()
        
        self.conv1 = GATConv(num_features, 32, heads=2, concat=True)
        self.conv2 = GATConv(64, 16, heads=1, concat=False)
        self.ln1 = nn.LayerNorm(64) 
        self.out = nn.Linear(16, 1)

    def forward4(self, x, edge_index):
        
        h = self.conv1(x, edge_index)
        h = self.ln1(h)
        h = F.elu(h) 
        
        
        h = self.conv2(h, edge_index)
        h = F.elu(h)
        
        return self.out(h)

def get_gnn_predictions4(corr_matrix, features_matrix):
    
    
    
    corr = corr_matrix
    
    
    allowed_names = {"abs": np.abs, "corr": corr, "np": np}
    
    try:
        
        adj = eval(formula, {"__builtins__": None}, allowed_names)
        adj = adj.astype(int)
    except Exception as e:
       
        adj = (np.abs(corr_matrix) > 0.5).astype(int)

    np.fill_diagonal(adj, 0)
    
    
    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    
    adj = np.zeros_like(corr_matrix)
    k = min(3, len(corr_matrix) - 1)
    for i in range(len(corr_matrix)):
        idx = np.argpartition(np.abs(corr_matrix[i]), -k)[-k:]
        adj[i, idx] = 1
    
    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    

    x = torch.tensor(features_matrix, dtype=torch.float)
    y = x[:, 0].view(-1, 1) 
    
   
    x_mean, x_std = x.mean(dim=0), x.std(dim=0) + 1e-6
    x_norm = (x - x_mean) / x_std
    
   
    y_mean, y_std = y.mean(), y.std() + 1e-6
    y_norm = (y - y_mean) / y_std

    model = StockGAT(num_features=x.shape[1])
    
    optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    criterion = nn.HuberLoss() 

    model.train()
    for _ in range(80):
        optimizer.zero_grad()
        out = model(x_norm, edge_index)
        loss = criterion(out, y_norm)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        preds_norm = model(x_norm, edge_index)
   
        preds = (preds_norm * y_std) + y_mean
    
    return preds.numpy().flatten()





import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GATConv


class StockGAT(nn.Module):
    def __init__(self, num_features):
        super(StockGAT, self).__init__()
        self.conv1 = GATConv(num_features, 32, heads=2, concat=True)
        self.conv2 = GATConv(64, 16, heads=1, concat=False)
        self.ln1 = nn.LayerNorm(64)
        self.out = nn.Linear(16, 1)

    def forward(self, x, edge_index):
        h = self.conv1(x, edge_index)
        h = self.ln1(h)
        h = F.elu(h)
        h = self.conv2(h, edge_index)
        h = F.elu(h)
        return self.out(h)


def get_gnn_predictions(corr_matrix, features_matrix, formula="abs(corr) > 0.5"):
   
    corr = corr_matrix
    allowed_names = {"abs": np.abs, "corr": corr, "np": np}
    
    try:
        
        adj = eval(formula, {"__builtins__": None}, allowed_names)
        if isinstance(adj, (bool, int, float)): 
            adj = (np.abs(corr_matrix) > 0.5)
        adj = adj.astype(int)
    except Exception as e:
        print(f"Formula error, fallback to 0.5: {e}")
        adj = (np.abs(corr_matrix) > 0.5).astype(int)

    np.fill_diagonal(adj, 0)
    
   
    if np.sum(adj) == 0:
        k = min(2, len(corr_matrix) - 1)
        for i in range(len(corr_matrix)):
            idx = np.argpartition(np.abs(corr_matrix[i]), -k)[-k:]
            adj[i, idx] = 1

    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    
  
    x = torch.tensor(features_matrix, dtype=torch.float)
    y = x[:, 0].view(-1, 1)
    
  
    x_mean, x_std = x.mean(dim=0), x.std(dim=0) + 1e-6
    x_norm = (x - x_mean) / x_std
    y_mean, y_std = y.mean(), y.std() + 1e-6
    y_norm = (y - y_mean) / y_std

   
    model = StockGAT(num_features=x.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    criterion = nn.HuberLoss()

    model.train()
    for _ in range(80):
        optimizer.zero_grad()
        out = model(x_norm, edge_index)
        loss = criterion(out, y_norm)
        loss.backward()
        optimizer.step()

  
    model.eval()
    with torch.no_grad():
        preds_norm = model(x_norm, edge_index)
        preds = (preds_norm * y_std) + y_mean
    
    return preds.numpy().flatten()




import numpy as np
import torch

def get_gnn_predictions_custom(corr_matrix, features_matrix, formula="abs(corr) > 0.5"):
    """
    Принимает матрицу корреляции и строку-формулу для создания ребер.
    """
    try:
        
        corr = corr_matrix
        
      
        allowed_names = {"abs": np.abs, "corr": corr, "np": np}
        
        
        adj_mask = eval(formula, {"__builtins__": None}, allowed_names)
        adj = adj_mask.astype(int)
        
       
        np.fill_diagonal(adj, 0)
        
       
        if np.sum(adj) == 0:
           
            n = len(corr_matrix)
            for i in range(n):
                adj[i, (i + 1) % n] = 1

        edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
        
        
        
        return preds 
        
    except Exception as e:
        print(f"Formula Error: {e}")
        
        adj = (np.abs(corr_matrix) > 0.5).astype(int)
        edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
        

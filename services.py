import torch
import yfinance as yf
import numpy as np
from .models import StockTicker


def update_stock_predictions():
    tickers = list(StockTicker.objects.values_list('symbol', flat=True))
    if not tickers: return
    
   
    data = yf.download(tickers, period="1y")['Close'].pct_change().dropna()
    
   
    corr = data.corr().values
    adj = (np.abs(corr) > 0.5).astype(int)
    edge_index = torch.tensor(np.array(np.nonzero(adj)), dtype=torch.long)
    
    features = np.stack([data.mean(), data.std()], axis=1)

    features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-6)
    x = torch.tensor(features, dtype=torch.float)

   
    model = StockGNN(num_features=2)
    model_path = 'stock_gnn_weights.pt'
    
    try:
        model.load_state_dict(torch.load(model_path))
    except:
        pass 

   
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    y = torch.tensor(data.mean().values, dtype=torch.float).view(-1, 1)
    
    model.train()
    for _ in range(10):
        optimizer.zero_grad()
        loss = torch.nn.MSELoss()(model(x, edge_index), y)
        loss.backward()
        optimizer.step()

   
    torch.save(model.state_dict(), model_path)

   
    model.eval()
    with torch.no_grad():
        preds = model(x, edge_index).numpy().flatten()
        for i, symbol in enumerate(tickers):
            StockTicker.objects.filter(symbol=symbol).update(prediction=float(preds[i]))
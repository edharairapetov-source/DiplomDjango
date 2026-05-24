


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
import io
import base64
from scipy.optimize import minimize
from django.core.cache import cache

# ---------- Price & caching ----------
def get_price_df_cached(tickers, cache_time=60):
    key = "price_df_" + "_".join(tickers)
    df = cache.get(key)
    if df is None:
        n_days = 252
        df = pd.DataFrame({t: np.cumprod(1 + np.random.normal(0, 0.01, n_days)) for t in tickers})
        cache.set(key, df, cache_time)
    return df

def generate_price_series(n_stocks, n_days=252):
    return np.cumprod(1 + np.random.normal(0, 0.01, (n_days, n_stocks)), axis=0)

# ---------- Portfolio Optimization ----------
def utility_portfolio(c, expected_returns, covariance_matrix):
    return np.dot(expected_returns, c) - 0.5 * np.dot(c, np.dot(covariance_matrix, c))

def optimize_portfolio(expected_returns, covariance_matrix, total_investment=1.0):
    n = len(expected_returns)
    cons = ({'type': 'eq', 'fun': lambda c: np.sum(c) - total_investment})
    bounds = [(0, total_investment) for _ in range(n)]
    result = minimize(
        lambda c: -utility_portfolio(c, expected_returns, covariance_matrix),
        x0=np.ones(n)/n,
        constraints=cons,
        bounds=bounds
    )
    return result.x

# ---------- Graphs ----------
def create_stock_correlation_graph(n_stocks, correlation_threshold=0.5):
    corr_matrix = np.random.uniform(-1, 1, size=(n_stocks, n_stocks))
    np.fill_diagonal(corr_matrix, 1)
    corr_matrix = (corr_matrix + corr_matrix.T) / 2
    G = nx.Graph()
    G.add_nodes_from(range(n_stocks))
    for i, j in combinations(range(n_stocks), 2):
        if abs(corr_matrix[i, j]) > correlation_threshold:
            G.add_edge(i, j, weight=corr_matrix[i, j])
    return G, corr_matrix

def plot_stock_graph(G):
    pos = nx.spring_layout(G)
    edges = G.edges(data=True)
    weights = [abs(d['weight']) for _, _, d in edges]
    plt.figure(figsize=(6,4))
    nx.draw(G, pos, with_labels=True, node_size=700, edge_color='gray', width=[w*3 for w in weights])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return 'data:image/png;base64,' + base64.b64encode(buf.read()).decode()

def graph_to_graphon(corr_matrix):
    max_val = np.max(np.abs(corr_matrix))
    return corr_matrix / max_val if max_val > 0 else corr_matrix

def visualize_graphon(graphon):
    plt.imshow(graphon, cmap='Greys', interpolation='nearest')
    plt.colorbar()
    plt.title("Market Connection Graphon")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return 'data:image/png;base64,' + base64.b64encode(buf.read()).decode()

# ---------- Backtesting ----------
def backtest_portfolio(weights, price_data):
    returns = price_data[1:] / price_data[:-1] - 1
    port_returns = returns.dot(weights)
    equity = np.cumprod(1 + port_returns)
    peak = np.maximum.accumulate(equity)
    drawdown = (equity - peak) / peak
    max_drawdown = np.min(drawdown)
    sharpe = np.mean(port_returns) / np.std(port_returns) * np.sqrt(252)
    return {
        "equity": equity.tolist(),
        "sharpe": round(sharpe, 3),
        "max_drawdown": round(max_drawdown, 3),
        "final_value": round(equity[-1], 3)
    }

# ---------- Main analysis ----------
def run_analysis_django(n_stocks=10, corr_threshold=0.6):
    tickers = [f"Stock {i+1}" for i in range(n_stocks)]
    price_df = get_price_df_cached(tickers)

    # Graph
    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)
    graphon_img = visualize_graphon(graph_to_graphon(corr_matrix))

    # Portfolio
    expected_returns = np.random.uniform(0.01, 0.2, n_stocks)
    cov_matrix = np.random.uniform(0.001, 0.02, (n_stocks, n_stocks))
    cov_matrix = (cov_matrix + cov_matrix.T) / 2
    np.fill_diagonal(cov_matrix, np.random.uniform(0.005, 0.03, n_stocks))
    weights = optimize_portfolio(expected_returns, cov_matrix)

    # Backtest
    price_data = generate_price_series(n_stocks, 252)
    bt = backtest_portfolio(weights, price_data)
    plt.figure(figsize=(8,4))
    plt.plot(bt["equity"])
    plt.title("Backtest Equity Curve")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    bt_img = base64.b64encode(buf.read()).decode()

    return {
        "tickers": tickers,
        "graph_url": graph_img,
        "graphon_url": graphon_img,
        "weights": np.round(weights, 2).tolist(),
        "expected_return": round(float(np.dot(expected_returns, weights)), 4),
        "risk": round(float(np.sqrt(weights.T @ cov_matrix @ weights)), 4),
        "backtest_final_value": bt["final_value"],
        "backtest_sharpe": bt["sharpe"],
        "backtest_drawdown": bt["max_drawdown"],
        "backtest_equity_curve_img": bt_img
    }

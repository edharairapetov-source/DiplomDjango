import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
import io
import base64
import math
from scipy.optimize import minimize

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
    weights = [abs(data['weight']) for _, _, data in edges]
    plt.figure(figsize=(6,4))
    nx.draw(G, pos, with_labels=True, node_size=700, edge_color='gray', width=[w*3 for w in weights])
    plt.title("Stock Correlation Network")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    return 'data:image/png;base64,' + img_str

def graph_to_graphon(corr_matrix):
    max_val = np.max(corr_matrix)
    return corr_matrix / max_val if max_val > 0 else corr_matrix

def visualize_graphon(graphon):
    plt.imshow(graphon, cmap='Greys', interpolation='nearest')
    plt.colorbar()
    plt.title('Market Connection Graphon')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    return 'data:image/png;base64,' + img_str

def utility_portfolio(c, expected_returns, covariance_matrix):
    return np.dot(expected_returns, c) - 0.5 * np.dot(c, np.dot(covariance_matrix, c))

def optimize_portfolio(expected_returns, covariance_matrix, total_investment=1.0):
    n = len(expected_returns)
    cons = ({'type': 'eq', 'fun': lambda c: np.sum(c) - total_investment})
    bounds = [(0, total_investment) for _ in range(n)]
    result = minimize(lambda c: -utility_portfolio(c, expected_returns, covariance_matrix),
                      x0=np.ones(n) / n,
                      constraints=cons,
                      bounds=bounds)
    return result.x

def run_analysis(**kwargs):
    n_stocks = kwargs.get('n_stocks', 10)
    corr_threshold = kwargs.get('corr_threshold', 0.6)
    min_return = kwargs.get('min_return', 0.01)
    max_return = kwargs.get('max_return', 0.2)
    min_cov = kwargs.get('min_cov', 0.001)
    max_cov = kwargs.get('max_cov', 0.02)
    S0 = kwargs.get('S0', 100)
    T = kwargs.get('T', 1.0)
    r = kwargs.get('r', 0.05)
    sigma = kwargs.get('sigma', 0.2)
    I = kwargs.get('I', 10000)

    # Generate graph
    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)
    graphon = graph_to_graphon(corr_matrix)
    graphon_img = visualize_graphon(graphon)

    # Expected returns
    expected_returns = np.random.uniform(min_return, max_return, size=n_stocks)

    # Covariance matrix
    random_cov = np.random.uniform(min_cov, max_cov, size=(n_stocks, n_stocks))
    covariance_matrix = (random_cov + random_cov.T) / 2
    np.fill_diagonal(covariance_matrix, np.random.uniform(0.005, 0.03, size=n_stocks))

    # Optimize portfolio
    weights = optimize_portfolio(expected_returns, covariance_matrix)
    expected_portfolio_return = np.dot(expected_returns, weights)
    risk = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))

    # Black-Scholes simulation
    rng = np.random.default_rng()
    ST_bs = S0 * np.exp((r - sigma**2 / 2) * T + sigma * math.sqrt(T) * rng.standard_normal(I))
    bs_sample = np.round(ST_bs[:8], 1)
    bs_mean = np.round(np.mean(ST_bs), 2)
    bs_std = np.round(np.std(ST_bs), 2)

    # Jump diffusion simulation
    lambda_jump = kwargs.get('lambda_jump', 0.3)
    mu_jump = kwargs.get('mu_jump', -0.3)
    delta_jump = kwargs.get('delta_jump', 0.1)
    z = rng.standard_normal(I)
    y = rng.poisson(lambda_jump * T, I)
    jump_component = (np.exp(mu_jump + delta_jump * rng.standard_normal(I)) - 1) * y
    ST_jd = S0 * np.exp(
        (r - lambda_jump * (np.exp(mu_jump + delta_jump**2/2) - 1) - sigma**2/2) * T +
        sigma * math.sqrt(T) * z
    )
    ST_jd *= (1 + jump_component)
    jd_sample = np.round(ST_jd[:8], 1)
    jd_mean = np.round(np.mean(ST_jd), 2)
    jd_std = np.round(np.std(ST_jd), 2)

    results = {
        'graph_url': graph_img,
        'graphon_url': graphon_img,
        'weights': np.round(weights, 2).tolist(),
        'expected_return': np.round(expected_portfolio_return, 4),
        'risk': np.round(risk, 4),
        'bs_sample': bs_sample.tolist(),
        'bs_mean': bs_mean,
        'bs_std': bs_std,
        'jd_sample': jd_sample.tolist(),
        'jd_mean': jd_mean,
        'jd_std': jd_std,
    }

    return results

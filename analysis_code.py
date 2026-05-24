import pandas as pd





import matplotlib
matplotlib.use("Agg")  

import matplotlib.pyplot as plt





import yfinance as yf
import pandas as pd


import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
import io
import base64
import math
from scipy.optimize import minimize



def generate_price_series(n_stocks, n_days=252, mu=0.10, sigma=0.2, seed=None):
    """
    Simulates realistic price movements for multiple assets using
    geometric Brownian motion.
    """
    rng = np.random.default_rng(seed)
    dt = 1 / 252
    prices = np.zeros((n_days, n_stocks))
    prices[0] = np.random.uniform(50, 150, n_stocks)

    for t in range(1, n_days):
        rand = rng.standard_normal(n_stocks)
        prices[t] = prices[t-1] * np.exp((mu - sigma**2/2) * dt + sigma * np.sqrt(dt) * rand)

    return prices


def backtest_portfolio(weights, price_data):
    """
    Performs a rolling backtest on historical data.
    """
    n_days, n_stocks = price_data.shape

    
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
    nx.draw(G, pos, with_labels=True, node_size=700,
            edge_color='gray', width=[w*3 for w in weights])

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


def utility_portfolio1(c, expected_returns, covariance_matrix):
    return np.dot(expected_returns, c) - 0.5 * np.dot(c, np.dot(covariance_matrix, c))
def utility_portfolio(c, expected_returns, covariance_matrix, gamma=0.1):
    return (
        np.dot(expected_returns, c)
        - 0.5 * np.dot(c, np.dot(covariance_matrix, c))
        - gamma * np.sum(c**2)
    )


def optimize_portfolio(expected_returns, covariance_matrix, total_investment=1.0):
    n = len(expected_returns)
    cons = ({'type': 'eq', 'fun': lambda c: np.sum(c) - total_investment})
    bounds = [(0, total_investment) for _ in range(n)]

    result = minimize(lambda c: -utility_portfolio(c, expected_returns, covariance_matrix),
                      x0=np.ones(n) / n,
                      constraints=cons,
                      bounds=bounds)
    return result.x








def analyze_alpha_factor(factor: pd.DataFrame, prices: pd.DataFrame, n_quantiles=5):
    """
    Minimal Alphalens-style factor analysis.
    factor: DataFrame (date x asset)
    prices: DataFrame (date x asset)
    """

    
    forward_returns = prices.pct_change().shift(-1)

   
    factor, forward_returns = factor.align(forward_returns, join="inner")

    
    ic_series = factor.corrwith(forward_returns, axis=1)
    ic_mean = ic_series.mean()
    ic_std = ic_series.std()
    ic_ir = ic_mean / ic_std if ic_std != 0 else 0

    
    quantile_returns = []

    for date in factor.index:
        df = pd.DataFrame({
            "factor": factor.loc[date],
            "fwd_ret": forward_returns.loc[date]
        }).dropna()

        if len(df) < n_quantiles:
            continue

        df["quantile"] = pd.qcut(df["factor"], n_quantiles, labels=False)
        quantile_returns.append(df.groupby("quantile")["fwd_ret"].mean())

    quantile_returns = pd.DataFrame(quantile_returns)
    mean_quantile_returns = quantile_returns.mean()

    return {
        "ic_mean": round(ic_mean, 4),
        "ic_ir": round(ic_ir, 4),
        "quantile_returns": mean_quantile_returns.round(4).tolist()
    }




def analyze_ml_predictions(predictions: pd.DataFrame,
                           prices: pd.DataFrame,
                           n_quantiles: int = 5):

    forward_returns = prices.pct_change().shift(-1)
    predictions, forward_returns = predictions.align(forward_returns, join="inner")

    ic_series = predictions.corrwith(forward_returns, axis=1)
    ic_mean = ic_series.mean()
    ic_std = ic_series.std()
    ic_ir = ic_mean / ic_std if ic_std > 0 else 0.0

    qrets = []

    for dt in predictions.index:
        df = pd.DataFrame({
            "pred": predictions.loc[dt],
            "fwd_ret": forward_returns.loc[dt]
        }).dropna()

        if len(df) < n_quantiles:
            continue

        df["q"] = pd.qcut(df["pred"], n_quantiles, labels=False, duplicates="drop")
        qrets.append(df.groupby("q")["fwd_ret"].mean())

    qrets = pd.DataFrame(qrets)

   
    top_q = n_quantiles - 1
    if 0 in qrets.columns and top_q in qrets.columns:
        ls_return = (qrets[top_q] - qrets[0]).mean()
    else:
        ls_return = 0.0

    return {
        "ml_ic_mean": round(ic_mean, 4),
        "ml_ic_ir": round(ic_ir, 4),
        "ml_quantile_returns": qrets.mean().round(4).tolist(),
        "ml_long_short_return": round(ls_return, 4)
    }













def run_analysis_cleanreal(**kwargs):
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.ensemble import RandomForestRegressor
    import io, base64

    
    tickers = kwargs.get("tickers", ["AAPL", "MSFT", "GOOG"])
    period = kwargs.get("period", "3y")
    rebalance_window = kwargs.get("rebalance_window", 63)  
    n_simulations = kwargs.get("n_simulations", 1000)

    
    price_df = yf.download(tickers, period=period)["Close"].dropna()
    returns = price_df.pct_change().dropna()
    n_stocks = len(tickers)

    
    def add_technical_indicators(prices, ma_windows=[5,10,20]):
        tech = pd.DataFrame(index=prices.index)
        for w in ma_windows:
            tech[f"SMA_{w}"] = prices.rolling(w).mean()
        tech["forward_return"] = prices.pct_change().shift(-1)
        return tech

    tech_indicators = add_technical_indicators(price_df)
    
    
    plt.figure(figsize=(10,5))
    plt.plot(price_df.index, price_df[tickers[0]], label="Price")
    for w in [5,10,20]:
        plt.plot(tech_indicators.index, tech_indicators[f"SMA_{w}"].iloc[:,0], label=f"SMA {w}")
    plt.title("Price with Moving Averages")
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    ma_chart = base64.b64encode(buf.getvalue()).decode()

    
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    def max_sharpe_weights(mean_returns, cov_matrix, rf_rate=0.04):
        from scipy.optimize import minimize
        n = len(mean_returns)
        def neg_sharpe(w):
            ret = np.dot(w, mean_returns)
            vol = np.sqrt(w.T @ cov_matrix @ w)
            return -(ret - rf_rate) / vol
        constraints = ({'type':'eq','fun':lambda w: np.sum(w)-1})
        bounds = [(0,1) for _ in range(n)]
        result = minimize(neg_sharpe, x0=np.ones(n)/n, bounds=bounds, constraints=constraints)
        return result.x

    weights = max_sharpe_weights(mean_returns.values, cov_matrix.values)

    
    portfolio_returns = []
    weight_history = []

    features = tech_indicators.dropna()
    for start in range(0, len(returns) - rebalance_window, rebalance_window):
        train_returns = returns.iloc[start:start+rebalance_window]
        test_returns = returns.iloc[start+rebalance_window:start+2*rebalance_window]
        if len(test_returns)==0:
            break

        X_train, y_train = features.align(train_returns, join='inner', axis=0)
        X_test, y_test = features.align(test_returns, join='inner', axis=0)

        weights_step = []
        for asset in tickers:
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X_train, y_train[asset])
            pred = rf.predict(X_test)
            w = np.sign(pred).mean()  
            weights_step.append(w)
        weight_history.append(weights_step)

        
        test_port_returns = X_test.index.map(lambda idx: (test_returns.loc[idx].values * weights_step).sum())
        portfolio_returns.extend(test_port_returns)

    portfolio_returns = np.array(portfolio_returns)
    equity = np.cumprod(1 + portfolio_returns)

    
    annual_return = np.mean(portfolio_returns)*252
    annual_vol = np.std(portfolio_returns)*np.sqrt(252)
    sharpe_ratio = annual_return/annual_vol
    peak = np.maximum.accumulate(equity)
    drawdown = (equity - peak)/peak
    max_dd = np.min(drawdown)

   
    plt.figure(figsize=(8,4))
    plt.plot(equity)
    plt.title("ML Portfolio Equity Curve")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    equity_chart = base64.b64encode(buf.getvalue()).decode()

    
    S0 = price_df.iloc[-1].mean()
    T, sigma, r, I = 1.0, 0.2, 0.05, n_simulations
    bs_prices = np.zeros((I, n_stocks))
    for i in range(I):
        bs_prices[i] = S0*np.exp((r-0.5*sigma**2)*T + sigma*np.sqrt(T)*np.random.randn(n_stocks))
    bs_mean = float(np.mean(bs_prices))
    bs_std = float(np.std(bs_prices))

    
    results = {
        "tickers": tickers,
        "weights_last_rebalance": np.round(weight_history[-1] if weight_history else weights,3).tolist(),
        "annual_return": round(float(annual_return),4),
        "annual_volatility": round(float(annual_vol),4),
        "sharpe_ratio": round(float(sharpe_ratio),4),
        "max_drawdown": round(float(max_dd),4),
        "equity_curve": equity.tolist(),
        "equity_chart": equity_chart,
        "technical_chart": ma_chart,
        "technical_indicators": tech_indicators.round(4).to_dict(),
        "bs_mean": bs_mean,
        "bs_std": bs_std
    }

    return results




import networkx as nx

def create_stock_correlation_graph_from_matrix(corr_matrix, threshold=0.6):
    
    n = corr_matrix.shape[0]
    
    G = nx.Graph()

    
    for i in range(n):
        G.add_node(i)

    
    for i in range(n):
        for j in range(i + 1, n):

            corr = corr_matrix[i, j]

            if abs(corr) >= threshold:
                G.add_edge(i, j, weight=float(corr))

    return G


def run_analysis(**kwargs):

    import numpy as np
    import pandas as pd
    import yfinance as yf
    import matplotlib.pyplot as plt
    import base64
    import io
    import math

    

    tickers = kwargs.get("tickers", [
        "AAPL","MSFT","GOOG","AMZN","META",
        "NVDA","TSLA","AMD","INTC","NFLX"
    ])

    data = yf.download(tickers, period="1y")["Close"]

    price_df = data.dropna()

    price_data = price_df.values
    n_stocks = price_df.shape[1]

    

    returns = price_df.pct_change().dropna()

    
    expected_returns = returns.mean().values

   
    covariance_matrix = returns.cov().values

    

    corr_matrix = returns.corr().values

    G = create_stock_correlation_graph_from_matrix(
        corr_matrix,
        threshold=kwargs.get("corr_threshold", 0.6)
    )

    graph_img = plot_stock_graph(G)

    graphon = graph_to_graphon(corr_matrix)

    graphon_img = visualize_graphon(graphon)

    

    weights = optimize_portfolio(expected_returns, covariance_matrix)

    

    S0 = kwargs.get('S0', 100)
    T = kwargs.get('T', 1.0)
    sigma = kwargs.get('sigma', 0.2)
    r = kwargs.get('r', 0.05)
    I = kwargs.get('I', 1000)

    bs_prices = np.zeros((I, n_stocks))

    for i in range(I):

        bs_prices[i] = S0 * np.exp(
            (r - 0.5 * sigma**2) * T
            + sigma * np.sqrt(T) * np.random.randn(n_stocks)
        )

    bs_mean = np.mean(bs_prices)
    bs_std = np.std(bs_prices)

    

    lambda_jump = kwargs.get('lambda_jump', 0.3)
    mu_jump = kwargs.get('mu_jump', -0.3)
    delta_jump = kwargs.get('delta_jump', 0.1)

    jd_prices = np.zeros((I, n_stocks))

    for i in range(I):

        jumps = np.random.poisson(lambda_jump * T, n_stocks)

        jump_sizes = np.random.normal(
            mu_jump,
            delta_jump,
            n_stocks
        ) * jumps

        jd_prices[i] = S0 * np.exp(
            (r - 0.5 * sigma**2) * T
            + sigma * np.sqrt(T) * np.random.randn(n_stocks)
            + jump_sizes
        )

    jd_mean = np.mean(jd_prices)
    jd_std = np.std(jd_prices)

    

    formula_str = kwargs.get('formula_str', 'pred')

    safe_globals = {"__builtins__": None, "math": math}

    gnn_prediction = {}

    for i in range(n_stocks):

        expr = formula_str.replace('pred', str(i))

        try:
            gnn_prediction[f"pred_{i}"] = float(
                eval(expr, safe_globals)
            )

        except:
            gnn_prediction[f"pred_{i}"] = 0.0

    

    bt = backtest_portfolio(weights, price_data)

   

    alpha_factor = returns

    alpha_analysis = analyze_alpha_factor(
        factor=alpha_factor,
        prices=price_df
    )

   

    ml_predictions = returns.shift(1)

    ml_alpha_stats = analyze_ml_predictions(
        predictions=ml_predictions,
        prices=price_df
    )

    
    portfolio_return = float(np.dot(expected_returns, weights))

    portfolio_risk = float(
        np.sqrt(
            np.dot(
                weights.T,
                np.dot(covariance_matrix, weights)
            )
        )
    )

   

    plt.figure(figsize=(8,4))

    plt.plot(bt["equity"])

    plt.title("Backtest Equity Curve")

    plt.xlabel("Days")

    plt.ylabel("Portfolio Value")

    buf = io.BytesIO()

    plt.savefig(buf, format="png")

    plt.close()

    buf.seek(0)

    backtest_img = base64.b64encode(buf.read()).decode()

    

    results = {

        "graph_url": graph_img,

        "graphon_url": graphon_img,

        "weights": np.round(weights,3).tolist(),

        "expected_return": round(portfolio_return,4),

        "risk": round(portfolio_risk,4),

        "bs_mean": float(bs_mean),

        "bs_std": float(bs_std),

        "jd_mean": float(jd_mean),

        "jd_std": float(jd_std),

        "gnn_prediction": gnn_prediction,

        "backtest_equity_curve": bt["equity"],

        "backtest_final_value": bt["final_value"],

        "backtest_sharpe": bt["sharpe"],

        "backtest_drawdown": bt["max_drawdown"],

        "backtest_equity_curve_img": backtest_img,

        "alpha_analysis": alpha_analysis,

        "ml_alpha_analysis": ml_alpha_stats
    }

    return results

def run_analysisшьзщкефтемукн(**kwargs):
    n_stocks = kwargs.get('n_stocks', 10)
    corr_threshold = kwargs.get('corr_threshold', 0.6)

    
    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)
    graphon = graph_to_graphon(corr_matrix)
    graphon_img = visualize_graphon(graphon)

    
    min_er = kwargs.get("min_expected_return", 0.01)
    max_er = kwargs.get("max_expected_return", 0.2)

    expected_returns = np.random.uniform(min_er, max_er, size=n_stocks)

    #expected_returns = np.random.uniform(0.01, 0.2, size=n_stocks)
    random_cov = np.random.uniform(0.001, 0.02, size=(n_stocks, n_stocks))
    covariance_matrix = (random_cov + random_cov.T) / 2
    np.fill_diagonal(covariance_matrix, np.random.uniform(0.005, 0.03, size=n_stocks))

    
    weights = optimize_portfolio(expected_returns, covariance_matrix)

   
    S0 = kwargs.get('S0', 100)
    T = kwargs.get('T', 1.0)
    sigma = kwargs.get('sigma', 0.2)
    r = kwargs.get('r', 0.05)
    I = kwargs.get('I', 1000)

    bs_prices = np.zeros((I, n_stocks))
    for i in range(I):
        bs_prices[i] = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * np.random.randn(n_stocks))
    bs_mean = np.mean(bs_prices)
    bs_std = np.std(bs_prices)

    
    lambda_jump = kwargs.get('lambda_jump', 0.3)
    mu_jump = kwargs.get('mu_jump', -0.3)
    delta_jump = kwargs.get('delta_jump', 0.1)

    jd_prices = np.zeros((I, n_stocks))
    for i in range(I):
        jumps = np.random.poisson(lambda_jump * T, n_stocks)
        jump_sizes = np.random.normal(mu_jump, delta_jump, n_stocks) * jumps
        jd_prices[i] = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * np.random.randn(n_stocks) + jump_sizes)
    jd_mean = np.mean(jd_prices)
    jd_std = np.std(jd_prices)

   
    formula_str = kwargs.get('formula_str', 'pred')
    safe_globals = {"__builtins__": None, "math": math}

    gnn_prediction = {}
    for i in range(n_stocks):
        expr = formula_str.replace('pred', str(i))
        try:
            gnn_prediction[f"pred_{i}"] = float(eval(expr, safe_globals))
        except:
            gnn_prediction[f"pred_{i}"] = 0.0  # fallback

    

    tickers = kwargs.get("tickers", [
       "AAPL","MSFT","GOOG","AMZN","META",
       "NVDA","TSLA","AMD","INTC","NFLX"
    ])

    data = yf.download(tickers, period="1y")["Close"]

    price_df = data.dropna()


    n_stocks = price_df.shape[1]


    if len(weights) != n_stocks:
        weights = optimize_portfolio(expected_returns[:n_stocks], covariance_matrix[:n_stocks, :n_stocks])

    price_data = price_df.values

    bt = backtest_portfolio(weights, price_data)
    
    #price_data = generate_price_series(n_stocks, n_days=252)
    #tickers = kwargs.get("tickers", ["AAPL", "MSFT", "GOOG"])
    #data = yf.download(tickers, period="1y")["Close"]

    #price_df = data.dropna()
    #price_data = price_df.values
    #price_data2 = generate_price_series(n_stocks, n_days=252)
    #bt = backtest_portfolio(weights, price_data)

    
    results = {
        'graph_url': graph_img,
        'graphon_url': graphon_img,
        'weights': np.round(weights, 2).tolist(),
        'expected_return': np.round(np.dot(expected_returns, weights), 4),
        'risk': np.round(np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights))), 4),
        'bs_sample': bs_prices.tolist(),
        'bs_mean': float(bs_mean),
        'bs_std': float(bs_std),
        'jd_sample': jd_prices.tolist(),
        'jd_mean': float(jd_mean),
        'jd_std': float(jd_std),
        'gnn_prediction': gnn_prediction,
        'backtest_equity_curve': bt["equity"],
        'backtest_final_value': bt["final_value"],
        'backtest_sharpe': bt["sharpe"],
        'backtest_drawdown': bt["max_drawdown"]
    }

    
    plt.figure(figsize=(8,4))
    plt.plot(bt["equity"])
    plt.title("Backtest Equity Curve")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Value")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    
    results['backtest_equity_curve_img'] = base64.b64encode(buf.read()).decode()






        
    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)

    
    alpha_factor = price_df.pct_change()

    alpha_analysis = analyze_alpha_factor(
        factor=alpha_factor,
        prices=price_df
    )

    results["alpha_analysis"] = alpha_analysis


   

    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)

    
    ml_predictions = price_df.pct_change().shift(1)  

    ml_alpha_stats = analyze_ml_predictions(
        predictions=ml_predictions,
        prices=price_df
    )

    results["ml_alpha_analysis"] = ml_alpha_stats
    
    results['backtest_equity_curve_img'] = base64.b64encode(buf.read()).decode()

   






    
    return results


def run_analysis2(**kwargs):
    n_stocks = kwargs.get('n_stocks', 10)
    corr_threshold = kwargs.get('corr_threshold', 0.6)

   
    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)
    graphon = graph_to_graphon(corr_matrix)
    graphon_img = visualize_graphon(graphon)

    
    min_er = kwargs.get("min_expected_return", 0.01)
    max_er = kwargs.get("max_expected_return", 0.2)

    expected_returns = np.random.uniform(min_er, max_er, size=n_stocks)

    #expected_returns = np.random.uniform(0.01, 0.2, size=n_stocks)
    random_cov = np.random.uniform(0.001, 0.02, size=(n_stocks, n_stocks))
    covariance_matrix = (random_cov + random_cov.T) / 2
    np.fill_diagonal(covariance_matrix, np.random.uniform(0.005, 0.03, size=n_stocks))

    
    weights = optimize_portfolio(expected_returns, covariance_matrix)

    
    S0 = kwargs.get('S0', 100)
    T = kwargs.get('T', 1.0)
    sigma = kwargs.get('sigma', 0.2)
    r = kwargs.get('r', 0.05)
    I = kwargs.get('I', 1000)

    bs_prices = np.zeros((I, n_stocks))
    for i in range(I):
        bs_prices[i] = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * np.random.randn(n_stocks))
    bs_mean = np.mean(bs_prices)
    bs_std = np.std(bs_prices)

    
    lambda_jump = kwargs.get('lambda_jump', 0.3)
    mu_jump = kwargs.get('mu_jump', -0.3)
    delta_jump = kwargs.get('delta_jump', 0.1)

    jd_prices = np.zeros((I, n_stocks))
    for i in range(I):
        jumps = np.random.poisson(lambda_jump * T, n_stocks)
        jump_sizes = np.random.normal(mu_jump, delta_jump, n_stocks) * jumps
        jd_prices[i] = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * np.random.randn(n_stocks) + jump_sizes)
    jd_mean = np.mean(jd_prices)
    jd_std = np.std(jd_prices)

    
    formula_str = kwargs.get('formula_str', 'pred')
    safe_globals = {"__builtins__": None, "math": math}

    gnn_prediction = {}
    for i in range(n_stocks):
        expr = formula_str.replace('pred', str(i))
        try:
            gnn_prediction[f"pred_{i}"] = float(eval(expr, safe_globals))
        except:
            gnn_prediction[f"pred_{i}"] = 0.0  

   
    price_data = generate_price_series(n_stocks, n_days=252)
    tickers = kwargs.get("tickers", ["AAPL", "MSFT", "GOOG"])
    data = yf.download(tickers, period="1y")["Close"]

    price_df = data.dropna()
    price_data = price_df.values
    price_data2 = generate_price_series(n_stocks, n_days=252)
    bt = backtest_portfolio(weights, price_data)

    results = {
        'graph_url': graph_img,
        'graphon_url': graphon_img,
        'weights': np.round(weights, 2).tolist(),
        'expected_return': np.round(np.dot(expected_returns, weights), 4),
        'risk': np.round(np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights))), 4),
        'bs_sample': bs_prices.tolist(),
        'bs_mean': float(bs_mean),
        'bs_std': float(bs_std),
        'jd_sample': jd_prices.tolist(),
        'jd_mean': float(jd_mean),
        'jd_std': float(jd_std),
        'gnn_prediction': gnn_prediction,
        'backtest_equity_curve': bt["equity"],
        'backtest_final_value': bt["final_value"],
        'backtest_sharpe': bt["sharpe"],
        'backtest_drawdown': bt["max_drawdown"]
    }

   
    plt.figure(figsize=(8,4))
    plt.plot(bt["equity"])
    plt.title("Backtest Equity Curve")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Value")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    
    results['backtest_equity_curve_img'] = base64.b64encode(buf.read()).decode()






     
    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)

   
    alpha_factor = price_df.pct_change()

    alpha_analysis = analyze_alpha_factor(
        factor=alpha_factor,
        prices=price_df
    )

    results["alpha_analysis"] = alpha_analysis


   

    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)

    
    ml_predictions = price_df.pct_change().shift(1)  

    ml_alpha_stats = analyze_ml_predictions(
        predictions=ml_predictions,
        prices=price_df
    )

    results["ml_alpha_analysis"] = ml_alpha_stats
    
    results['backtest_equity_curve_img'] = base64.b64encode(buf.read()).decode()

   






    
    return results













def excel_summary_stats(price_df: pd.DataFrame):
    return pd.DataFrame({
        "mean": price_df.mean(),
        "std": price_df.std(),
        "min": price_df.min(),
        "max": price_df.max(),
        "last": price_df.iloc[-1],
    }).round(4)


def excel_correlation(price_df: pd.DataFrame):
    return price_df.pct_change().corr().round(3)


def excel_pivot_returns(price_df: pd.DataFrame):
    returns = price_df.pct_change().dropna()
    pivot = (
        returns
        .melt(var_name="Asset", value_name="Return")
        .groupby("Asset")
        .agg(
            avg_return=("Return", "mean"),
            volatility=("Return", "std"),
            observations=("Return", "count"),
        )
    )
    return pivot.round(4)


def excel_for_template(price_df: pd.DataFrame):
   
    summary_table = excel_summary_stats(price_df).reset_index().rename(columns={"index": "Asset"})
    
   
    corr_matrix = excel_correlation(price_df)
    corr_table = corr_matrix.reset_index().rename(columns={"index": "Asset"})
    
  
    pivot_table = excel_pivot_returns(price_df).reset_index()
    
    return {
        "summary_table": summary_table.to_dict(orient="records"),
        "correlation_table": corr_table.to_dict(orient="records"),
        "pivot_table": pivot_table.to_dict(orient="records")
    }




def plot_moving_averages(price_df, asset_index=0, windows=[5, 20, 50]):
    """ Generates a chart with Price and Multiple SMA lines """
    plt.figure(figsize=(10, 6))
    asset_name = price_df.columns[asset_index]
    
   
    plt.plot(price_df.index, price_df.iloc[:, asset_index], label=f"{asset_name} Price", color='black', alpha=0.6)
    
  
    for w in windows:
        sma = price_df.iloc[:, asset_index].rolling(window=w).mean()
        plt.plot(price_df.index, sma, label=f"SMA {w}")
    
    plt.title(f"Moving Averages: {asset_name}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode()

def plot_bollinger_bands(price_df, asset_index=0, window=20, num_std=2):
    """ Generates a Bollinger Band chart """
    plt.figure(figsize=(10, 6))
    asset_name = price_df.columns[asset_index]
    series = price_df.iloc[:, asset_index]
    
   
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    
    plt.plot(price_df.index, series, label="Price", color='blue', alpha=0.5)
    plt.plot(price_df.index, sma, label="Middle Band (SMA)", color='orange')
    plt.plot(price_df.index, upper_band, label="Upper Band", color='green', linestyle='--')
    plt.plot(price_df.index, lower_band, label="Lower Band", color='red', linestyle='--')
    
    
    plt.fill_between(price_df.index, lower_band, upper_band, color='gray', alpha=0.1)
    
    plt.title(f"Bollinger Bands: {asset_name}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode()
def add_technical_indicators(price_df: pd.DataFrame, ma_windows=[5, 10, 20]):
    """
    Adds simple moving averages and forward derivatives to a price DataFrame.
    Returns a dictionary with SMA and derivative DataFrames.
    """
    indicators = {}
    
   
    for w in ma_windows:
        indicators[f"SMA_{w}"] = price_df.rolling(window=w).mean()
    
    
    indicators["forward_return"] = price_df.pct_change().shift(-1)
    
    return indicators





def run_analysis_clean(**kwargs):
    n_stocks = kwargs.get("n_stocks", 10)
    corr_threshold = kwargs.get("corr_threshold", 0.6)

   
    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)
    graphon = graph_to_graphon(corr_matrix)
    graphon_img = visualize_graphon(graphon)

   
    expected_returns = np.random.uniform(0.01, 0.2, size=n_stocks)
    cov_matrix = np.random.uniform(0.001, 0.02, size=(n_stocks, n_stocks))
    cov_matrix = (cov_matrix + cov_matrix.T) / 2
    np.fill_diagonal(cov_matrix, np.random.uniform(0.005, 0.03, size=n_stocks))

    
    weights = optimize_portfolio(expected_returns, cov_matrix)


   
    price_data = generate_price_series(n_stocks, n_days=252)
    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)

   
    bt = backtest_portfolio(weights, price_data)

   
    excel_summary = excel_summary_stats(price_df)
    excel_corr = excel_correlation(price_df)
    excel_pivot = excel_pivot_returns(price_df)

    
    S0 = kwargs.get('S0', 100)
    T = kwargs.get('T', 1.0)
    sigma = kwargs.get('sigma', 0.2)
    r = kwargs.get('r', 0.05)
    I = kwargs.get('I', 1000)

    bs_prices = np.zeros((I, n_stocks))
    for i in range(I):
        bs_prices[i] = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * np.random.randn(n_stocks))
    bs_mean = float(np.mean(bs_prices))
    bs_std = float(np.std(bs_prices))

   
    lambda_jump = kwargs.get('lambda_jump', 0.3)
    mu_jump = kwargs.get('mu_jump', -0.3)
    delta_jump = kwargs.get('delta_jump', 0.1)

    jd_prices = np.zeros((I, n_stocks))
    for i in range(I):
        jumps = np.random.poisson(lambda_jump * T, n_stocks)
        jump_sizes = np.random.normal(mu_jump, delta_jump, n_stocks) * jumps
        jd_prices[i] = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * np.random.randn(n_stocks) + jump_sizes)
    jd_mean = float(np.mean(jd_prices))
    jd_std = float(np.std(jd_prices))

   
    plt.figure(figsize=(8,4))
    plt.plot(bt["equity"])
    plt.title("Backtest Equity Curve")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Value")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    bt_img = base64.b64encode(buf.read()).decode()

  
    alpha_factor = price_df.pct_change()
    alpha_analysis = analyze_alpha_factor(alpha_factor, price_df)

    
    ml_predictions = price_df.pct_change().shift(1)  
    ml_analysis = analyze_ml_predictions(ml_predictions, price_df)

 
    results = {
        "graph_url": graph_img,
        "graphon_url": graphon_img,
        "weights": np.round(weights, 2).tolist(),
        "expected_return": round(float(np.dot(expected_returns, weights)), 4),
        "risk": round(float(np.sqrt(weights.T @ cov_matrix @ weights)), 4),

        "backtest_final_value": bt["final_value"],
        "backtest_sharpe": bt["sharpe"],
        "backtest_drawdown": bt["max_drawdown"],
        "backtest_equity_curve_img": bt_img,

        
        "excel_summary": excel_summary.to_dict(),
        "excel_correlation": excel_corr.to_dict(),
        "excel_pivot": excel_pivot.reset_index().to_dict(orient="records"),

        #
        "bs_mean": bs_mean,
        "bs_std": bs_std,
        "jd_mean": jd_mean,
        "jd_std": jd_std,
        "bs_sample": bs_prices.tolist(),
        "jd_sample": jd_prices.tolist(),

       
        "alpha_analysis": alpha_analysis,
        "ml_alpha_analysis": ml_analysis
    }











    tech_indicators = add_technical_indicators(price_df, ma_windows=[5,10,20])


    results["technical_indicators"] = {
       "SMA_5": tech_indicators["SMA_5"].round(2).to_dict(),
       "SMA_10": tech_indicators["SMA_10"].round(2).to_dict(),
       "SMA_20": tech_indicators["SMA_20"].round(2).to_dict(),
       "forward_return": tech_indicators["forward_return"].round(4).to_dict(),
    }

    
    avg_forward_derivative = tech_indicators["forward_return"].mean(axis=1)
    results["technical_indicators"]["avg_forward_derivative"] = avg_forward_derivative.round(4).to_dict()
    
    plt.figure(figsize=(10,5))
    plt.plot(price_df.index, price_df.iloc[:,0], label="Price")
    plt.plot(tech_indicators["SMA_5"].index, tech_indicators["SMA_5"].iloc[:,0], label="SMA 5")
    plt.plot(tech_indicators["SMA_10"].index, tech_indicators["SMA_10"].iloc[:,0], label="SMA 10")
    plt.plot(tech_indicators["SMA_20"].index, tech_indicators["SMA_20"].iloc[:,0], label="SMA 20")
    plt.legend()
    plt.title("Price with Moving Averages")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)

    results["price_ma_chart"] = base64.b64encode(buf.read()).decode()
    
    
    
    
        
    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)


    excel_tables = excel_for_template(price_df)


    results["excel_summary_table"] = excel_tables["summary_table"]
    results["excel_correlation_table"] = excel_tables["correlation_table"]
    results["excel_pivot_table"] = excel_tables["pivot_table"]

    
    
   
    price_data = generate_price_series(n_stocks, n_days=252)
    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates, columns=[f"Stock_{i}" for i in range(n_stocks)])

    
    ma_chart = plot_moving_averages(price_df)
    bollinger_chart = plot_bollinger_bands(price_df)

    
    results.update({
        "ma_chart": ma_chart,
        "bollinger_chart": bollinger_chart,
    })    
    
    
    
    
    
    
    
    
    
    
    
    return results


def run_analysis_cleanprevious2(**kwargs):
    n_stocks = kwargs.get("n_stocks", 10)
    corr_threshold = kwargs.get("corr_threshold", 0.6)

    
    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)

    
    expected_returns = np.random.uniform(0.01, 0.2, size=n_stocks)
    cov_matrix = np.random.uniform(0.001, 0.02, size=(n_stocks, n_stocks))
    cov_matrix = (cov_matrix + cov_matrix.T) / 2
    np.fill_diagonal(cov_matrix, np.random.uniform(0.005, 0.03, size=n_stocks))

    
    weights = optimize_portfolio(expected_returns, cov_matrix)

    
    price_data = generate_price_series(n_stocks, n_days=252)
    dates = pd.date_range("2023-01-01", periods=price_data.shape[0])
    price_df = pd.DataFrame(price_data, index=dates)

   
    bt = backtest_portfolio(weights, price_data)

   
    summary = excel_summary_stats(price_df)
    correlation = excel_correlation(price_df)
    pivot = excel_pivot_returns(price_df)

    
    return {
        "graph_url": graph_img,
        "weights": np.round(weights, 2).tolist(),
        "expected_return": round(float(np.dot(expected_returns, weights)), 4),
        "risk": round(float(np.sqrt(weights.T @ cov_matrix @ weights)), 4),

        "backtest_final_value": bt["final_value"],
        "backtest_sharpe": bt["sharpe"],
        "backtest_drawdown": bt["max_drawdown"],

        
        "excel_summary": summary.to_dict(),
        "excel_correlation": correlation.to_dict(),
        "excel_pivot": pivot.reset_index().to_dict(orient="records"),
    }






def run_analysis_cleanprevious(**kwargs):
    n_stocks = kwargs.get('n_stocks', 10)
    corr_threshold = kwargs.get('corr_threshold', 0.6)

    G, corr_matrix = create_stock_correlation_graph(n_stocks, corr_threshold)
    graph_img = plot_stock_graph(G)
    graphon = graph_to_graphon(corr_matrix)
    graphon_img = visualize_graphon(graphon)

   
    expected_returns = np.random.uniform(0.01, 0.2, size=n_stocks)
    random_cov = np.random.uniform(0.001, 0.02, size=(n_stocks, n_stocks))
    covariance_matrix = (random_cov + random_cov.T) / 2
    np.fill_diagonal(
        covariance_matrix,
        np.random.uniform(0.005, 0.03, size=n_stocks)
    )

  
    weights = optimize_portfolio(expected_returns, covariance_matrix)

    
    price_data = generate_price_series(n_stocks, n_days=252)
    bt = backtest_portfolio(weights, price_data)

    
    S0 = kwargs.get('S0', 100)
    T = kwargs.get('T', 1.0)
    sigma = kwargs.get('sigma', 0.2)
    r = kwargs.get('r', 0.05)
    I = kwargs.get('I', 1000)

    bs_prices = np.zeros((I, n_stocks))
    for i in range(I):
        bs_prices[i] = S0 * np.exp(
            (r - 0.5 * sigma**2) * T
            + sigma * np.sqrt(T) * np.random.randn(n_stocks)
        )

    bs_mean = float(np.mean(bs_prices))
    bs_std = float(np.std(bs_prices))

  
    lambda_jump = kwargs.get('lambda_jump', 0.3)
    mu_jump = kwargs.get('mu_jump', -0.3)
    delta_jump = kwargs.get('delta_jump', 0.1)

    jd_prices = np.zeros((I, n_stocks))
    for i in range(I):
        jumps = np.random.poisson(lambda_jump * T, n_stocks)
        jump_sizes = np.random.normal(mu_jump, delta_jump, n_stocks) * jumps
        jd_prices[i] = S0 * np.exp(
            (r - 0.5 * sigma**2) * T
            + sigma * np.sqrt(T) * np.random.randn(n_stocks)
            + jump_sizes
        )

    jd_mean = float(np.mean(jd_prices))
    jd_std = float(np.std(jd_prices))

    
    results = {
        'graph_url': graph_img,
        'graphon_url': graphon_img,
        'weights': np.round(weights, 2).tolist(),
        'expected_return': round(float(np.dot(expected_returns, weights)), 4),
        'risk': round(float(np.sqrt(
            np.dot(weights.T, np.dot(covariance_matrix, weights))
        )), 4),

        'bs_mean': bs_mean,
        'bs_std': bs_std,
        'jd_mean': jd_mean,
        'jd_std': jd_std,

        'backtest_equity_curve': bt["equity"],
        'backtest_final_value': bt["final_value"],
        'backtest_sharpe': bt["sharpe"],
        'backtest_drawdown': bt["max_drawdown"],
    }

    return results








def run_analysis_with_save(**kwargs):
   
    results = run_analysis_clean(**kwargs)
    
    
    SimulationRecord.objects.create(
        final_value=results['backtest_final_value'],
        sharpe_ratio=results['backtest_sharpe']
    )
    
    return results




def plot_simulation_history():
   
    records = SimulationRecord.objects.all().order_by('timestamp')
    if not records.exists():
        return None

    dates = [r.timestamp.strftime("%Y-%m-%d %H:%M") for r in records]
    values = [r.final_value for r in records]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker='o', linestyle='-', color='b')
    plt.fill_between(dates, values, alpha=0.1, color='b')
    
    plt.title("Historical Performance of All Simulations")
    plt.xlabel("Simulation Date")
    plt.ylabel("Final Portfolio Value")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()